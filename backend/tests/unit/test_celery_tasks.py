"""Unit tests for Celery background tasks."""

from unittest.mock import AsyncMock, patch
import pytest
from app.workers.tasks import send_otp_sms_task, send_welcome_email_task


@patch("app.workers.tasks.NotificationService")
def test_send_otp_sms_task(mock_service_class):
    """Test send_otp_sms_task delegates to NotificationService."""
    mock_service_instance = mock_service_class.return_value
    mock_service_instance.send_otp_sms = AsyncMock()

    send_otp_sms_task("9876543210", "123456")

    mock_service_class.assert_called_once()
    mock_service_instance.send_otp_sms.assert_called_once_with("9876543210", "123456")


@patch("app.workers.tasks.NotificationService")
def test_send_welcome_email_task(mock_service_class):
    """Test send_welcome_email_task delegates to NotificationService."""
    mock_service_instance = mock_service_class.return_value
    mock_service_instance.send_welcome_email = AsyncMock()

    send_welcome_email_task("user@example.com", "Test User")

    mock_service_class.assert_called_once()
    mock_service_instance.send_welcome_email.assert_called_once_with("user@example.com", "Test User")
