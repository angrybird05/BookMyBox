"""Celery worker module."""

from app.workers.celery_app import celery_app
from app.workers.tasks import (
    send_otp_sms_task,
    send_welcome_email_task,
    send_password_reset_email_task,
    send_booking_confirmation_email_task,
    generate_ticket_pdf_task,
)
