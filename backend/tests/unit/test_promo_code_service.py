"""Unit tests for PromoCodeService business logic."""

from datetime import date, timedelta
from unittest.mock import AsyncMock
import pytest

from app.models.promo_code import PromoCode, PromoCodeType
from app.services.promo_code import PromoCodeService


@pytest.mark.asyncio
async def test_validate_promo_flat_discount():
    """Test valid flat promo code calculation."""
    promo = PromoCode(
        code="FLAT200",
        type=PromoCodeType.FLAT,
        value=200,
        min_amount=1000,
        valid_from=date.today() - timedelta(days=1),
        valid_to=date.today() + timedelta(days=1),
        is_active=True,
        usage_limit=10,
        used_count=0
    )
    
    db_mock = AsyncMock()
    service = PromoCodeService(db_mock)
    service.promo_repo.get_by_code = AsyncMock(return_value=promo)

    # 1. Valid case
    valid, discount, final_amount, msg = await service.validate_promo("FLAT200", 1200)
    assert valid is True
    assert discount == 200
    assert final_amount == 1000
    
    # 2. Min amount violation
    valid, discount, final_amount, msg = await service.validate_promo("FLAT200", 800)
    assert valid is False
    assert discount == 0
    assert final_amount == 800
    assert "Minimum order value" in msg
