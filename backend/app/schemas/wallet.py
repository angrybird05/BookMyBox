"""Wallet Pydantic schemas."""

from datetime import datetime
from typing import List, Optional
import uuid

from pydantic import BaseModel, Field

from app.models.wallet import WalletTransactionType


class WalletTransactionResponse(BaseModel):
    """Output details for a wallet transaction."""

    id: uuid.UUID
    wallet_id: uuid.UUID
    amount: int = Field(..., description="Transaction amount in rupees")
    type: WalletTransactionType
    description: Optional[str] = None
    reference_id: Optional[uuid.UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


class WalletResponse(BaseModel):
    """Output wallet details."""

    id: uuid.UUID
    user_id: uuid.UUID
    balance: int = Field(..., description="Current balance in rupees")

    class Config:
        from_attributes = True


class WalletTopUpRequest(BaseModel):
    """Input payload to top up the wallet balance."""

    amount: int = Field(..., ge=1, description="Amount to add in rupees")
