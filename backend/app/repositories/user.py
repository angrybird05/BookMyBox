"""User and RefreshToken repository operations."""

from datetime import datetime, timezone
from typing import Optional
import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, RefreshToken, UserStatus
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository operations for User model."""

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> User | None:
        """Fetch user by email (case-insensitive and excludes soft-deleted)."""
        stmt = select(User).where(
            User.email == email.lower(),
            User.deleted_at.is_(None)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> User | None:
        """Fetch user by phone (excludes soft-deleted)."""
        stmt = select(User).where(
            User.phone == phone,
            User.deleted_at.is_(None)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email_or_phone(self, email: str, phone: str) -> User | None:
        """Fetch user by email or phone (excludes soft-deleted)."""
        stmt = select(User).where(
            ((User.email == email.lower()) | (User.phone == phone)) &
            (User.deleted_at.is_(None))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def soft_delete(self, user_id: uuid.UUID) -> bool:
        """Soft-delete user by setting deleted_at timestamp and updating status."""
        user = await self.get(user_id)
        if user and not user.is_deleted:
            user.deleted_at = datetime.now(timezone.utc)
            user.status = UserStatus.DELETED
            self.db.add(user)
            await self.db.flush()
            return True
        return False


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """Repository operations for RefreshToken model."""

    def __init__(self, db: AsyncSession):
        super().__init__(RefreshToken, db)

    async def get_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        """Retrieve refresh token by its hashed value."""
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked.is_(False)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke_token(self, token_hash: str) -> bool:
        """Revoke a refresh token by hashing it."""
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
            .values(is_revoked=True, updated_at=datetime.now(timezone.utc))
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount > 0

    async def revoke_all_user_tokens(self, user_id: uuid.UUID) -> int:
        """Revoke all active refresh tokens of a user (e.g. during security event or password change)."""
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.is_revoked.is_(False))
            .values(is_revoked=True, updated_at=datetime.now(timezone.utc))
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount
