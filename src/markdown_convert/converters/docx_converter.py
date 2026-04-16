"""Docx converter using mammoth and markdownify."""

import base64
import re
from io import BytesIO
from pathlib import Path
from typing import Optional

import mammoth
import pytesseract
from markdownify import markdownify as md
from PIL import Image

from ..config import ConverterConfig
from ..exceptions import ConversionError
from .base import BaseConverter

# Compiled regex for finding base64-encoded images in HTML
IMG_PATTERN = re.compile(r'<img\s+src="data:image/[^;]+;base64,([^"]+)"')


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
        return file_path.suffix.lower() in {".docx", ".doc"}

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
                    if (
                        "File is not a zip file" in str(e)
                        or file_path.suffix.lower() == ".doc"
                    ):
                        raise ValueError(
                            "Legacy binary .doc files are not supported. "
                            "Please convert to .docx or ensure the file is a valid "
                            "XML-based Word document."
                        )
                    raise e

                html = result.value
                messages = result.messages

                if messages:
                    for message in messages:
                        print(f"Docx warning: {message}")

            # Convert HTML to Markdown (strip images to avoid base64 bloat)
            markdown_text = md(html, heading_style="ATX", strip=["img"])

            # If no text extracted, try OCR on embedded images
            if not markdown_text.strip():
                print("No text found, attempting OCR on embedded images...")
                markdown_text = self._extract_text_from_images(html)

            print(f"Extracted {len(markdown_text)} characters")
            return markdown_text

        except Exception as e:
            raise ConversionError(str(file_path), f"Docx conversion failed: {str(e)}")

    def _extract_text_from_images(self, html: str) -> str:
        """Extract text from base64-encoded images using OCR.

        Args:
            html: HTML content containing base64 images.

        Returns:
            Markdown text extracted from images via OCR.
        """
        # Find all base64-encoded images in HTML.
        # We convert finditer to a list once to avoid redundant scanning of the HTML string,
        # while still processing the image data itself lazily in the loop.
        matches = list(IMG_PATTERN.finditer(html))
        num_images = len(matches)

        if num_images == 0:
            print("No images found in document")
            return ""

        print(f"Found {num_images} image(s), processing with OCR...")
        ocr_parts = []
        ocr_cache = {}

        # Process matches to extract text from images
        for idx, match in enumerate(matches):
            try:
                # Extract base64 data lazily
                base64_data = match.group(1)

                # Use cached OCR result if available for identical images
                if base64_data in ocr_cache:
                    ocr_text = ocr_cache[base64_data]
                else:
                    # Decode base64 image
                    img_bytes = base64.b64decode(base64_data)
                    img = Image.open(BytesIO(img_bytes))

                    # Run OCR
                    ocr_text = pytesseract.image_to_string(img)
                    ocr_cache[base64_data] = ocr_text

                # Add to results if text was found
                if ocr_text.strip():
                    ocr_parts.append(f"\n\n# Image {idx + 1}\n\n{ocr_text}")

                # Progress reporting
                if (idx + 1) % 10 == 0 or (idx + 1) == num_images:
                    print(f"Processed {idx + 1}/{num_images} image(s)")

            except Exception as e:
                print(f"Warning: Failed to OCR image {idx + 1}: {str(e)}")
                continue

        result = "".join(ocr_parts)
        if result:
            print(f"OCR extracted text from {len(ocr_parts)} image(s)")
        else:
            print("No text could be extracted from images")

        return result
