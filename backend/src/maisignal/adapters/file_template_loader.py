"""File-system adapter for loading HTML email templates."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FileTemplateLoader:
    """Reads an HTML email template from disk."""

    def __init__(self, template_path: Path) -> None:
        self._template_path = template_path

    def load(self) -> str:
        """Read and return the HTML template content.

        Raises:
            FileNotFoundError: If the template file does not exist.
        """
        if not self._template_path.is_file():
            raise FileNotFoundError(
                f"HTML template not found: {self._template_path}"
            )
        html = self._template_path.read_text(encoding="utf-8")
        logger.info("Loaded HTML template (%d chars).", len(html))
        return html
