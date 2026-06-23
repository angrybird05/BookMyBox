"""User Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, Optional
import uuid

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserRole, UserStatus


class UserBase(BaseModel):
    """Base fields shared across user schemas."""

    name: str = Field(..., min_length=2, max_length=100, description="User's full name")
    email: EmailStr = Field(..., description="Unique email address")
    phone: str = Field(..., min_length=10, max_length=15, description="Mobile number")
    city: Optional[str] = Field(None, max_length=100, description="Current city of residence")


class UserCreate(UserBase):
    """Input parameters for registering a new user."""

    password: str = Field(..., min_length=6, max_length=100, description="Plaintext password")


class UserUpdate(BaseModel):
    """Input parameters for updating a user profile."""

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    city: Optional[str] = Field(None, max_length=100)


class UserUpdatePassword(BaseModel):
    """Input parameters for changing account password."""

    old_password: str = Field(..., description="Current plaintext password")
    new_password: str = Field(..., min_length=6, max_length=100, description="New plaintext password")


class UserUpdateNotifications(BaseModel):
    """Input parameters for updating notification settings."""

    email: bool = Field(default=True)
    sms: bool = Field(default=True)
    push: bool = Field(default=True)


class UserResponse(UserBase):
    """Output user profile payload returned by APIs."""

    id: uuid.UUID
    role: UserRole
    status: UserStatus
    avatar_url: Optional[str] = None
    notification_prefs: Dict[str, bool]
    created_at: datetime

    class Config:
        from_attributes = True


class UserDashboardStats(BaseModel):
    """User summary statistics displayed in the client dashboard."""

    bookings_count: int = Field(0, description="Total number of ground bookings")
    total_spent: int = Field(0, description="Total amount spent on bookings (in rupees)")
    wallet_balance: int = Field(0, description="Available wallet balance (in rupees)")
