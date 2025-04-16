import pytest
from app.utils.smtp_connection import SMTPClient
from unittest.mock import patch
import smtplib

def test_smtp_send_email_success():
    client = SMTPClient("smtp.example.com", 587, "user@example.com", "password")
    with patch("smtplib.SMTP") as mock_smtp:
        instance = mock_smtp.return_value.__enter__.return_value
        instance.sendmail.return_value = None
        client.send_email("Subject", "<b>Hi</b>", "to@example.com")
        instance.sendmail.assert_called_once()

def test_smtp_send_email_failure():
    client = SMTPClient("smtp.example.com", 587, "user@example.com", "password")
    with patch("smtplib.SMTP") as mock_smtp:
        instance = mock_smtp.return_value.__enter__.return_value
        instance.sendmail.side_effect = smtplib.SMTPException("fail")
        with pytest.raises(Exception):
            client.send_email("Subject", "<b>Hi</b>", "to@example.com")

def test_smtp_send_email_login_failure():
    client = SMTPClient("smtp.example.com", 587, "user@example.com", "password")
    with patch("smtplib.SMTP") as mock_smtp:
        instance = mock_smtp.return_value.__enter__.return_value
        instance.login.side_effect = smtplib.SMTPAuthenticationError(535, b'5.7.8 Authentication failed')
        with pytest.raises(Exception):
            client.send_email("Subject", "<b>Hi</b>", "to@example.com")

def test_smtp_send_email_starttls_failure():
    client = SMTPClient("smtp.example.com", 587, "user@example.com", "password")
    with patch("smtplib.SMTP") as mock_smtp:
        instance = mock_smtp.return_value.__enter__.return_value
        instance.starttls.side_effect = smtplib.SMTPException("TLS fail")
        with pytest.raises(Exception):
            client.send_email("Subject", "<b>Hi</b>", "to@example.com")

# Add more tests for error handling, connection errors, etc.
