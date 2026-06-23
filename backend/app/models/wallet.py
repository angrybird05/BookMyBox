"""Wallet and WalletTransaction database models."""

import enum
from typing import List, Optional
import uuid

from sqlalchemy import ForeignKey, Integer, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin


class WalletTransactionType(str, enum.Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"


class Wallet(Base, UUIDMixin, TimestampMixin):
    """User wallet representing their current account balance."""

    __tablename__ = "wallets"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    balance: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="wallet")
    transactions: Mapped[List["WalletTransaction"]] = relationship(
        "WalletTransaction", back_populates="wallet", cascade="all, delete-orphan"
    )


class WalletTransaction(Base, UUIDMixin, TimestampMixin):
    """Ledger recording each credit/debit transaction inside the wallet."""

    __tablename__ = "wallet_transactions"

    wallet_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # Must be positive; type determines direction
    type: Mapped[WalletTransactionType] = mapped_column(
        Enum(WalletTransactionType, name="wallet_transaction_type", inherit_schema=True),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reference_id: Mapped[Optional[uuid.UUID]] = mapped_column(nullable=True, index=True)  # Can refer to booking_id or payment_id

    # Relationships
    wallet: Mapped[Wallet] = relationship("Wallet", back_populates="transactions")
