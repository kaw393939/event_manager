import pytest
from unittest.mock import patch, MagicMock
from app.services.email_service import EmailService
from app.utils.template_manager import TemplateManager

@pytest.mark.asyncio
async def test_send_user_email_success():
    template_manager = TemplateManager()
    service = EmailService(template_manager)
    user_data = {"email": "test@example.com", "nickname": "test"}
    with patch.object(service, "smtp_client") as mock_smtp, \
         patch.object(template_manager, "render_template", return_value="<html>content</html>") as mock_render:
        mock_smtp.send_email.return_value = None
        await service.send_user_email(user_data, "email_verification")
        mock_smtp.send_email.assert_called_once()
        mock_render.assert_called_once()

@pytest.mark.asyncio
async def test_send_user_email_failure():
    template_manager = TemplateManager()
    service = EmailService(template_manager)
    user_data = {"email": "fail@example.com", "nickname": "fail"}
    with patch.object(service, "smtp_client") as mock_smtp, \
         patch.object(template_manager, "render_template", return_value="<html>content</html>"):
        mock_smtp.send_email.side_effect = Exception("SMTP failed!")
        with pytest.raises(Exception):
            await service.send_user_email(user_data, "email_verification")
