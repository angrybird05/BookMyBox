"""OTP service for generating, sending, and verifying 6-digit verification codes."""

import random
import string
from app.core.config import get_settings
from app.core.logging import get_logger
from app.database.redis import get_redis

settings = get_settings()
logger = get_logger(__name__)


class OtpService:
    """Service to handle generation, storage, and validation of OTPs in Redis."""

    def __init__(self):
        self.settings = get_settings()

    async def generate_otp(self, identifier: str) -> str:
        """Generate a random 6-digit OTP and store it in Redis with an expiration."""
        # Check if we should generate a mock code or a real random code
        if self.settings.is_development and self.settings.OTP_MOCK_CODE:
            otp = self.settings.OTP_MOCK_CODE
        else:
            otp = "".join(random.choices(string.digits, k=self.settings.OTP_LENGTH))

        redis_client = await get_redis()
        redis_key = f"otp:{identifier.lower()}"
        
        # Store OTP in Redis with expiry
        await redis_client.set(redis_key, otp, ex=self.settings.OTP_EXPIRY_SECONDS)
        
        logger.info("otp_generated", identifier=identifier, expiry=self.settings.OTP_EXPIRY_SECONDS)
        return otp

    async def verify_otp(self, identifier: str, code: str) -> bool:
        """Verify if the provided OTP code matches what's in Redis (or standard mock in dev)."""
        # Always allow mock code in development environment for testing convenience
        if self.settings.is_development and code == self.settings.OTP_MOCK_CODE:
            logger.info("otp_verified_via_mock", identifier=identifier)
            return True

        redis_client = await get_redis()
        redis_key = f"otp:{identifier.lower()}"
        stored_otp = await redis_client.get(redis_key)

        if not stored_otp:
            logger.warning("otp_verification_failed_expired_or_not_found", identifier=identifier)
            return False

        is_valid = stored_otp == code
        if is_valid:
            # Delete OTP key upon successful verification (one-time use)
            await redis_client.delete(redis_key)
            logger.info("otp_verified_successfully", identifier=identifier)
        else:
            logger.warning("otp_verification_failed_mismatch", identifier=identifier)
            
        return is_valid
