import smtplib
from builtins import ValueError, dict, str
from settings.config import settings
from app.utils.smtp_connection import SMTPClient
from app.utils.template_manager import TemplateManager
from app.models.user_model import User
import logging
import re

class EmailService:
    def __init__(self, template_manager: TemplateManager):
        """Initialize the EmailService with SMTP client and template manager."""
        self.smtp_client = SMTPClient(
            server=settings.smtp_server,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password
        )
        self.template_manager = template_manager

    def is_valid_email(self, email: str) -> bool:
        """Check if the provided email has a valid format."""
        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        return re.match(email_regex, email) is not None

    async def send_user_email(self, user_data: dict, email_type: str):
        """Send an email based on the user data and email type."""
        subject_map = {
            'email_verification': "Verify Your Account",
            'password_reset': "Password Reset Instructions",
            'account_locked': "Account Locked Notification"
        }

        # Validate email format
        if not self.is_valid_email(user_data['email']):
            raise ValueError("Invalid email address format")

        if email_type not in subject_map:
            raise ValueError("Invalid email type")

        # Render email content from template
        try:
            html_content = self.template_manager.render_template(email_type, **user_data)
        except Exception as e:
            logging.error(f"Error rendering template: {e}")
            raise ValueError("Error rendering the email template")

        # Send the email via SMTP client
        try:
            self.smtp_client.send_email(subject_map[email_type], html_content, user_data['email'])
        except smtplib.SMTPException as e:
            logging.error(f"Failed to send email: {e}")
            raise ConnectionError("Failed to send the email due to SMTP error.") from e
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise

    async def send_verification_email(self, user: User):
        """Send an email verification link to the user."""
        verification_url = f"{settings.server_base_url}verify-email/{user.id}/{user.verification_token}"
        await self.send_user_email({
            "name": user.first_name,
            "verification_url": verification_url,
            "email": user.email
        }, 'email_verification')