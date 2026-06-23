"""Ground database model."""

from typing import List, Optional
from sqlalchemy import String, Integer, Float, Boolean, JSON
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin, SoftDeleteMixin


class Ground(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """Ground model representing a box cricket ground/facility."""

    __tablename__ = "grounds"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(512), nullable=False)
    city: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    price_per_hour: Mapped[int] = mapped_column(Integer, nullable=False)
    rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    review_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Storing as standard Postgres Array of strings
    amenities: Mapped[List[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    
    total_slots: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    open_time: Mapped[str] = mapped_column(String(5), default="06:00", nullable=False)  # HH:MM format
    close_time: Mapped[str] = mapped_column(String(5), default="23:00", nullable=False) # HH:MM format
    slot_duration_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    
    tag: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # POPULAR, PREMIUM, NEW
    gradient: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # For UI card gradients
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # For UI icons
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    slots: Mapped[List["Slot"]] = relationship(
        "Slot", back_populates="ground", cascade="all, delete-orphan"
    )
    bookings: Mapped[List["Booking"]] = relationship(
        "Booking", back_populates="ground"
    )
    reviews: Mapped[List["Review"]] = relationship(
        "Review", back_populates="ground", cascade="all, delete-orphan"
    )
