"""Wallet and WalletTransaction repository operations."""

from collections.abc import Sequence
from typing import Optional, Tuple
import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wallet import Wallet, WalletTransaction
from app.repositories.base import BaseRepository


class WalletRepository(BaseRepository[Wallet]):
    """Repository operations for Wallet model."""

    def __init__(self, db: AsyncSession):
        super().__init__(Wallet, db)

    async def get_by_user_id(self, user_id: uuid.UUID) -> Wallet | None:
        """Fetch user wallet by user ID."""
        stmt = select(Wallet).where(Wallet.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create_by_user_id(self, user_id: uuid.UUID) -> Wallet:
        """Get the user's wallet. If it does not exist, create it."""
        wallet = await self.get_by_user_id(user_id)
        if not wallet:
            wallet = Wallet(user_id=user_id, balance=0)
            self.db.add(wallet)
            await self.db.flush()
        return wallet


class WalletTransactionRepository(BaseRepository[WalletTransaction]):
    """Repository operations for WalletTransaction model."""

    def __init__(self, db: AsyncSession):
        super().__init__(WalletTransaction, db)

    async def list_transactions_by_wallet_id(
        self,
        wallet_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[Sequence[WalletTransaction], int]:
        """Fetch paginated transactions for a specific wallet, ordered by creation date desc."""
        stmt = (
            select(WalletTransaction)
            .where(WalletTransaction.wallet_id == wallet_id)
            .order_by(WalletTransaction.created_at.desc())
        )

        # Count query
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_res = await self.db.execute(count_stmt)
        total_count = count_res.scalar_one() or 0

        # Paginate and fetch
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        transactions = result.scalars().all()

        return transactions, total_count
