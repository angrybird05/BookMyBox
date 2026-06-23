"""User API endpoints."""

from typing import Any
from fastapi import APIRouter, Depends, Request, status

from app.api.deps import get_db, get_current_user
from app.core.responses import success_response
from app.models.user import User
from app.schemas.user import UserUpdate, UserResponse, UserUpdatePassword, UserUpdateNotifications
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_me(
    request: Request,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Retrieve the current logged-in user profile details."""
    user_data = UserResponse.model_validate(current_user).model_dump(mode="json")
    
    request_id = getattr(request.state, "request_id", None)
    return success_response(data=user_data, request_id=request_id)


@router.put("/me", status_code=status.HTTP_200_OK)
async def update_me(
    request: Request,
    profile_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
) -> Any:
    """Update profile fields (name, phone, city) for the current user."""
    user_service = UserService(db)
    updated_user = await user_service.update_profile(current_user.id, profile_in)
    user_data = UserResponse.model_validate(updated_user).model_dump(mode="json")
    
    request_id = getattr(request.state, "request_id", None)
    return success_response(
        data=user_data,
        message="Profile updated successfully",
        request_id=request_id
    )


@router.put("/me/notifications", status_code=status.HTTP_200_OK)
async def update_my_notifications(
    request: Request,
    prefs_in: UserUpdateNotifications,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
) -> Any:
    """Update communication notification preferences."""
    user_service = UserService(db)
    updated_user = await user_service.update_notifications(current_user.id, prefs_in)
    user_data = UserResponse.model_validate(updated_user).model_dump(mode="json")
    
    request_id = getattr(request.state, "request_id", None)
    return success_response(
        data=user_data,
        message="Notification preferences updated successfully",
        request_id=request_id
    )


@router.put("/me/password", status_code=status.HTTP_200_OK)
async def update_my_password(
    request: Request,
    password_in: UserUpdatePassword,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
) -> Any:
    """Change the account password (requires verifying current password)."""
    # Verify current password
    from app.core.security import verify_password, hash_password
    from app.core.exceptions import UnauthorizedException
    
    if not verify_password(password_in.old_password, current_user.password_hash):
        raise UnauthorizedException("Invalid current password")

    # Hash and save new password
    current_user.password_hash = hash_password(password_in.new_password)
    db.add(current_user)
    
    # Revoke all sessions for security rotation
    from app.repositories.user import RefreshTokenRepository
    token_repo = RefreshTokenRepository(db)
    await token_repo.revoke_all_user_tokens(current_user.id)
    
    await db.flush()
    
    request_id = getattr(request.state, "request_id", None)
    return success_response(message="Password changed successfully", request_id=request_id)


@router.delete("/me", status_code=status.HTTP_200_OK)
async def delete_me(
    request: Request,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
) -> Any:
    """Soft-delete account and terminate session."""
    user_service = UserService(db)
    await user_service.delete_account(current_user.id)
    
    # Revoke all tokens
    from app.repositories.user import RefreshTokenRepository
    token_repo = RefreshTokenRepository(db)
    await token_repo.revoke_all_user_tokens(current_user.id)
    
    request_id = getattr(request.state, "request_id", None)
    return success_response(message="Account deleted successfully", request_id=request_id)


@router.get("/me/stats", status_code=status.HTTP_200_OK)
async def get_me_stats(
    request: Request,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
) -> Any:
    """Retrieve user dashboard summary statistics (bookings, spent, wallet)."""
    user_service = UserService(db)
    stats = await user_service.get_dashboard_stats(current_user.id)
    
    request_id = getattr(request.state, "request_id", None)
    return success_response(data=stats.model_dump(mode="json"), request_id=request_id)
