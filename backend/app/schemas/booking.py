"""Booking Pydantic schemas."""

from datetime import date, datetime
from typing import List, Optional
import uuid

from pydantic import BaseModel, Field, field_serializer

from app.models.booking import BookingStatus, BookingSlotStatus
from app.models.payment import PaymentMethod
from app.schemas.ground import GroundResponse
from app.schemas.slot import SlotResponse


class BookingSlotResponse(BaseModel):
    """Output details for an individual slot reserved within a booking."""

    id: uuid.UUID
    slot_id: uuid.UUID
    price: int
    status: BookingSlotStatus
    cancelled_at: Optional[datetime] = None
    slot: Optional[SlotResponse] = None

    class Config:
        from_attributes = True


class BookingResponse(BaseModel):
    """Output booking payload details returned by lookup/history APIs."""

    id: uuid.UUID
    ref: str
    user_id: uuid.UUID
    ground_id: uuid.UUID
    booking_date: date
    total_amount: int
    discount: int
    final_amount: int
    promo_code: Optional[str] = None
    status: BookingStatus
    created_at: datetime
    cancelled_at: Optional[datetime] = None
    ground: Optional[GroundResponse] = None
    booking_slots: List[BookingSlotResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True

    @field_serializer("booking_date")
    def serialize_booking_date(self, d: date) -> str:
        return d.isoformat()


class BookingCreateRequest(BaseModel):
    """Input payload to checkout and create a booking cart."""

    ground_id: uuid.UUID = Field(..., description="Target facility ground ID")
    booking_date: date = Field(..., description="Target date for slots")
    slot_ids: List[uuid.UUID] = Field(..., min_length=1, max_length=6, description="List of 1 to 6 slots in the cart")
    promo_code: Optional[str] = Field(None, description="Optional coupon code")
    payment_method: PaymentMethod = Field(..., description="Method: UPI, CARD, NET_BANKING, or WALLET")


class ValidatePromoRequest(BaseModel):
    """Input payload to dry-run validate a discount code."""

    code: str = Field(..., min_length=1)
    total_amount: int = Field(..., ge=0, description="Booking cart total price")


class ValidatePromoResponse(BaseModel):
    """Output details of promo code check."""

    valid: bool
    discount: int
    final_amount: int
    message: str


class CancelSlotsRequest(BaseModel):
    """Input payload to cancel specific slots (partial cancellation)."""

    slot_ids: List[uuid.UUID] = Field(..., min_length=1, description="List of slot IDs to cancel")
