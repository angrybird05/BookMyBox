"""Unit tests for WalletService business logic."""

from unittest.mock import AsyncMock, MagicMock
import uuid
import pytest

from app.core.exceptions import BadRequestException, NotFoundException
from app.models.user import User
from app.models.wallet import Wallet, WalletTransactionType
from app.services.wallet import WalletService


@pytest.mark.asyncio
async def test_top_up_wallet_success(mock_db):
    """Test successful wallet balance addition and ledger transaction."""
    user_id = uuid.uuid4()
    user = User(id=user_id, name="Customer Name")
    wallet = Wallet(id=uuid.uuid4(), user_id=user_id, balance=100)

    service = WalletService(mock_db)
    service.user_repo.get = AsyncMock(return_value=user)
    service.wallet_repo.get_or_create_by_user_id = AsyncMock(return_value=wallet)

    updated_wallet = await service.top_up_wallet(
        user_id=user_id,
        amount=500,
        description="Topup desc"
    )

    assert updated_wallet.balance == 600
    assert mock_db.add.call_count == 2  # Wallet instance and WalletTransaction instance


@pytest.mark.asyncio
async def test_top_up_wallet_negative_amount(mock_db):
    """Test wallet top-up rejects negative or zero values."""
    user_id = uuid.uuid4()
    service = WalletService(mock_db)

    with pytest.raises(BadRequestException):
        await service.top_up_wallet(user_id=user_id, amount=-100)

    with pytest.raises(BadRequestException):
        await service.top_up_wallet(user_id=user_id, amount=0)


@pytest.mark.asyncio
async def test_get_wallet_not_found(mock_db):
    """Test exception raised when loading wallet for non-existent user."""
    user_id = uuid.uuid4()
    service = WalletService(mock_db)
    service.user_repo.get = AsyncMock(return_value=None)

    with pytest.raises(NotFoundException):
        await service.get_wallet(user_id)
