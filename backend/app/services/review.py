"""Review service managing feedback submissions and ground rating recalculations."""

from datetime import date, datetime
from typing import Sequence, Tuple, Optional
import uuid


from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException, ConflictException
from app.core.logging import get_logger
from app.models.review import Review
from app.models.booking import BookingStatus
from app.repositories.review import ReviewRepository
from app.repositories.booking import BookingRepository
from app.repositories.ground import GroundRepository

logger = get_logger(__name__)


class ReviewService:
    """Service handling reviews and ground statistics recalculations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.review_repo = ReviewRepository(db)
        self.booking_repo = BookingRepository(db)
        self.ground_repo = GroundRepository(db)

    async def create_review(
        self, user_id: uuid.UUID, booking_id: uuid.UUID, rating: int, text: Optional[str] = None
    ) -> Review:
        """Submit feedback for a completed booking and update ground rating metrics."""
        # 1. Validate booking existence and ownership
        booking = await self.booking_repo.get_details(booking_id)
        if not booking:
            raise NotFoundException("Booking not found")
        if booking.user_id != user_id:
            raise BadRequestException("You can only review your own bookings")

        # 2. Check if booking is eligible for review
        # Must be CONFIRMED or COMPLETED and booking date must be in the past or today
        if booking.status == BookingStatus.CANCELLED:
            raise BadRequestException("Cannot review a cancelled booking")
        if booking.booking_date > date.today():
            raise BadRequestException("Cannot review a future booking before it takes place")

        # 3. Check for existing review (Unique constraint on booking_id)
        existing_review = await self.review_repo.get_by_booking_id(booking_id)
        if existing_review:
            raise ConflictException("You have already submitted a review for this booking")

        # 4. Create review
        review = Review(
            user_id=user_id,
            ground_id=booking.ground_id,
            booking_id=booking_id,
            rating=rating,
            text=text,
        )
        self.db.add(review)
        await self.db.flush()

        # 5. Recalculate Ground average rating and count
        await self.recalculate_ground_rating(booking.ground_id)

        logger.info("review_created", booking_id=booking_id, ground_id=booking.ground_id, rating=rating)
        return review

    async def get_reviews_for_ground(
        self, ground_id: uuid.UUID, *, skip: int = 0, limit: int = 10
    ) -> Tuple[Sequence[Review], int]:
        """Fetch paginated reviews for a ground."""
        # Ensure ground exists
        ground = await self.ground_repo.get(ground_id)
        if not ground or ground.deleted_at is not None:
            raise NotFoundException("Ground not found")

        return await self.review_repo.list_by_ground_id(ground_id, skip=skip, limit=limit)

    async def recalculate_ground_rating(self, ground_id: uuid.UUID) -> None:
        """Update a ground's rating and review count based on reviews."""
        avg_rating, total_reviews = await self.review_repo.get_rating_stats_by_ground_id(ground_id)
        
        # Round rating to 1 decimal place
        rounded_rating = round(avg_rating, 1)

        ground = await self.ground_repo.get(ground_id)
        if ground:
            ground.rating = rounded_rating
            ground.review_count = total_reviews
            self.db.add(ground)
            await self.db.flush()
            
            # Invalidate cached top rated grounds
            try:
                from app.database.redis import get_redis, RedisCache
                redis_client = await get_redis()
                cache = RedisCache(redis_client)
                await cache.delete_pattern("grounds:top:*")
            except Exception:
                pass
                
            logger.info("ground_rating_recalculated", ground_id=ground_id, rating=rounded_rating, count=total_reviews)

