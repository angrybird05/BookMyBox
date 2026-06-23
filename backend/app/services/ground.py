"""Ground service managing business operations around sport box cricket grounds."""

from typing import List, Optional, Tuple
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.ground import Ground
from app.repositories.ground import GroundRepository
from app.schemas.ground import GroundCreate, GroundUpdate


class GroundService:
    """Service handling catalog lookups and metrics for grounds."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.ground_repo = GroundRepository(db)

    async def get_ground(self, ground_id: uuid.UUID) -> Ground:
        """Fetch ground by ID, raising NotFoundException if missing."""
        ground = await self.ground_repo.get(ground_id)
        if not ground or ground.deleted_at is not None:
            raise NotFoundException("Ground not found")
        return ground

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
        page: int = 1,
        per_page: int = 10,
    ) -> Tuple[List[Ground], int]:
        """Fetch paginated list of active grounds based on filtering and sorting."""
        skip = (page - 1) * per_page
        grounds, total = await self.ground_repo.list_grounds(
            city=city,
            search_query=search_query,
            price_min=price_min,
            price_max=price_max,
            amenities=amenities,
            tag=tag,
            sort_by=sort_by,
            skip=skip,
            limit=per_page,
        )
        return list(grounds), total

    async def get_top_grounds(self, limit: int = 6) -> List[Ground]:
        """Fetch featured top-rated grounds with Redis cache fallback."""
        import json
        from app.database.redis import get_redis, RedisCache

        cache_key = f"grounds:top:{limit}"
        try:
            redis_client = await get_redis()
            cache = RedisCache(redis_client)
            cached_data = await cache.get(cache_key)
            if cached_data:
                data_list = json.loads(cached_data)
                # Reconstruct transient model objects for response mapping
                return [Ground(**item) for item in data_list]
        except Exception:
            # Fallback to database on cache lookup failure
            pass

        grounds = await self.ground_repo.get_top_rated(limit=limit)
        grounds_list = list(grounds)

        # Cache the results for 5 minutes
        try:
            serialized_list = []
            for g in grounds_list:
                serialized_list.append({
                    "id": str(g.id),
                    "name": g.name,
                    "location": g.location,
                    "city": g.city,
                    "description": g.description,
                    "price_per_hour": g.price_per_hour,
                    "rating": g.rating,
                    "review_count": g.review_count,
                    "amenities": g.amenities,
                    "total_slots": g.total_slots,
                    "open_time": g.open_time,
                    "close_time": g.close_time,
                    "slot_duration_minutes": g.slot_duration_minutes,
                    "tag": g.tag,
                    "gradient": g.gradient,
                    "icon": g.icon,
                    "is_active": g.is_active,
                })
            await cache.set(cache_key, json.dumps(serialized_list), ttl=300)
        except Exception:
            pass

        return grounds_list

