"""Review repository operations."""

from collections.abc import Sequence
from typing import Optional, Tuple
import uuid

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review
from app.repositories.base import BaseRepository


class ReviewRepository(BaseRepository[Review]):
    """Repository operations for Review model."""

    def __init__(self, db: AsyncSession):
        super().__init__(Review, db)

    async def get_by_booking_id(self, booking_id: uuid.UUID) -> Review | None:
        """Fetch review by booking ID (one review per booking)."""
        stmt = select(Review).where(Review.booking_id == booking_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_and_booking(self, user_id: uuid.UUID, booking_id: uuid.UUID) -> Review | None:
        """Fetch review by user ID and booking ID."""
        stmt = select(Review).where(Review.user_id == user_id, Review.booking_id == booking_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_ground_id(
        self,
        ground_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[Sequence[Review], int]:
        """Fetch paginated reviews for a specific ground, ordered by creation date desc."""
        stmt = (
            select(Review)
            .where(Review.ground_id == ground_id)
            .order_by(Review.created_at.desc())
        )

        # Count query
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_res = await self.db.execute(count_stmt)
        total_count = count_res.scalar_one() or 0

        # Paginate and fetch, eager loading the user who wrote it
        stmt = stmt.offset(skip).limit(limit).options(
            selectinload(Review.user)
        )
        result = await self.db.execute(stmt)
        reviews = result.scalars().all()

        return reviews, total_count

    async def get_rating_stats_by_ground_id(self, ground_id: uuid.UUID) -> Tuple[float, int]:
        """Get the average rating and total count of reviews for a ground."""
        stmt = (
            select(
                func.coalesce(func.avg(Review.rating), 0.0),
                func.count(Review.id)
            )
            .where(Review.ground_id == ground_id)
        )
        result = await self.db.execute(stmt)
        row = result.fetchone()
        if row:
            return float(row[0]), int(row[1])
        return 0.0, 0
