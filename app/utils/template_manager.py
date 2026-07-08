from jinja2 import Environment, FileSystemLoader
import os
import markdown2
from pathlib import Path

class TemplateManager:
    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), '../templates')
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=True
        )
        # Dynamically determine the root path of the project
        self.root_dir = Path(__file__).resolve().parent.parent.parent  # Adjust this depending on the structure
        self.templates_dir = self.root_dir / 'templates'  # Changed from 'email_templates'
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        # Create default templates if they don't exist
        self._create_default_templates()

    def _read_template(self, template_name: str) -> str:
        try:
            template = self.env.get_template(template_name)
            return template.render()
        except Exception as e:
            raise ValueError(f"Failed to read template: {str(e)}")

    def _apply_email_styles(self, html: str) -> str:
        """Apply advanced CSS styles inline for email compatibility with excellent typography."""
        styles = {
            'body': 'font-family: Arial, sans-serif; font-size: 16px; color: #333333; background-color: #ffffff; line-height: 1.5;',
            'h1': 'font-size: 24px; color: #333333; font-weight: bold; margin-top: 20px; margin-bottom: 10px;',
            'p': 'font-size: 16px; color: #666666; margin: 10px 0; line-height: 1.6;',
            'a': 'color: #0056b3; text-decoration: none; font-weight: bold;',
            'footer': 'font-size: 12px; color: #777777; padding: 20px 0;',
            'ul': 'list-style-type: none; padding: 0;',
            'li': 'margin-bottom: 10px;'
        }
        # Wrap entire HTML content in <div> with body style
        styled_html = f'<div style="{styles["body"]}">{html}</div>'
        # Apply styles to each HTML element
        for tag, style in styles.items():
            if tag != 'body':  # Skip the body style since it's already applied to the <div>
                styled_html = styled_html.replace(f'<{tag}>', f'<{tag} style="{style}">')
        return styled_html

    def _create_default_templates(self):
        templates = {
            'email_verification.md': '# Welcome {{name}}\nPlease verify your email at: {{verification_url}}',
            'header.md': '# Header',
            'footer.md': '---\nFooter'
        }
        for name, content in templates.items():
            path = self.templates_dir / name
            if not path.exists():
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)

    def render_template(self, template_name: str, **context) -> str:
        """Render a markdown template with given context, applying advanced email styles."""
        header = self._read_template('header.md')
        footer = self._read_template('footer.md')

        # Read main template and format it with provided context
        main_template = self._read_template(f'{template_name}.md')
        main_content = main_template.format(**context)

        full_markdown = f"{header}\n{main_content}\n{footer}"
        html_content = markdown2.markdown(full_markdown)
        return self._apply_email_styles(html_content)

    def render_email_template(self, template_type: str, context: dict) -> str:
        template_name = f"{template_type}.html"
        template = self.env.get_template(template_name)
        return template.render(**context)
