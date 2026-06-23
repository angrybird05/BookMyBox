"""Review database model."""

from typing import Optional
import uuid

from sqlalchemy import ForeignKey, Integer, String, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin


class Review(Base, UUIDMixin, TimestampMixin):
    """Review model capturing a user's rating and comment for a specific booking and ground."""

    __tablename__ = "reviews"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ground_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("grounds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    booking_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Rating range validation constraint (1 to 5)
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="chk_review_rating_range"),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="reviews")
    ground: Mapped["Ground"] = relationship("Ground", back_populates="reviews")
    booking: Mapped["Booking"] = relationship("Booking", back_populates="review")
