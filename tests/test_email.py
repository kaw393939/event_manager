import pytest
from app.services.email_service import EmailService
from app.utils.template_manager import TemplateManager
from unittest.mock import patch, MagicMock

    
@pytest.mark.asyncio
@patch("app.utils.smtp_connection.smtplib.SMTP")
async def test_send_markdown_email(mock_smtp):
    '''setting up the fake client'''
    smtp_instance = MagicMock()
    mock_smtp.return_value.__enter__.return_value = smtp_instance
    '''creating email service'''
    email_service = EmailService(template_manager=TemplateManager())
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "verification_url": "http://example.com/verify?token=abc123"
    }
    await email_service.send_user_email(user_data, 'email_verification')
    # Manual verification in Mailtrap
    smtp_instance.sendmail.assert_called_once()

