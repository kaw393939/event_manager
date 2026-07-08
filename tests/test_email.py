from unittest.mock import MagicMock
import pytest
from app.services.email_service import EmailService
from app.utils.template_manager import TemplateManager

@pytest.mark.asyncio
async def test_send_markdown_email(email_service):
    # Mock the SMTP client
    smtp_mock = MagicMock()
    smtp_mock.send_email.return_value = None  # No-op

    email_service.smtp_client = smtp_mock
    email_service.template_manager = TemplateManager()

    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "verification_url": "http://example.com/verify?token=abc123"
    }

    await email_service.send_user_email(user_data, 'email_verification')

    # Assert the mocked email method was called once
    smtp_mock.send_email.assert_called_once()
