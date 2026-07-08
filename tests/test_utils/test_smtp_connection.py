import pytest
from unittest.mock import patch, MagicMock
from app.utils.smtp_connection import SMTPClient

@pytest.fixture
def smtp_client():
    return SMTPClient(
        host="smtp.example.com",
        port=587,
        username="test@example.com",
        password="password",
        use_tls=True
    )

@patch('smtplib.SMTP')
def test_send_email_success(mock_smtp, smtp_client):
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server
    
    smtp_client.send_email(
        subject="Test Subject",
        content="Test Content",
        recipient="recipient@example.com"
    )
    
    mock_server.send_message.assert_called_once()

@patch('smtplib.SMTP')
def test_send_email_connection_error(mock_smtp, smtp_client):
    mock_smtp.side_effect = Exception("Connection failed")
    
    smtp_client.send_email(
        subject="Test Subject",
        content="Test Content",
        recipient="recipient@example.com"
    )
    # Should handle the error gracefully

@patch('smtplib.SMTP')
def test_smtp_context_manager(mock_smtp, smtp_client):
    with smtp_client.get_server() as server:
        assert server is not None
    mock_smtp.return_value.__enter__.assert_called_once()
    mock_smtp.return_value.__exit__.assert_called_once()