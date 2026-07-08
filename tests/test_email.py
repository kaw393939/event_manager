import pytest
from app.services.email_service import EmailService
from app.utils.template_manager import TemplateManager


@pytest.mark.asyncio
async def test_send_markdown_email(email_service_mock):
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "verification_url": "http://example.com/verify?token=abc123"
    }
    await email_service_mock.send_user_email(user_data, 'email_verification')
    email_service_mock.smtp_client.send_email.assert_called_once()

