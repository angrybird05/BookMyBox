"""Celery background tasks for emails, SMS, and ticket processing."""

import asyncio
from app.workers.celery_app import celery_app
from app.services.notification import NotificationService
from app.services.ticket import TicketService
from app.repositories.booking import BookingRepository
from app.database.session import get_db_context


@celery_app.task
def send_otp_sms_task(phone: str, otp: str) -> None:
    """Send SMS verification code asynchronously."""
    service = NotificationService()
    asyncio.run(service.send_otp_sms(phone, otp))


@celery_app.task
def send_welcome_email_task(email: str, name: str) -> None:
    """Send welcome email to newly registered users asynchronously."""
    service = NotificationService()
    asyncio.run(service.send_welcome_email(email, name))


@celery_app.task
def send_password_reset_email_task(email: str, token: str) -> None:
    """Send password reset link email asynchronously."""
    service = NotificationService()
    asyncio.run(service.send_password_reset_email(email, token))


@celery_app.task
def send_booking_confirmation_email_task(
    email: str, booking_ref: str, ground_name: str, booking_date: str
) -> None:
    """Send booking confirmation email asynchronously."""
    service = NotificationService()
    asyncio.run(service.send_booking_confirmation_email(email, booking_ref, ground_name, booking_date))


@celery_app.task
def generate_ticket_pdf_task(booking_id_str: str) -> None:
    """Background task to pre-generate and cache/store booking ticket PDF."""
    import uuid
    booking_id = uuid.UUID(booking_id_str)
    
    async def run_generation():
        async with get_db_context() as db:
            booking_repo = BookingRepository(db)
            booking = await booking_repo.get_details(booking_id)
            if booking:
                # Triggers the reportlab PDF generation in-memory to ensure it works
                TicketService.generate_pdf_ticket(booking)

    asyncio.run(run_generation())
