import pytest
from unittest.mock import MagicMock
from app.services.email_service import EmailService
from app.utils.template_manager import TemplateManager
from app.models.user_model import User

@pytest.fixture
def email_service():
    """Fixture to mock the EmailService."""
    # Mock TemplateManager
    template_manager = MagicMock(TemplateManager)
    
    # Create the EmailService instance with mocked TemplateManager
    service = EmailService(template_manager=template_manager)
    
    # Mock the send_email method to avoid actually sending emails
    #service.smtp_client.send_email = MagicMock()
    service.smtp_client.send_email = MagicMock(return_value=True)

    return service

@pytest.mark.asyncio
async def test_send_markdown_email(email_service):
    """Test sending a markdown email with proper handling of templates."""
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "verification_url": "http://example.com/verify?token=abc123"
    }

    # Mock the render_template method to return a simple HTML string
    email_content = "<html><body><h1>Verify Your Account</h1></body></html>"
    email_service.template_manager.render_template = MagicMock(return_value=email_content)

    # Call the method that sends the email
    await email_service.send_user_email(user_data, 'email_verification')
    
    # Assert that send_email was called with the correct subject and content
    email_service.smtp_client.send_email.assert_called_once_with(
        "Verify Your Account",  # Subject
        email_content,           # Actual HTML content returned by mock
        "test@example.com"       # Recipient email
    )
    
    # Optionally, check that the template rendering method was called
    email_service.template_manager.render_template.assert_called_once_with(
        'email_verification', 
        **user_data
    )

@pytest.mark.asyncio
async def test_send_email_with_template_error(email_service):
    """Test that errors in template rendering are caught."""
    # Mock render_template to raise an error
    email_service.template_manager.render_template = MagicMock(side_effect=ValueError("Template error"))

    with pytest.raises(ValueError, match="Error rendering the email template"):
        await email_service.send_user_email({
            "email": "test@example.com",
            "name": "Test User"
        }, 'email_verification')