
import pytest
from smtplib import SMTPServerDisconnected
from app.utils.smtp_connection import SMTPClient

@pytest.fixture
def smtp_client():
    return SMTPClient(
        host="smtp.example.com",
        port=587,
        username="user",
        password="pass"
    )

def test_send_email_connection_error(smtp_client, monkeypatch):
    def mock_init(*args, **kwargs):
        raise SMTPServerDisconnected("Connection lost")
    monkeypatch.setattr("smtplib.SMTP.__init__", mock_init)
    with pytest.raises(SMTPServerDisconnected):
        smtp_client.send_email(
            subject="Test Subject",
            content="Test Content",
            recipient="recipient@example.com"
        )