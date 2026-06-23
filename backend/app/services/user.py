"""User service handling profile updates, dashboard stats, and deletion."""

from typing import Any, Dict, Optional
import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.booking import Booking, BookingStatus
from app.models.user import User, UserStatus
from app.models.wallet import Wallet
from app.repositories.user import UserRepository
from app.schemas.user import UserUpdate, UserDashboardStats, UserUpdateNotifications

from app.core.logging import get_logger

logger = get_logger(__name__)


class UserService:
    """Service handling profile management and user-related aggregation metrics."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def get_profile(self, user_id: uuid.UUID) -> User:
        """Fetch user by ID, raising NotFoundException if missing or deleted."""
        user = await self.user_repo.get(user_id)
        if not user or user.status == UserStatus.DELETED:
            raise NotFoundException("User not found")
        return user

    async def update_profile(self, user_id: uuid.UUID, profile_in: UserUpdate) -> User:
        """Update core profile attributes."""
        user = await self.get_profile(user_id)
        
        # Build update dictionary
        update_data = profile_in.model_dump(exclude_unset=True)
        if not update_data:
            return user

        # Perform the update
        updated_user = await self.user_repo.update(user, obj_in=update_data)
        logger.info("user_profile_updated", user_id=user_id, updated_fields=list(update_data.keys()))
        return updated_user

    async def update_notifications(self, user_id: uuid.UUID, prefs_in: UserUpdateNotifications) -> User:
        """Update notification preferences JSON field."""
        user = await self.get_profile(user_id)
        user.notification_prefs = prefs_in.model_dump()
        self.db.add(user)
        await self.db.flush()
        logger.info("user_notification_prefs_updated", user_id=user_id)
        return user

    async def update_avatar(self, user_id: uuid.UUID, avatar_url: str) -> User:
        """Update user avatar URL."""
        user = await self.get_profile(user_id)
        user.avatar_url = avatar_url
        self.db.add(user)
        await self.db.flush()
        logger.info("user_avatar_updated", user_id=user_id, avatar_url=avatar_url)
        return user

    async def delete_account(self, user_id: uuid.UUID) -> None:
        """Soft delete a user account."""
        success = await self.user_repo.soft_delete(user_id)
        if not success:
            raise NotFoundException("User not found")
        logger.info("user_account_deleted", user_id=user_id)

    async def get_dashboard_stats(self, user_id: uuid.UUID) -> UserDashboardStats:
        """Compute user dashboard metrics (booking count, total spent, wallet balance)."""
        # 1. Fetch wallet balance
        wallet_stmt = select(Wallet.balance).where(Wallet.user_id == user_id)
        wallet_res = await self.db.execute(wallet_stmt)
        wallet_balance = wallet_res.scalar_one_or_none() or 0

        # 2. Count active bookings (excludes CANCELLED)
        bookings_count_stmt = select(func.count(Booking.id)).where(
            Booking.user_id == user_id,
            Booking.status != BookingStatus.CANCELLED
        )
        count_res = await self.db.execute(bookings_count_stmt)
        bookings_count = count_res.scalar_one() or 0

        # 3. Sum final amounts of bookings (only CONFIRMED or COMPLETED)
        total_spent_stmt = select(func.sum(Booking.final_amount)).where(
            Booking.user_id == user_id,
            (Booking.status == BookingStatus.CONFIRMED) | (Booking.status == BookingStatus.COMPLETED)
        )
        spent_res = await self.db.execute(total_spent_stmt)
        total_spent = spent_res.scalar_one() or 0

        return UserDashboardStats(
            bookings_count=bookings_count,
            total_spent=total_spent,
            wallet_balance=wallet_balance,
        )
