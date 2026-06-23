"""Review Pydantic schemas."""

from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel, Field


class ReviewUserResponse(BaseModel):
    """Minimal user profile information included in reviews."""

    id: uuid.UUID
    name: str
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


class ReviewResponse(BaseModel):
    """Output review details."""

    id: uuid.UUID
    user_id: uuid.UUID
    ground_id: uuid.UUID
    booking_id: uuid.UUID
    rating: int = Field(..., ge=1, le=5)
    text: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    user: Optional[ReviewUserResponse] = None

    class Config:
        from_attributes = True


class ReviewCreateRequest(BaseModel):
    """Input payload to write a review for a completed booking."""

    booking_id: uuid.UUID = Field(..., description="Completed booking ID to review")
    rating: int = Field(..., ge=1, le=5, description="Rating stars between 1 and 5")
    text: Optional[str] = Field(None, max_length=1000, description="Optional text feedback")
