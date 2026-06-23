"""Payments API endpoints."""

from typing import Any
import uuid

from fastapi import APIRouter, Depends, Request, status

from app.api.deps import get_db, get_current_user
from app.core.responses import success_response
from app.core.exceptions import NotFoundException, BadRequestException
from app.models.user import User
from app.schemas.payment import PaymentResponse, PaymentInitiateRequest, PaymentConfirmRequest
from app.services.payment import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/initiate", status_code=status.HTTP_200_OK)
async def initiate_payment_endpoint(
    request: Request,
    payload: PaymentInitiateRequest,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
) -> Any:
    """Initiate a payment transaction for an existing booking (External simulated payment gateway)."""
    payment_service = PaymentService(db)
    payment = await payment_service.initiate_payment(
        user_id=current_user.id,
        booking_id=payload.booking_id,
        method=payload.method,
    )
    
    payment_data = PaymentResponse.model_validate(payment).model_dump(mode="json")
    request_id = getattr(request.state, "request_id", None)
    
    return success_response(
        data=payment_data,
        message="Payment initiated successfully",
        request_id=request_id
    )


@router.post("/confirm", status_code=status.HTTP_200_OK)
async def confirm_payment_endpoint(
    request: Request,
    payload: PaymentConfirmRequest,
    db=Depends(get_db)
) -> Any:
    """Confirm a pending payment transaction (simulates webhook or provider response)."""
    payment_service = PaymentService(db)
    payment = await payment_service.confirm_payment(
        transaction_ref=payload.transaction_ref,
        status=payload.status,
        gateway_response=payload.gateway_response
    )
    
    payment_data = PaymentResponse.model_validate(payment).model_dump(mode="json")
    request_id = getattr(request.state, "request_id", None)
    
    return success_response(
        data=payment_data,
        message=f"Payment status updated to {payload.status.value}",
        request_id=request_id
    )


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_payment_status(
    request: Request,
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
) -> Any:
    """Retrieve details and status of a payment."""
    payment_service = PaymentService(db)
    payment = await payment_service.payment_repo.get(id)
    if not payment:
        raise NotFoundException("Payment record not found")
        
    if payment.user_id != current_user.id and current_user.role != "admin":
        raise BadRequestException("Access denied to this payment record")
        
    payment_data = PaymentResponse.model_validate(payment).model_dump(mode="json")
    request_id = getattr(request.state, "request_id", None)
    
    return success_response(data=payment_data, request_id=request_id)
