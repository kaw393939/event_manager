import pytest
from app.utils.template_manager import TemplateManager


def test_template_manager_render():
    tm = TemplateManager()
    # Should not raise for a simple template
    result = tm.render_template("Hello {{ name }}", {"name": "World"})
    assert result == "Hello World"

    # Test with missing variable
    result = tm.render_template("Hi {{ name }} and {{ missing }}", {"name": "A"})
    assert "A" in result


def test_apply_email_styles_basic():
    tm = TemplateManager()
    html = "<h1>Header</h1><p>Body</p>"
    styled = tm._apply_email_styles(html)
    assert 'font-family' in styled
    assert '<div' in styled
    assert '<h1 style=' in styled
    assert '<p style=' in styled


def test_render_template_from_file_handles_missing_file(tmp_path, monkeypatch):
    tm = TemplateManager()
    # Patch templates_dir to a temp dir without templates
    tm.templates_dir = tmp_path
    with pytest.raises(FileNotFoundError):
        tm.render_template_from_file("nonexistent", name="Test")


def test_render_template_from_file_success(tmp_path, monkeypatch):
    tm = TemplateManager()
    tm.templates_dir = tmp_path
    (tmp_path / "header.md").write_text("HEADER")
    (tmp_path / "footer.md").write_text("FOOTER")
    (tmp_path / "welcome.md").write_text("Welcome, {name}!")
    html = tm.render_template_from_file("welcome", name="TestUser")
    assert "TestUser" in html
    assert "HEADER" in html or "FOOTER" in html or "<div" in html


def test_render_template_from_file_context_edge(tmp_path, monkeypatch):
    tm = TemplateManager()
    tm.templates_dir = tmp_path
    (tmp_path / "header.md").write_text("HEADER")
    (tmp_path / "footer.md").write_text("FOOTER")
    (tmp_path / "edge.md").write_text("Welcome!")
    # No context provided, should not error
    html = tm.render_template_from_file("edge")
    assert "Welcome!" in html


# Add more tests for error handling and edge cases as needed
