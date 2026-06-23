"""FastAPI dependency injection utilities."""

from collections.abc import AsyncGenerator
from typing import Annotated
import uuid

from fastapi import Depends, Security
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.core.security import decode_access_token
from app.database.session import get_db_context
from app.models.user import User, UserRole, UserStatus
from app.repositories.user import UserRepository

settings = get_settings()

# Define OAuth2 scheme extraction dependency
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_PREFIX}/auth/login"
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency yielding database session context."""
    async with get_db_context() as session:
        yield session


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(reusable_oauth2)],
) -> User:
    """Retrieve and validate the current authenticated user from access token."""
    # 1. Decode token
    payload = decode_access_token(token)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Invalid access token format")
        
    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise UnauthorizedException("Invalid user identity in token")

    # 2. Retrieve user
    user_repo = UserRepository(db)
    user = await user_repo.get(user_id)
    if not user or user.status == UserStatus.DELETED:
        raise UnauthorizedException("User account not found")

    # 3. Check status
    if user.status == UserStatus.BLOCKED:
        raise ForbiddenException("User account is blocked")

    return user


async def get_current_admin(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Ensure that the current user has administrator role permissions."""
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenException("Administrator permission required")
    return current_user
