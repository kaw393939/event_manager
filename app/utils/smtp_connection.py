import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from settings.config import settings
import logging
import asyncio

class SMTPClient:
    def __init__(self, server: str, port: int, username: str, password: str):
        self.server = server
        self.port = port
        self.username = username
        self.password = password

    async def send_email(self, subject: str, html_content: str, recipient: str):
        """Async method to send email using smtplib."""
        try:
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.username
            message['To'] = recipient
            message.attach(MIMEText(html_content, 'html'))

            await asyncio.to_thread(self._send_smtp_email, message, recipient)

            logging.info(f"Email sent to {recipient}")
        except Exception as e:
            logging.error(f"Failed to send email: {str(e)}")
            raise

    def _send_smtp_email(self, message, recipient):
        """Blocking method to actually send the email using smtplib"""
        with smtplib.SMTP(self.server, self.port) as server:
            server.starttls()  # Use TLS
            server.login(self.username, self.password)
            server.sendmail(self.username, recipient, message.as_string())
