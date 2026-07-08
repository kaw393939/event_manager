import pytest
from unittest.mock import MagicMock
from app.services.email_service import EmailService
from app.utils.template_manager import TemplateManager


@pytest.fixture
def email_service():
    """Fixture to provide a mocked EmailService."""
    # Mock the TemplateManager
    template_manager = MagicMock(TemplateManager)

    # Create the EmailService with the mocked TemplateManager
    service = EmailService(template_manager=template_manager)

    # Mock the send_email method in SMTPClient
    service.smtp_client.send_email = MagicMock()

    return service


@pytest.mark.asyncio
async def test_send_markdown_email(email_service):
    """Test sending a markdown email with proper handling of templates."""
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "verification_url": "http://example.com/verify?token=abc123"
    }

    # Mock the render_template method to return a valid HTML string
    email_content = "<html><body><h1>Verify Your Account</h1><p>Click <a href='{verification_url}'>here</a> to verify.</p></body></html>"
    email_service.template_manager.render_template = MagicMock(return_value=email_content)

    # Call the method to send the email
    await email_service.send_user_email(user_data, 'email_verification')

    # Assert that send_email was called with the correct parameters
    email_service.smtp_client.send_email.assert_called_once_with(
        "Verify Your Account",  # Subject
        email_content,          # Mocked HTML content
        "test@example.com"      # Recipient email
    )

    # Assert that render_template was called with the correct arguments
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
        