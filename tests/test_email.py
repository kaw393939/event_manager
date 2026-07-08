import pytest
from unittest.mock import MagicMock
from app.services.email_service import EmailService
from app.utils.template_manager import TemplateManager
from app.utils.smtp_connection import SMTPClient
from app.models.user_model import User

@pytest.fixture
def email_service():
    template_manager = TemplateManager()
    service = EmailService(template_manager=template_manager)
    service.smtp_client = MagicMock()
    return service

@pytest.mark.asyncio
async def test_send_markdown_email(email_service):
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "verification_url": "http://example.com/verify?token=abc123"
    }
    await email_service.send_user_email(user_data, 'email_verification')
    email_service.smtp_client.send_email.assert_called_once()

@pytest.mark.asyncio
async def test_send_user_email(email_service):
    template_manager = TemplateManager()
    smtp_client = SMTPClient(
        host="smtp.example.com",
        port=587,
        username="user",
        password="pass"
    )
    email_service = EmailService(template_manager)
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "verification_url": "http://example.com/verify?token=abc123"
    }
    await email_service.send_user_email(user_data, 'email_verification')
    email_service.smtp_client.send_email.assert_called_once()
