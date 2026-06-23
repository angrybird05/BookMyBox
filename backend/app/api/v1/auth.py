"""Authentication API endpoints."""

from typing import Any
from fastapi import APIRouter, Depends, Request, status

from app.api.deps import get_db, get_current_user
from app.core.responses import success_response
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, OtpVerifyRequest, RefreshTokenRequest, ForgotPasswordRequest, ResetPasswordRequest
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_200_OK)
async def register(
    request: Request,
    user_in: UserCreate,
    db=Depends(get_db)
) -> Any:
    """Register a new user profile and dispatch a verification OTP to phone/email."""
    auth_service = AuthService(db)
    message = await auth_service.register_pending(user_in)
    
    request_id = getattr(request.state, "request_id", None)
    return success_response(message=message, request_id=request_id)


@router.post("/verify-otp", status_code=status.HTTP_200_OK)
async def verify_otp(
    request: Request,
    verify_in: OtpVerifyRequest,
    db=Depends(get_db)
) -> Any:
    """Verify registration OTP, complete user creation, and issue session tokens."""
    auth_service = AuthService(db)
    user, tokens = await auth_service.verify_registration_otp(verify_in)
    
    user_data = UserResponse.from_orm(user).model_dump(mode="json")
    data = {
        "user": user_data,
        "tokens": tokens.model_dump(mode="json")
    }
    
    request_id = getattr(request.state, "request_id", None)
    return success_response(
        data=data,
        message="Registration verified and completed successfully",
        request_id=request_id
    )


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    request: Request,
    login_in: LoginRequest,
    db=Depends(get_db)
) -> Any:
    """Login with credentials to obtain an access and refresh token."""
    auth_service = AuthService(db)
    user, tokens = await auth_service.login(login_in)
    
    user_data = UserResponse.from_orm(user).model_dump(mode="json")
    data = {
        "user": user_data,
        "tokens": tokens.model_dump(mode="json")
    }
    
    request_id = getattr(request.state, "request_id", None)
    return success_response(
        data=data,
        message="Login successful",
        request_id=request_id
    )


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_token(
    request: Request,
    refresh_in: RefreshTokenRequest,
    db=Depends(get_db)
) -> Any:
    """Renew expired access tokens by verifying and rotating refresh token."""
    auth_service = AuthService(db)
    tokens = await auth_service.rotate_tokens(refresh_in.refresh_token)
    
    request_id = getattr(request.state, "request_id", None)
    return success_response(
        data=tokens.model_dump(mode="json"),
        message="Token refreshed successfully",
        request_id=request_id
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    request: Request,
    refresh_in: RefreshTokenRequest,
    db=Depends(get_db)
) -> Any:
    """Revoke active refresh token to end session."""
    auth_service = AuthService(db)
    await auth_service.logout(refresh_in.refresh_token)
    
    request_id = getattr(request.state, "request_id", None)
    return success_response(message="Logged out successfully", request_id=request_id)


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    request: Request,
    forgot_in: ForgotPasswordRequest,
    db=Depends(get_db)
) -> Any:
    """Request a password reset link email."""
    auth_service = AuthService(db)
    await auth_service.forgot_password(forgot_in.email)
    
    request_id = getattr(request.state, "request_id", None)
    return success_response(
        message="If the email is registered, password reset instructions have been sent.",
        request_id=request_id
    )


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    request: Request,
    reset_in: ResetPasswordRequest,
    db=Depends(get_db)
) -> Any:
    """Change user password using verification token."""
    auth_service = AuthService(db)
    await auth_service.reset_password(reset_in.token, reset_in.new_password)
    
    request_id = getattr(request.state, "request_id", None)
    return success_response(message="Password reset successfully", request_id=request_id)
