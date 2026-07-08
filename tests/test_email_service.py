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
    await email_service.send_user_email(user_data, 'verification_email')
    email_service.smtp_client.send_email.assert_called_once()

@pytest.mark.asyncio
async def test_send_verification_email(email_service):
    user = MagicMock()
    user.email = "test@example.com"
    user.first_name = "Test"
    user.id = "123"
    user.verification_token = "abc123"
    await email_service.send_verification_email(user)
    email_service.smtp_client.send_email.assert_called_once()

@pytest.mark.asyncio
async def test_send_user_email(email_service):
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "verification_url": "http://example.com/verify?token=abc123"
    }
    await email_service.send_user_email(user_data, 'verification_email')
    email_service.smtp_client.send_email.assert_called_once()

@pytest.mark.asyncio
async def test_send_user_email_invalid_type(email_service):
    user_data = {
        "email": "test@example.com",
        "name": "Test User"
    }
    with pytest.raises(ValueError):
        await email_service.send_user_email(user_data, 'invalid_type')

@pytest.mark.asyncio
async def test_send_user_email_missing_email(email_service):
    user_data = {
        "name": "Test User",
        "verification_url": "http://example.com/verify?token=abc123"
    }
    with pytest.raises(KeyError):
        await email_service.send_user_email(user_data, 'email_verification')