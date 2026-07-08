import markdown2
from pathlib import Path
import logging

class TemplateManager:
    def __init__(self):
        """Initialize TemplateManager with project path configuration."""
        self.root_dir = Path(__file__).resolve().parent.parent.parent  # Adjust this based on project structure
        self.templates_dir = self.root_dir / 'email_templates'

    def _read_template(self, filename: str) -> str:
        """Private method to read the content of a template file."""
        template_path = self.templates_dir / filename
        try:
            with open(template_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            logging.error(f"Template file not found: {template_path}")
            raise ValueError(f"Template file {filename} not found.")
        except Exception as e:
            logging.error(f"Error reading template: {e}")
            raise

    def _apply_email_styles(self, html: str) -> str:
        """Apply inline CSS styles to the HTML for better email rendering compatibility."""
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
            if tag != 'body':  # Skip the body style
                styled_html = styled_html.replace(f'<{tag}>', f'<{tag} style="{style}">')
        return styled_html

    def render_template(self, template_name: str, **context) -> str:
        """Render a markdown template with given context and return styled HTML."""
        header = self._read_template('header.md')
        footer = self._read_template('footer.md')

        # Read main template and format it with provided context
        main_template = self._read_template(f'{template_name}.md')
        main_content = main_template.format(**context)

        full_markdown = f"{header}\n{main_content}\n{footer}"
        html_content = markdown2.markdown(full_markdown)
        return self._apply_email_styles(html_content)
    