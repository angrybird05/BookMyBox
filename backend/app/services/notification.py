"""Notification service for dispatching emails, SMS, and push notifications."""

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class NotificationService:
    """Service to send out emails and SMS notifications. Currently operates in mock mode."""

    def __init__(self):
        self.settings = get_settings()

    async def send_otp_sms(self, phone: str, otp: str) -> None:
        """Mock SMS dispatcher for phone OTP verification."""
        logger.info(
            "notification_sms_sent",
            recipient=phone,
            message=f"Your BookMyBox verification code is: {otp}. Valid for 5 minutes.",
        )

    async def send_welcome_email(self, email: str, name: str) -> None:
        """Mock email dispatcher for welcoming new registered users."""
        logger.info(
            "notification_email_sent",
            recipient=email,
            subject="Welcome to BookMyBox!",
            message=f"Hi {name}, thank you for registering with BookMyBox! Start booking box cricket grounds in your city.",
        )

    async def send_password_reset_email(self, email: str, token: str) -> None:
        """Mock email dispatcher for password reset instructions."""
        reset_link = f"http://localhost:5173/reset-password?token={token}"
        logger.info(
            "notification_email_sent",
            recipient=email,
            subject="Reset Your BookMyBox Password",
            message=f"Click the following link to reset your password: {reset_link}. Valid for 30 minutes.",
        )

    async def send_booking_confirmation_email(self, email: str, booking_ref: str, ground_name: str, booking_date: str) -> None:
        """Mock email dispatcher for successful booking confirmations."""
        logger.info(
            "notification_email_sent",
            recipient=email,
            subject=f"Booking Confirmed: {booking_ref}",
            message=f"Your booking for {ground_name} on {booking_date} has been confirmed. Booking Ref: {booking_ref}.",
        )
