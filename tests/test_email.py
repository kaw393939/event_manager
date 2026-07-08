import pytest
from app.services.email_service import EmailService
from app.utils.template_manager import TemplateManager
from app.utils.smtp_connection import SMTPClient

# Patch the SMTPClient.send_email method to avoid external SMTP connection
@pytest.fixture(autouse=True)
def patch_smtp(monkeypatch):
    def fake_send_email(self, subject, html_content, recipient):
        # Optionally, you can log the fake call or store values for later assertions
        print(f"Fake send_email called with subject: {subject}, recipient: {recipient}")
    monkeypatch.setattr(SMTPClient, "send_email", fake_send_email)

@pytest.mark.asyncio
async def test_send_markdown_email(email_service):
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "verification_url": "http://example.com/verify?token=abc123"
    }
    await email_service.send_user_email(user_data, 'email_verification')
    # Manual verification in Mailtrap can be omitted since we're now faking the call.
