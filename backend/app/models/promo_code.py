"""PromoCode database model."""

import enum
from datetime import date
from typing import Optional

from sqlalchemy import String, Integer, Boolean, Date, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin, UUIDMixin


class PromoCodeType(str, enum.Enum):
    PERCENTAGE = "PERCENTAGE"
    FLAT = "FLAT"


class PromoCode(Base, UUIDMixin, TimestampMixin):
    """PromoCode model representing discount codes that can be applied to bookings."""

    __tablename__ = "promo_codes"

    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    type: Mapped[PromoCodeType] = mapped_column(
        Enum(PromoCodeType, name="promo_code_type", inherit_schema=True),
        nullable=False,
    )
    value: Mapped[int] = mapped_column(Integer, nullable=False)  # flat discount amount or percentage
    min_amount: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_discount: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # cap limit for percentage type
    usage_limit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # max times this promo can be used globally
    used_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    @property
    def is_expired(self) -> bool:
        return date.today() > self.valid_to

    @property
    def is_valid_now(self) -> bool:
        today = date.today()
        return (
            self.is_active
            and self.valid_from <= today <= self.valid_to
            and (self.usage_limit is None or self.used_count < self.usage_limit)
        )
