import pytest
from app.services.email_service import EmailService
from app.utils.template_manager import TemplateManager

class DummySMTPClient:
    def __init__(self):
        self.calls = []
    def send_email(self, subject, html_body, to_address):
        # record the arguments so you can assert on them
        self.calls.append((subject, html_body, to_address))
@pytest.mark.asyncio
async def test_send_markdown_email(email_service, monkeypatch):
    dummy = DummySMTPClient()
    # swap out the real SMTP client
    monkeypatch.setattr(email_service, "smtp_client", dummy)

    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "verification_url": "http://example.com/verify?token=abc123"
    }
    await email_service.send_user_email(user_data, "email_verification")

    # now assert that we “sent” exactly one email, with the correct subject/body/to
    assert len(dummy.calls) == 1
    subject, html_body, to_addr = dummy.calls[0]
    assert to_addr == "test@example.com"
    assert "Verify Your Account" in subject
    assert "http://example.com/verify?token=abc123" in html_body
