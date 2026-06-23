"""Payment database model."""

import enum
from typing import Any, Dict, Optional
import uuid

from sqlalchemy import ForeignKey, Integer, String, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin


class PaymentMethod(str, enum.Enum):
    UPI = "UPI"
    CARD = "CARD"
    NET_BANKING = "NET_BANKING"
    WALLET = "WALLET"


class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class Payment(Base, UUIDMixin, TimestampMixin):
    """Payment record tracking transactions and gateway responses."""

    __tablename__ = "payments"

    booking_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("bookings.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod, name="payment_method", inherit_schema=True),
        nullable=False,
    )
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status", inherit_schema=True),
        default=PaymentStatus.PENDING,
        nullable=False,
        index=True,
    )
    transaction_ref: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    gateway_response: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Relationships
    booking: Mapped["Booking"] = relationship("Booking", back_populates="payments")
    user: Mapped["User"] = relationship("User")
