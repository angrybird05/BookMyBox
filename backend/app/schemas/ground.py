"""Ground Pydantic schemas."""

from datetime import datetime
from typing import List, Optional
import uuid

from pydantic import BaseModel, Field


class GroundBase(BaseModel):
    """Base ground properties."""

    name: str = Field(..., max_length=255)
    location: str = Field(..., max_length=512)
    city: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    price_per_hour: int = Field(..., ge=0)
    amenities: List[str] = Field(default_factory=list)
    open_time: str = Field(default="06:00", pattern=r"^\d{2}:\d{2}$")  # HH:MM format
    close_time: str = Field(default="23:00", pattern=r"^\d{2}:\d{2}$") # HH:MM format
    slot_duration_minutes: int = Field(default=60, ge=30, le=240)
    tag: Optional[str] = Field(None, max_length=50)       # POPULAR, PREMIUM, NEW
    gradient: Optional[str] = Field(None, max_length=100) # Card gradient CSS class
    icon: Optional[str] = Field(None, max_length=50)       # Emoji/Lucide icon name


class GroundCreate(GroundBase):
    """Input payload to create a ground (admin only)."""

    pass


class GroundUpdate(BaseModel):
    """Input payload to update a ground (admin only)."""

    name: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=512)
    city: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    price_per_hour: Optional[int] = Field(None, ge=0)
    amenities: Optional[List[str]] = None
    open_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    close_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    slot_duration_minutes: Optional[int] = Field(None, ge=30, le=240)
    tag: Optional[str] = Field(None, max_length=50)
    gradient: Optional[str] = Field(None, max_length=100)
    icon: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class GroundResponse(GroundBase):
    """Output ground payload returned by list/detail APIs."""

    id: uuid.UUID
    rating: float
    review_count: int
    total_slots: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        
        # Customize serialization to output clean time strings
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
