"""Slot service managing availability checks and on-demand slot generation."""

from datetime import date, datetime, time, timedelta
from typing import List, Sequence
import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.models.ground import Ground
from app.models.slot import Slot, SlotStatus
from app.repositories.ground import GroundRepository
from app.repositories.slot import SlotRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


class SlotService:
    """Service handling slot availability, on-demand auto-generation, and administrative locks."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.slot_repo = SlotRepository(db)
        self.ground_repo = GroundRepository(db)

    async def get_slots_for_date(self, ground_id: uuid.UUID, target_date: date) -> Sequence[Slot]:
        """Fetch slots for a ground on a date. If empty and date is today/future, auto-generate them."""
        # 1. Query existing slots from DB
        slots = await self.slot_repo.get_by_ground_and_date(ground_id, target_date)
        if slots:
            return slots

        # 2. Check if date is in the past
        if target_date < date.today():
            return []  # Do not generate slots for past dates

        # 3. Generate slots on-demand
        logger.info("generating_slots_on_demand", ground_id=ground_id, date=target_date)
        try:
            return await self.generate_slots_for_date(ground_id, target_date)
        except IntegrityError:
            # Handle race condition: if slots were created concurrently by another request
            self.db.rollback()
            logger.info("slots_concurrency_race_detected_reloading", ground_id=ground_id, date=target_date)
            return await self.slot_repo.get_by_ground_and_date(ground_id, target_date)

    async def generate_slots_for_date(self, ground_id: uuid.UUID, target_date: date) -> List[Slot]:
        """Auto-generate slots based on ground operating hours and slot duration."""
        # Fetch ground details
        ground = await self.ground_repo.get(ground_id)
        if not ground or not ground.is_active or ground.deleted_at is not None:
            raise NotFoundException("Active ground not found")

        # Parse start and close times (expected format "HH:MM")
        try:
            open_time_parsed = datetime.strptime(ground.open_time, "%H:%M").time()
            close_time_parsed = datetime.strptime(ground.close_time, "%H:%M").time()
        except ValueError as exc:
            logger.error("invalid_ground_operating_hours", ground_id=ground_id, error=str(exc))
            raise BadRequestException("Ground operating hours are incorrectly formatted")

        # Calculate time intervals
        start_dt = datetime.combine(target_date, open_time_parsed)
        end_dt = datetime.combine(target_date, close_time_parsed)
        duration = timedelta(minutes=ground.slot_duration_minutes)

        generated_slots: List[Slot] = []
        current_dt = start_dt
        
        while current_dt + duration <= end_dt:
            slot_start = current_dt.time()
            slot_end = (current_dt + duration).time()
            
            # Compute price proportional to ground hourly rate
            slot_price = int(ground.price_per_hour * (ground.slot_duration_minutes / 60.0))

            slot = Slot(
                ground_id=ground_id,
                date=target_date,
                start_time=slot_start,
                end_time=slot_end,
                price=slot_price,
                status=SlotStatus.AVAILABLE,
                duration_minutes=ground.slot_duration_minutes,
            )
            generated_slots.append(slot)
            current_dt += duration

        if not generated_slots:
            return []

        # Bulk save generated slots to database
        saved_slots = await self.slot_repo.create_bulk(generated_slots)
        
        # Update ground total slot counts dynamically
        ground.total_slots = len(saved_slots)
        self.db.add(ground)
        await self.db.flush()

        logger.info("slots_auto_generated", ground_id=ground_id, count=len(saved_slots), date=target_date)
        return saved_slots

    async def block_slots(self, slot_ids: List[uuid.UUID]) -> None:
        """Mark slots as BLOCKED (admin control)."""
        affected = []
        for slot_id in slot_ids:
            slot = await self.slot_repo.get(slot_id)
            if not slot:
                raise NotFoundException(f"Slot {slot_id} not found")
            if slot.status == SlotStatus.BOOKED:
                raise BadRequestException(f"Cannot block slot {slot_id} as it is already booked")
            slot.status = SlotStatus.BLOCKED
            self.db.add(slot)
            affected.append((slot.ground_id, slot.date))
        await self.db.flush()
        logger.info("slots_blocked_by_admin", count=len(slot_ids))
        
        # Broadcast real-time slot state changes to websocket listeners
        from app.core.websocket import broadcast_slot_updates
        for gid, d in set(affected):
            await broadcast_slot_updates(self.db, gid, d)

    async def unblock_slots(self, slot_ids: List[uuid.UUID]) -> None:
        """Release admin block on slots (mark as AVAILABLE)."""
        affected = []
        for slot_id in slot_ids:
            slot = await self.slot_repo.get(slot_id)
            if not slot:
                raise NotFoundException(f"Slot {slot_id} not found")
            if slot.status == SlotStatus.BLOCKED:
                slot.status = SlotStatus.AVAILABLE
                self.db.add(slot)
                affected.append((slot.ground_id, slot.date))
        await self.db.flush()
        logger.info("slots_unblocked_by_admin", count=len(slot_ids))
        
        # Broadcast real-time slot state changes to websocket listeners
        from app.core.websocket import broadcast_slot_updates
        for gid, d in set(affected):
            await broadcast_slot_updates(self.db, gid, d)

    async def update_slot_prices(self, slot_ids: List[uuid.UUID], price: int) -> None:
        """Bulk update pricing for slots (admin control)."""
        affected = []
        for slot_id in slot_ids:
            slot = await self.slot_repo.get(slot_id)
            if not slot:
                raise NotFoundException(f"Slot {slot_id} not found")
            if slot.status == SlotStatus.BOOKED:
                raise BadRequestException(f"Cannot update price of slot {slot_id} as it is already booked")
            slot.price = price
            self.db.add(slot)
            affected.append((slot.ground_id, slot.date))
        await self.db.flush()
        logger.info("slot_prices_updated_by_admin", count=len(slot_ids), new_price=price)
        
        # Broadcast real-time slot state changes to websocket listeners
        from app.core.websocket import broadcast_slot_updates
        for gid, d in set(affected):
            await broadcast_slot_updates(self.db, gid, d)


