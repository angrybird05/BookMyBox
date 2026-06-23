"""Wallet API endpoints."""

from typing import Any
import uuid

from fastapi import APIRouter, Depends, Query, Request, status

from app.api.deps import get_db, get_current_user
from app.core.responses import success_response, paginated_response
from app.models.user import User
from app.schemas.wallet import WalletResponse, WalletTransactionResponse, WalletTopUpRequest
from app.services.wallet import WalletService

router = APIRouter(prefix="/wallet", tags=["Wallet"])


@router.get("", status_code=status.HTTP_200_OK)
async def get_wallet_balance(
    request: Request,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
) -> Any:
    """Retrieve current wallet balance for the authenticated user."""
    wallet_service = WalletService(db)
    wallet = await wallet_service.get_wallet(current_user.id)
    
    wallet_data = WalletResponse.model_validate(wallet).model_dump(mode="json")
    request_id = getattr(request.state, "request_id", None)
    
    return success_response(data=wallet_data, request_id=request_id)


@router.post("/topup", status_code=status.HTTP_200_OK)
async def topup_wallet(
    request: Request,
    payload: WalletTopUpRequest,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
) -> Any:
    """Add money to user's wallet (simulates gateway recharge)."""
    wallet_service = WalletService(db)
    wallet = await wallet_service.top_up_wallet(
        user_id=current_user.id,
        amount=payload.amount,
        description="Wallet top-up (Simulated)"
    )
    
    wallet_data = WalletResponse.model_validate(wallet).model_dump(mode="json")
    request_id = getattr(request.state, "request_id", None)
    
    return success_response(
        data=wallet_data,
        message=f"Wallet successfully topped up by ₹{payload.amount}",
        request_id=request_id
    )


@router.get("/transactions", status_code=status.HTTP_200_OK)
async def get_wallet_transactions(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
) -> Any:
    """Retrieve user's wallet transaction ledger history (paginated)."""
    wallet_service = WalletService(db)
    skip = (page - 1) * per_page
    transactions, total = await wallet_service.list_transactions(
        user_id=current_user.id,
        skip=skip,
        limit=per_page
    )
    
    tx_data = [WalletTransactionResponse.model_validate(tx).model_dump(mode="json") for tx in transactions]
    request_id = getattr(request.state, "request_id", None)
    
    return paginated_response(
        data=tx_data,
        total=total,
        page=page,
        per_page=per_page,
        message="Wallet transaction history retrieved successfully",
        request_id=request_id
    )
