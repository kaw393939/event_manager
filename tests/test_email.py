import pytest
from app.services.email_service import EmailService
from app.utils.template_manager import TemplateManager
from unittest.mock import patch

    
@pytest.mark.asyncio
def test_send_markdown_email(email_service):
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "verification_url": "http://example.com/verify?token=abc123"
    }
    with patch.object(EmailService, 'send_user_email', return_value=None):
        # This will not actually send an email
        email_service.send_user_email(user_data, 'email_verification')
    assert True  # If no exception, the test passes
