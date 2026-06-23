"""Reviews API endpoints."""

from typing import Any
import uuid

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_user
from app.core.responses import success_response
from app.models.user import User
from app.models.review import Review
from app.schemas.review import ReviewResponse, ReviewCreateRequest
from app.services.review import ReviewService

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_review_endpoint(
    request: Request,
    payload: ReviewCreateRequest,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
) -> Any:
    """Create a new review for a completed booking, updating the ground average rating."""
    review_service = ReviewService(db)
    review = await review_service.create_review(
        user_id=current_user.id,
        booking_id=payload.booking_id,
        rating=payload.rating,
        text=payload.text,
    )
    
    # Eager load user relation for response validation
    stmt = select(Review).where(Review.id == review.id).options(selectinload(Review.user))
    res = await db.execute(stmt)
    full_review = res.scalar_one()
    
    review_data = ReviewResponse.model_validate(full_review).model_dump(mode="json")
    request_id = getattr(request.state, "request_id", None)
    
    return success_response(
        data=review_data,
        message="Review submitted successfully",
        request_id=request_id
    )


@router.get("/featured", status_code=status.HTTP_200_OK)
async def get_featured_reviews(
    request: Request,
    limit: int = Query(5, ge=1, le=20, description="Max reviews to return"),
    db=Depends(get_db)
) -> Any:
    """Retrieve featured/top-rated reviews for the landing page."""
    # Query high-rated reviews (rating >= 4) with their author user details
    stmt = (
        select(Review)
        .where(Review.rating >= 4)
        .order_by(Review.created_at.desc())
        .limit(limit)
        .options(selectinload(Review.user))
    )
    result = await db.execute(stmt)
    reviews = result.scalars().all()
    
    reviews_data = [ReviewResponse.model_validate(r).model_dump(mode="json") for r in reviews]
    request_id = getattr(request.state, "request_id", None)
    
    return success_response(data=reviews_data, request_id=request_id)
