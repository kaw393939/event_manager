import pytest
from app.services.email_service import EmailService
from app.utils.template_manager import TemplateManager

    
@pytest.mark.asyncio
async def test_send_markdown_email(email_service):
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "verification_url": "http://example.com/verify?token=abc123"
    }
    result = await email_service.send_email(
        recipient_email=user_data["email"],
        subject="Test Email",
        body="Test email body",
        template_name='email_verification'
    )
    assert result is True
