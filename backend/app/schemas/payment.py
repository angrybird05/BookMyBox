"""Payment Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, Optional
import uuid

from pydantic import BaseModel, Field

from app.models.payment import PaymentMethod, PaymentStatus


class PaymentResponse(BaseModel):
    """Output details for a payment transaction."""

    id: uuid.UUID
    booking_id: uuid.UUID
    user_id: uuid.UUID
    amount: int
    method: PaymentMethod
    status: PaymentStatus
    transaction_ref: Optional[str] = None
    gateway_response: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentInitiateRequest(BaseModel):
    """Request payload to initiate a booking payment."""

    booking_id: uuid.UUID = Field(..., description="Target booking ID")
    method: PaymentMethod = Field(..., description="Payment method: UPI, CARD, NET_BANKING, or WALLET")


class PaymentConfirmRequest(BaseModel):
    """Simulation input payload to confirm standard external gateway payment."""

    transaction_ref: str = Field(..., description="Unique transaction ID from simulated gateway")
    status: PaymentStatus = Field(..., description="Outcome of payment process (SUCCESS or FAILED)")
    gateway_response: Optional[Dict[str, Any]] = Field(None, description="Detailed simulated response")
