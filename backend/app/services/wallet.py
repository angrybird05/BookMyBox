"""Wallet service managing balances, top-ups, and transactions."""

from typing import Optional, Sequence, Tuple
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.core.logging import get_logger
from app.models.wallet import Wallet, WalletTransaction, WalletTransactionType
from app.repositories.wallet import WalletRepository, WalletTransactionRepository
from app.repositories.user import UserRepository

logger = get_logger(__name__)


class WalletService:
    """Service handling wallet operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.wallet_repo = WalletRepository(db)
        self.tx_repo = WalletTransactionRepository(db)
        self.user_repo = UserRepository(db)

    async def get_wallet(self, user_id: uuid.UUID) -> Wallet:
        """Fetch or create a user's wallet."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException("User not found")
        return await self.wallet_repo.get_or_create_by_user_id(user_id)

    async def top_up_wallet(
        self, user_id: uuid.UUID, amount: int, description: Optional[str] = None
    ) -> Wallet:
        """Add balance to user's wallet and log the transaction."""
        if amount <= 0:
            raise BadRequestException("Top-up amount must be greater than zero")

        wallet = await self.get_wallet(user_id)
        wallet.balance += amount
        self.db.add(wallet)

        # Create wallet transaction
        tx = WalletTransaction(
            wallet_id=wallet.id,
            amount=amount,
            type=WalletTransactionType.CREDIT,
            description=description or "Wallet top-up",
        )
        self.db.add(tx)
        await self.db.flush()

        logger.info("wallet_topped_up", user_id=user_id, amount=amount, new_balance=wallet.balance)
        return wallet

    async def list_transactions(
        self, user_id: uuid.UUID, *, skip: int = 0, limit: int = 10
    ) -> Tuple[Sequence[WalletTransaction], int]:
        """Retrieve paginated wallet transactions for a user."""
        wallet = await self.get_wallet(user_id)
        return await self.tx_repo.list_transactions_by_wallet_id(wallet.id, skip=skip, limit=limit)
