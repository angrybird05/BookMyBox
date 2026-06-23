"""Slot database model."""

import enum
from datetime import date, time
from typing import List
import uuid

from sqlalchemy import ForeignKey, Date, Time, Integer, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin


class SlotStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    BOOKED = "BOOKED"
    BLOCKED = "BLOCKED"


class Slot(Base, UUIDMixin, TimestampMixin):
    """Slot representing a specific bookable time block at a ground."""

    __tablename__ = "slots"

    ground_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("grounds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[SlotStatus] = mapped_column(
        Enum(SlotStatus, name="slot_status", inherit_schema=True),
        default=SlotStatus.AVAILABLE,
        nullable=False,
        index=True,
    )
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)

    # Unique constraint: a ground cannot have duplicate slots for the exact same date and time
    __table_args__ = (
        UniqueConstraint("ground_id", "date", "start_time", name="uq_ground_slot_time"),
    )

    # Relationships
    ground: Mapped["Ground"] = relationship("Ground", back_populates="slots")
    booking_slots: Mapped[List["BookingSlot"]] = relationship(
        "BookingSlot", back_populates="slot"
    )
