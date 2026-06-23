"""Slot Pydantic schemas."""

from datetime import date, time
from typing import Optional
import uuid

from pydantic import BaseModel, Field, field_serializer

from app.models.slot import SlotStatus


class SlotBase(BaseModel):
    """Base fields shared across slot schemas."""

    date: date
    start_time: time
    end_time: time
    price: int = Field(..., ge=0)
    status: SlotStatus = Field(default=SlotStatus.AVAILABLE)
    duration_minutes: int = Field(default=60, ge=30)


class SlotCreate(SlotBase):
    """Input payload to create a slot manually (admin only)."""

    ground_id: uuid.UUID


class SlotResponse(SlotBase):
    """Output slot payload returned by search/list APIs."""

    id: uuid.UUID
    ground_id: uuid.UUID

    class Config:
        from_attributes = True

    # Custom serializers to output times as clean "HH:MM" strings
    @field_serializer("start_time")
    def serialize_start_time(self, start_time: time) -> str:
        return start_time.strftime("%H:%M")

    @field_serializer("end_time")
    def serialize_end_time(self, end_time: time) -> str:
        return end_time.strftime("%H:%M")
        
    @field_serializer("date")
    def serialize_date(self, d: date) -> str:
        return d.isoformat()
