import pytest
from unittest.mock import MagicMock
from app.services.email_service import EmailService
from app.utils.template_manager import TemplateManager


@pytest.mark.asyncio
async def test_send_markdown_email(mocker):
    # Provide a mocked TemplateManager
    template_manager = MagicMock()
    template_manager.render.return_value = "<html>Mocked Email</html>"

    # Create the email service with the mocked TemplateManager
    email_service = EmailService(template_manager)

    # Mock the SMTP client inside EmailService
    email_service.smtp_client = mocker.Mock()
    email_service.smtp_client.send_email = mocker.Mock()

    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "verification_url": "http://example.com/verify?token=abc123"
    }

    await email_service.send_user_email(user_data, 'email_verification')

    # Verify it was called
    email_service.smtp_client.send_email.assert_called_once()
