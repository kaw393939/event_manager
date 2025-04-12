import pytest
from unittest.mock import patch, MagicMock
from app.services.email_service import EmailService
from app.utils.template_manager import TemplateManager
from app.utils.smtp_connection import SMTPClient

@pytest.mark.asyncio
async def test_send_markdown_email():
    mock_smtp_client = MagicMock(spec=SMTPClient)
    email_service = EmailService(TemplateManager())
    email_service.smtp_client = mock_smtp_client  # Inject the mock

    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "verification_url": "http://example.com/verify?token=abc123"
    }

    await email_service.send_user_email(user_data, 'email_verification')

    assert mock_smtp_client.send_email.called