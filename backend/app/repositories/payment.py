"""Payment repository operations."""

from collections.abc import Sequence
from typing import Optional
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment
from app.repositories.base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    """Repository operations for Payment model."""

    def __init__(self, db: AsyncSession):
        super().__init__(Payment, db)

    async def get_by_transaction_ref(self, transaction_ref: str) -> Payment | None:
        """Fetch payment by unique transaction reference."""
        stmt = select(Payment).where(Payment.transaction_ref == transaction_ref)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_booking_id(self, booking_id: uuid.UUID) -> Sequence[Payment]:
        """Fetch all payments related to a booking."""
        stmt = select(Payment).where(Payment.booking_id == booking_id).order_by(Payment.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()
