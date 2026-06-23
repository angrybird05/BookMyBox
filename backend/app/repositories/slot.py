"""Slot repository operations."""

from collections.abc import Sequence
from datetime import date
from typing import List, Optional
import uuid

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.slot import Slot, SlotStatus
from app.repositories.base import BaseRepository


class SlotRepository(BaseRepository[Slot]):
    """Repository operations for Slot model."""

    def __init__(self, db: AsyncSession):
        super().__init__(Slot, db)

    async def get_by_ground_and_date(self, ground_id: uuid.UUID, slot_date: date) -> Sequence[Slot]:
        """Fetch all slots for a specific ground on a given date (ordered by start time)."""
        stmt = (
            select(Slot)
            .where(
                Slot.ground_id == ground_id,
                Slot.date == slot_date
            )
            .order_by(Slot.start_time.asc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_with_lock(self, slot_id: uuid.UUID) -> Slot | None:
        """Fetch a slot by ID with SELECT FOR UPDATE row-level lock (prevents reservation race conditions)."""
        stmt = (
            select(Slot)
            .where(Slot.id == slot_id)
            .with_for_update()
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_bulk(self, slots: List[Slot]) -> List[Slot]:
        """Bulk insert list of Slot models."""
        self.db.add_all(slots)
        await self.db.flush()
        return slots

    async def get_active_slots_by_ids(self, slot_ids: List[uuid.UUID]) -> Sequence[Slot]:
        """Fetch multiple slots by their ID list."""
        stmt = select(Slot).where(Slot.id.in_(slot_ids))
        result = await self.db.execute(stmt)
        return result.scalars().all()
