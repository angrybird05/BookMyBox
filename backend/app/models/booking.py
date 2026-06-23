"""Booking and BookingSlot database models."""

import enum
from datetime import date, datetime
from typing import List, Optional
import uuid

from sqlalchemy import ForeignKey, Date, DateTime, Integer, String, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin


class BookingStatus(str, enum.Enum):
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    PARTIALLY_CANCELLED = "PARTIALLY_CANCELLED"


class BookingSlotStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


class Booking(Base, UUIDMixin, TimestampMixin):
    """Booking representing a customer reservation of one or more slots."""

    __tablename__ = "bookings"

    ref: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    ground_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("grounds.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    booking_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    total_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    discount: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    final_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    promo_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus, name="booking_status", inherit_schema=True),
        default=BookingStatus.CONFIRMED,
        nullable=False,
        index=True,
    )
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="bookings")
    ground: Mapped["Ground"] = relationship("Ground", back_populates="bookings")
    booking_slots: Mapped[List["BookingSlot"]] = relationship(
        "BookingSlot", back_populates="booking", cascade="all, delete-orphan"
    )
    payments: Mapped[List["Payment"]] = relationship(
        "Payment", back_populates="booking", cascade="all, delete-orphan"
    )
    review: Mapped[Optional["Review"]] = relationship(
        "Review", back_populates="booking", uselist=False, cascade="all, delete-orphan"
    )


class BookingSlot(Base, UUIDMixin, TimestampMixin):
    """Junction table connecting Bookings to Slots, tracking individual slot statuses."""

    __tablename__ = "booking_slots"

    booking_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    slot_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("slots.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[BookingSlotStatus] = mapped_column(
        Enum(BookingSlotStatus, name="booking_slot_status", inherit_schema=True),
        default=BookingSlotStatus.ACTIVE,
        nullable=False,
    )
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relational constraints: a slot cannot be booked multiple times in the same active booking
    __table_args__ = (
        UniqueConstraint("booking_id", "slot_id", name="uq_booking_slot"),
    )

    # Relationships
    booking: Mapped[Booking] = relationship("Booking", back_populates="booking_slots")
    slot: Mapped["Slot"] = relationship("Slot", back_populates="booking_slots")
