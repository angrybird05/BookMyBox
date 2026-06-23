"""Ground repository operations."""

from collections.abc import Sequence
from typing import List, Optional, Tuple
import uuid

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ground import Ground
from app.repositories.base import BaseRepository


class GroundRepository(BaseRepository[Ground]):
    """Repository operations for Ground model."""

    def __init__(self, db: AsyncSession):
        super().__init__(Ground, db)

    async def list_grounds(
        self,
        *,
        city: Optional[str] = None,
        search_query: Optional[str] = None,
        price_min: Optional[int] = None,
        price_max: Optional[int] = None,
        amenities: Optional[List[str]] = None,
        tag: Optional[str] = None,
        sort_by: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[Sequence[Ground], int]:
        """Query grounds with dynamic filtering, search, sorting, and pagination."""
        # Base query for active, non-deleted grounds
        stmt = select(Ground).where(
            Ground.is_active.is_(True),
            Ground.deleted_at.is_(None)
        )

        # Apply city filter (case-insensitive)
        if city:
            stmt = stmt.where(func.lower(Ground.city) == city.lower().strip())

        # Apply search query (matches name or location)
        if search_query:
            stmt = stmt.where(
                Ground.name.ilike(f"%{search_query}%") |
                Ground.location.ilike(f"%{search_query}%")
            )

        # Apply price ranges
        if price_min is not None:
            stmt = stmt.where(Ground.price_per_hour >= price_min)
        if price_max is not None:
            stmt = stmt.where(Ground.price_per_hour <= price_max)

        # Apply tags filter
        if tag:
            stmt = stmt.where(Ground.tag == tag)

        # Apply amenities filter (Postgres ARRAY contains query)
        if amenities:
            stmt = stmt.where(Ground.amenities.contains(amenities))

        # First, query total count matching these filters (before offset/limit)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_res = await self.db.execute(count_stmt)
        total_count = count_res.scalar_one() or 0

        # Apply sorting
        if sort_by == "price_asc":
            stmt = stmt.order_by(Ground.price_per_hour.asc())
        elif sort_by == "price_desc":
            stmt = stmt.order_by(Ground.price_per_hour.desc())
        elif sort_by == "rating_desc":
            stmt = stmt.order_by(Ground.rating.desc(), Ground.review_count.desc())
        else:
            # Default sorting: active tags/featured, then rating, then name
            stmt = stmt.order_by(Ground.rating.desc(), Ground.name.asc())

        # Apply pagination
        stmt = stmt.offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        grounds = result.scalars().all()

        return grounds, total_count

    async def get_top_rated(self, *, limit: int = 6) -> Sequence[Ground]:
        """Retrieve highest-rated grounds (used for landing/home page)."""
        stmt = (
            select(Ground)
            .where(Ground.is_active.is_(True), Ground.deleted_at.is_(None))
            .order_by(Ground.rating.desc(), Ground.review_count.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
