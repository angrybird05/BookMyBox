"""Unit tests for ReviewService business logic."""

from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock
import uuid
import pytest

from app.core.exceptions import BadRequestException, ConflictException
from app.models.booking import Booking, BookingStatus
from app.models.review import Review
from app.models.ground import Ground
from app.services.review import ReviewService


@pytest.mark.asyncio
async def test_create_review_success(mock_db):
    """Test successful review creation and rating metrics recalculation."""
    user_id = uuid.uuid4()
    booking_id = uuid.uuid4()
    ground_id = uuid.uuid4()
    
    # Completed past booking
    booking = Booking(
        id=booking_id,
        user_id=user_id,
        ground_id=ground_id,
        booking_date=date.today() - timedelta(days=1),
        status=BookingStatus.CONFIRMED
    )
    ground = Ground(id=ground_id, rating=0.0, review_count=0)

    service = ReviewService(mock_db)
    service.booking_repo.get_details = AsyncMock(return_value=booking)
    service.review_repo.get_by_booking_id = AsyncMock(return_value=None)
    service.review_repo.get_rating_stats_by_ground_id = AsyncMock(return_value=(4.5, 1))
    service.ground_repo.get = AsyncMock(return_value=ground)

    review = await service.create_review(
        user_id=user_id,
        booking_id=booking_id,
        rating=5,
        text="Loved playing here!"
    )

    assert review.user_id == user_id
    assert review.rating == 5
    assert ground.rating == 4.5
    assert ground.review_count == 1
    assert mock_db.add.call_count == 2  # Review added, Ground updated


@pytest.mark.asyncio
async def test_create_review_future_booking(mock_db):
    """Test review creation rejected for a future booking."""
    user_id = uuid.uuid4()
    booking_id = uuid.uuid4()
    ground_id = uuid.uuid4()
    
    # Future booking
    booking = Booking(
        id=booking_id,
        user_id=user_id,
        ground_id=ground_id,
        booking_date=date.today() + timedelta(days=2),
        status=BookingStatus.CONFIRMED
    )

    service = ReviewService(mock_db)
    service.booking_repo.get_details = AsyncMock(return_value=booking)

    with pytest.raises(BadRequestException) as exc:
        await service.create_review(user_id, booking_id, 5, "Nice")
        
    assert "Cannot review a future booking" in str(exc.value)


@pytest.mark.asyncio
async def test_create_review_already_reviewed(mock_db):
    """Test review creation rejected if a review already exists for the booking."""
    user_id = uuid.uuid4()
    booking_id = uuid.uuid4()
    ground_id = uuid.uuid4()
    
    booking = Booking(
        id=booking_id,
        user_id=user_id,
        ground_id=ground_id,
        booking_date=date.today() - timedelta(days=1),
        status=BookingStatus.CONFIRMED
    )
    existing_review = Review(id=uuid.uuid4())

    service = ReviewService(mock_db)
    service.booking_repo.get_details = AsyncMock(return_value=booking)
    service.review_repo.get_by_booking_id = AsyncMock(return_value=existing_review)

    with pytest.raises(ConflictException):
        await service.create_review(user_id, booking_id, 4, "Another comment")
