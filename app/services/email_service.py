from builtins import ValueError, dict, str
from settings.config import settings
from app.utils.smtp_connection import SMTPClient
from app.utils.template_manager import TemplateManager
from app.models.user_model import User
import logging

# Initialize logger
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self, template_manager: TemplateManager):
        self.smtp_client = SMTPClient(
            server=settings.smtp_server,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password
        )
        self.template_manager = template_manager
        logger.info("EmailService initialized with SMTPClient and TemplateManager.")

    async def send_user_email(self, user_data: dict, email_type: str):
        subject_map = {
            'email_verification': "Verify Your Account",
            'password_reset': "Password Reset Instructions",
            'account_locked': "Account Locked Notification"
        }

        if email_type not in subject_map:
            logger.error(f"Invalid email type: {email_type}")
            raise ValueError("Invalid email type")

        try:
            logger.info(f"Rendering template for email type: {email_type} to {user_data['email']}.")
            html_content = self.template_manager.render_template(email_type, **user_data)
            logger.info(f"Sending {email_type} email to {user_data['email']}.")
            self.smtp_client.send_email(subject_map[email_type], html_content, user_data['email'])
            logger.info(f"{email_type} email sent successfully to {user_data['email']}.")
        except Exception as error:
            logger.error(f"Failed to send {email_type} email to {user_data['email']}: {error}")
            raise

    async def send_verification_email(self, user: User):
        verification_url = f"{settings.server_base_url}verify-email/{user.id}/{user.verification_token}"
        logger.info(f"Preparing verification email for user ID {user.id}.")
        try:
            await self.send_user_email({
                "name": user.first_name,
                "verification_url": verification_url,
                "email": user.email
            }, 'email_verification')
            logger.info(f"Verification email sent successfully to {user.email}.")
        except Exception as error:
            logger.error(f"Failed to send verification email to {user.email}: {error}")
            raise
