import pytest
from app.utils.template_manager import TemplateManager

def test_read_template():
    template_manager = TemplateManager()
    template = template_manager._read_template("verification_email.md")
    assert template is not None
    assert "{verification_url}" in template

def test_render_email_template():
    template_manager = TemplateManager()
    rendered = template_manager.render_email_template("verification_email", {
        "verification_url": "http://test.com",
        "name": "Test User"
    })
    assert "http://test.com" in rendered
    assert "Test User" in rendered

def test_render_email_template_missing_context():
    template_manager = TemplateManager()
    with pytest.raises(KeyError):
        template_manager.render_email_template("verification_email", {
            "name": "Test User"
        })