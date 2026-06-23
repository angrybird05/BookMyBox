"""PromoCode service for dry-run discount validation."""

from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.promo_code import PromoCodeType
from app.repositories.promo_code import PromoCodeRepository


class PromoCodeService:
    """Service handling promo code validations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.promo_repo = PromoCodeRepository(db)

    async def validate_promo(self, code: str, total_amount: int) -> Tuple[bool, int, int, str]:
        """Validate a promo code against a cart total.
        
        Returns:
            (valid, discount, final_amount, message)
        """
        promo = await self.promo_repo.get_by_code(code)
        if not promo:
            return False, 0, total_amount, "Invalid or expired promo code"

        if not promo.is_valid_now:
            return False, 0, total_amount, "Promo code is inactive or expired"

        if total_amount < promo.min_amount:
            return False, 0, total_amount, f"Minimum order value for this promo is ₹{promo.min_amount}"

        # Calculate discount
        discount = 0
        if promo.type == PromoCodeType.PERCENTAGE:
            discount = int(total_amount * (promo.value / 100.0))
            if promo.max_discount is not None:
                discount = min(discount, promo.max_discount)
        elif promo.type == PromoCodeType.FLAT:
            discount = promo.value

        # Cap discount at total amount
        discount = min(discount, total_amount)
        final_amount = total_amount - discount

        return True, discount, final_amount, "Promo code applied successfully"
