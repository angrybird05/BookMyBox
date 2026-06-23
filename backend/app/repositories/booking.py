"""Booking repository operations."""

from collections.abc import Sequence
from typing import List, Optional, Tuple
import uuid

from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking, BookingStatus, BookingSlot
from app.repositories.base import BaseRepository


class BookingRepository(BaseRepository[Booking]):
    """Repository operations for Booking model."""

    def __init__(self, db: AsyncSession):
        super().__init__(Booking, db)

    async def get_by_ref(self, ref: str) -> Booking | None:
        """Fetch a booking by its unique reference string."""
        stmt = (
            select(Booking)
            .where(Booking.ref == ref.upper())
            .options(
                selectinload(Booking.booking_slots).selectinload(BookingSlot.slot),
                selectinload(Booking.ground),
                selectinload(Booking.payments)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_details(self, booking_id: uuid.UUID) -> Booking | None:
        """Fetch booking by ID, preloading slots, grounds, and payments."""
        stmt = (
            select(Booking)
            .where(Booking.id == booking_id)
            .options(
                selectinload(Booking.booking_slots).selectinload(BookingSlot.slot),
                selectinload(Booking.ground),
                selectinload(Booking.payments),
                selectinload(Booking.review)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_user_bookings(
        self,
        user_id: uuid.UUID,
        *,
        tab: Optional[str] = None,  # UPCOMING, PAST, CANCELLED
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[Sequence[Booking], int]:
        """Fetch paginated bookings matching tab filters for a specific user."""
        stmt = select(Booking).where(Booking.user_id == user_id)
        now_dt = func.now()

        # Apply tab status grouping logic
        if tab == "UPCOMING":
            stmt = stmt.where(
                Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PARTIALLY_CANCELLED]),
                Booking.booking_date >= func.current_date()
            ).order_by(Booking.booking_date.asc(), Booking.created_at.asc())
            
        elif tab == "PAST":
            # Completed bookings or past date confirmed bookings
            stmt = stmt.where(
                (Booking.status == BookingStatus.COMPLETED) |
                (
                    Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PARTIALLY_CANCELLED]) & 
                    (Booking.booking_date < func.current_date())
                )
            ).order_by(Booking.booking_date.desc(), Booking.created_at.desc())
            
        elif tab == "CANCELLED":
            stmt = stmt.where(Booking.status == BookingStatus.CANCELLED).order_by(Booking.cancelled_at.desc())
        else:
            # All bookings
            stmt = stmt.order_by(Booking.created_at.desc())

        # Count query
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_res = await self.db.execute(count_stmt)
        total_count = count_res.scalar_one() or 0

        # Paginate and fetch, eager loading relations for card listing
        stmt = stmt.offset(skip).limit(limit).options(
            selectinload(Booking.booking_slots).selectinload(BookingSlot.slot),
            selectinload(Booking.ground)
        )
        result = await self.db.execute(stmt)
        bookings = result.scalars().all()

        return bookings, total_count

    async def list_all_bookings_admin(
        self,
        *,
        search: Optional[str] = None,
        status_filter: Optional[BookingStatus] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[Sequence[Booking], int]:
        """List all bookings globally for admin search panels."""
        stmt = select(Booking)

        if status_filter:
            stmt = stmt.where(Booking.status == status_filter)

        if search:
            stmt = stmt.where(Booking.ref.ilike(f"%{search}%"))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_res = await self.db.execute(count_stmt)
        total_count = count_res.scalar_one() or 0

        stmt = stmt.order_by(Booking.created_at.desc()).offset(skip).limit(limit).options(
            selectinload(Booking.booking_slots).selectinload(BookingSlot.slot),
            selectinload(Booking.ground),
            selectinload(Booking.user)
        )
        result = await self.db.execute(stmt)
        bookings = result.scalars().all()

        return bookings, total_count
