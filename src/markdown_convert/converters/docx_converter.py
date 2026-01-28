"""Docx converter using mammoth and markdownify."""

from pathlib import Path
from typing import Optional

import mammoth
from markdownify import markdownify as md

from .base import BaseConverter
from ..config import ConverterConfig
from ..exceptions import ConversionError


class DocxConverter(BaseConverter):
    """Converter for Docx files.

    This converter uses mammoth to convert Docx to HTML,
    and then uses markdownify to convert HTML to Markdown.
    """

    def __init__(self, config: Optional[ConverterConfig] = None):
        """Initialize the Docx converter.

        Args:
            config: Converter configuration.
        """
        super().__init__(config)

    def can_convert(self, file_path: Path) -> bool:
        """Check if file is a Doc/Docx file.

        Args:
            file_path: Path to the file.

        Returns:
            True if file is a .doc or .docx file, False otherwise.
        """
        return file_path.suffix.lower() in {'.docx', '.doc'}

    def _convert_to_markdown(self, file_path: Path) -> str:
        """Convert Docx to markdown.

        Args:
            file_path: Path to the Docx file.

        Returns:
            Markdown text content.

        Raises:
            ConversionError: If conversion fails.
        """
        try:
            print(f"Processing: {file_path}")
            print("Using Docx converter...")

            with open(file_path, "rb") as docx_file:
                try:
                    result = mammoth.convert_to_html(docx_file)
                except Exception as e:
                    # Mammoth raises errors for non-zip files (binary .doc)
                    if "File is not a zip file" in str(e) or file_path.suffix.lower() == '.doc':
                        raise ValueError(
                            "Legacy binary .doc files are not supported. "
                            "Please convert to .docx or ensure the file is a valid XML-based Word document."
                        )
                    raise e

                html = result.value
                messages = result.messages

                if messages:
                    for message in messages:
                        print(f"Docx warning: {message}")

            # Convert HTML to Markdown
            markdown_text = md(html, heading_style="ATX")

            print(f"Extracted {len(markdown_text)} characters")
            return markdown_text

        except Exception as e:
            raise ConversionError(
                str(file_path),
                f"Docx conversion failed: {str(e)}"
            )
