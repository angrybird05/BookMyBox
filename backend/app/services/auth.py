"""Authentication service handling registration, login, logout, and token rotation."""

from datetime import datetime, timedelta, timezone
import hashlib
import json
from typing import Any, Dict, Tuple
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import ConflictException, UnauthorizedException, ForbiddenException, BadRequestException
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_refresh_token
from app.models.user import User, RefreshToken, UserStatus, UserRole
from app.models.wallet import Wallet
from app.repositories.user import UserRepository, RefreshTokenRepository
from app.schemas.auth import LoginRequest, TokenResponse, OtpVerifyRequest
from app.schemas.user import UserCreate
from app.services.otp import OtpService
from app.services.notification import NotificationService
from app.database.redis import get_redis
from app.workers.tasks import send_otp_sms_task, send_welcome_email_task, send_password_reset_email_task

settings = get_settings()


class AuthService:
    """Service handling all authentication, authorization, and session registration flows."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_repo = RefreshTokenRepository(db)
        self.otp_service = OtpService()
        self.notification_service = NotificationService()

    async def register_pending(self, user_in: UserCreate) -> str:
        """Verify username uniqueness and cache pending registration data in Redis while dispatching OTP."""
        # 1. Check if user already exists
        existing_user = await self.user_repo.get_by_email_or_phone(user_in.email, user_in.phone)
        if existing_user:
            raise ConflictException("Email or phone number is already registered")

        # 2. Hash password and prepare user data
        hashed_pwd = hash_password(user_in.password)
        pending_data = {
            "name": user_in.name,
            "email": user_in.email.lower(),
            "phone": user_in.phone,
            "password_hash": hashed_pwd,
            "city": user_in.city,
        }

        # 3. Store registration data in Redis (valid for 10 minutes)
        redis_client = await get_redis()
        redis_key = f"pending_registration:{user_in.email.lower()}"
        await redis_client.set(redis_key, json.dumps(pending_data), ex=600)

        # 4. Generate and send OTP (deletes immediate block, sends via Celery task)
        otp = await self.otp_service.generate_otp(user_in.email)
        send_otp_sms_task.delay(user_in.phone, otp)

        return "OTP sent successfully to email/phone"

    async def verify_registration_otp(self, verify_in: OtpVerifyRequest) -> Tuple[User, TokenResponse]:
        """Validate registration OTP, instantiate user & wallet in DB, and issue tokens."""
        # 1. Verify OTP code
        otp_valid = await self.otp_service.verify_otp(verify_in.email, verify_in.otp_code)
        if not otp_valid:
            raise BadRequestException("Invalid or expired verification code")

        # 2. Retrieve pending registration details from Redis
        redis_client = await get_redis()
        redis_key = f"pending_registration:{verify_in.email.lower()}"
        cached_data_str = await redis_client.get(redis_key)
        
        if not cached_data_str:
            raise BadRequestException("Registration session expired. Please register again.")

        pending_data = json.loads(cached_data_str)

        # Double check email/phone again just in case a concurrent request registered them
        existing_user = await self.user_repo.get_by_email_or_phone(pending_data["email"], pending_data["phone"])
        if existing_user:
            raise ConflictException("Email or phone number is already registered")

        # 3. Create User in Database
        user = User(
            name=pending_data["name"],
            email=pending_data["email"],
            phone=pending_data["phone"],
            password_hash=pending_data["password_hash"],
            city=pending_data["city"],
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
        )
        self.db.add(user)
        await self.db.flush()

        # 4. Create Wallet for User
        wallet = Wallet(user_id=user.id, balance=0)
        self.db.add(wallet)
        await self.db.flush()

        # 5. Clear registration cache
        await redis_client.delete(redis_key)

        # 6. Issue Tokens
        tokens = await self._generate_session_tokens(user)
        
        # Trigger welcome email notification via Celery background task
        send_welcome_email_task.delay(user.email, user.name)

        return user, tokens

    async def login(self, login_in: LoginRequest) -> Tuple[User, TokenResponse]:
        """Verify user credentials and return active tokens."""
        # Fetch user
        user = await self.user_repo.get_by_email(login_in.email)
        if not user:
            raise UnauthorizedException("Invalid email or password")

        # Verify password
        if not verify_password(login_in.password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")

        # Check status
        if user.status == UserStatus.BLOCKED:
            raise ForbiddenException("Your account is blocked. Please contact support.")
        if user.status == UserStatus.DELETED:
            raise ForbiddenException("Your account has been deleted.")

        # Generate tokens
        tokens = await self._generate_session_tokens(user)
        return user, tokens

    async def rotate_tokens(self, refresh_token: str) -> TokenResponse:
        """Validate refresh token and issue new rotated tokens (token rotation security)."""
        # Decode and validate refresh token format
        payload = decode_refresh_token(refresh_token)
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise UnauthorizedException("Invalid refresh token payload")

        user_id = uuid.UUID(user_id_str)
        token_hash = self._hash_token(refresh_token)

        # Look up token in database to prevent reuse/revocation bypass
        stored_token = await self.token_repo.get_by_token_hash(token_hash)
        if not stored_token or stored_token.is_expired or stored_token.is_revoked:
            # Security event: if token is valid signature but not in DB, it might be a reuse attack.
            # Revoke all tokens for this user for security.
            await self.token_repo.revoke_all_user_tokens(user_id)
            raise UnauthorizedException("Invalid or expired refresh token session")

        # Fetch user
        user = await self.user_repo.get(user_id)
        if not user or user.status != UserStatus.ACTIVE:
            raise UnauthorizedException("User account is inactive or blocked")

        # Revoke old refresh token (mark as used/revoked)
        stored_token.is_revoked = True
        self.db.add(stored_token)
        await self.db.flush()

        # Generate new pair of tokens
        new_tokens = await self._generate_session_tokens(user)
        return new_tokens

    async def logout(self, refresh_token: str) -> None:
        """Revoke refresh token and terminate active session."""
        try:
            payload = decode_refresh_token(refresh_token)
            token_hash = self._hash_token(refresh_token)
            await self.token_repo.revoke_token(token_hash)
        except UnauthorizedException:
            # Suppress token validation error during logout
            pass

    async def forgot_password(self, email: str) -> None:
        """Generate reset password token and send email."""
        user = await self.user_repo.get_by_email(email)
        if not user:
            # Security best practice: don't disclose whether email exists or not
            return

        # Generate reset token cached in Redis for 30 minutes
        reset_token = str(uuid.uuid4())
        redis_client = await get_redis()
        redis_key = f"password_reset:{reset_token}"
        await redis_client.set(redis_key, str(user.id), ex=1800)

        # Dispatch email via Celery background task
        send_password_reset_email_task.delay(user.email, reset_token)

    async def reset_password(self, token: str, new_password: str) -> None:
        """Reset user password using reset token."""
        redis_client = await get_redis()
        redis_key = f"password_reset:{token}"
        user_id_str = await redis_client.get(redis_key)

        if not user_id_str:
            raise BadRequestException("Invalid or expired password reset link")

        user_id = uuid.UUID(user_id_str)
        user = await self.user_repo.get(user_id)
        if not user or user.status != UserStatus.ACTIVE:
            raise BadRequestException("User account is inactive or no longer exists")

        # Hash and update password
        user.password_hash = hash_password(new_password)
        self.db.add(user)

        # Revoke all current refresh sessions for safety
        await self.token_repo.revoke_all_user_tokens(user_id)
        
        # Delete reset token from Redis
        await redis_client.delete(redis_key)

    async def _generate_session_tokens(self, user: User) -> TokenResponse:
        """Helper to create access and refresh tokens, and store refresh token hash in DB."""
        extra_claims = {"role": user.role.value, "name": user.name}
        
        access_token = create_access_token(subject=str(user.id), extra_claims=extra_claims)
        refresh_token = create_refresh_token(subject=str(user.id))

        # Hash the refresh token before storing it
        token_hash = self._hash_token(refresh_token)
        expiry_days = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        expires_at = datetime.now(timezone.utc) + timedelta(days=expiry_days)

        db_refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.db.add(db_refresh_token)
        await self.db.flush()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    def _hash_token(self, token: str) -> str:
        """SHA-256 helper to store token hashes securely in the DB."""
        return hashlib.sha256(token.encode()).hexdigest()
