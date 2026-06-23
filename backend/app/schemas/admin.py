"""Admin-specific Pydantic schemas."""

from datetime import date
from typing import List, Optional
import uuid

from pydantic import BaseModel, Field


class AdminStatsResponse(BaseModel):
    """System-wide summary metrics for admin dashboard."""

    revenue: int = Field(..., description="Total system revenue from paid bookings (in rupees)")
    bookings_count: int = Field(..., description="Total number of bookings across the system")
    users_count: int = Field(..., description="Total registered customers")
    grounds_count: int = Field(..., description="Total active facilities")


class RevenueChartItem(BaseModel):
    """Daily revenue entry for charting."""

    date: date
    amount: int


class BlockSlotsRequest(BaseModel):
    """Request payload to block specific slots for booking."""

    slot_ids: List[uuid.UUID] = Field(..., min_length=1)


class UnblockSlotsRequest(BaseModel):
    """Request payload to unblock specific slots."""

    slot_ids: List[uuid.UUID] = Field(..., min_length=1)


class BulkUpdatePriceRequest(BaseModel):
    """Request payload to change pricing for a list of slots."""

    slot_ids: List[uuid.UUID] = Field(..., min_length=1)
    price: int = Field(..., ge=0)
