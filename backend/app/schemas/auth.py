"""Authentication Pydantic schemas."""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Input payload for logging in via email/password."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's plaintext password")


class TokenResponse(BaseModel):
    """Payload containing session tokens returned upon successful auth."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token for session renewals")
    token_type: str = Field(default="Bearer", description="Token authentication type")


class RefreshTokenRequest(BaseModel):
    """Input payload containing refresh token for session rotation."""

    refresh_token: str = Field(..., description="Existing JWT refresh token")


class OtpVerifyRequest(BaseModel):
    """Input payload for validating OTP during registration/login."""

    email: EmailStr = Field(..., description="User's registered email")
    otp_code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")


class ForgotPasswordRequest(BaseModel):
    """Input payload to trigger a password reset flow."""

    email: EmailStr = Field(..., description="User's registered email")


class ResetPasswordRequest(BaseModel):
    """Input payload for setting a new password using a reset token."""

    token: str = Field(..., description="Reset verification token sent to email")
    new_password: str = Field(..., min_length=6, max_length=100, description="New plaintext password")


class GoogleLoginRequest(BaseModel):
    """Input payload for Google Sign-In verification."""

    id_token: str = Field(..., description="OAuth id_token received from Google client auth")
