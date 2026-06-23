"""PromoCode repository operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.promo_code import PromoCode
from app.repositories.base import BaseRepository


class PromoCodeRepository(BaseRepository[PromoCode]):
    """Repository operations for PromoCode model."""

    def __init__(self, db: AsyncSession):
        super().__init__(PromoCode, db)

    async def get_by_code(self, code: str) -> PromoCode | None:
        """Retrieve promo code by exact string matches (case-insensitive)."""
        stmt = select(PromoCode).where(
            PromoCode.code == code.upper().strip(),
            PromoCode.is_active.is_(True)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
