"""Standard PDF converter using text extraction."""

from pathlib import Path
from typing import Optional

import pymupdf4llm
import pymupdf as fitz

from .base import BaseConverter
from ..config import ConverterConfig
from ..exceptions import ConversionError


class PDFConverter(BaseConverter):
    """Converter for text-based PDFs using direct text extraction.
    
    This converter uses pymupdf4llm to extract text directly from PDFs
    that contain selectable text. It's fast and efficient for standard PDFs.
    """
    
    def __init__(self, config: Optional[ConverterConfig] = None):
        """Initialize the PDF converter.
        
        Args:
            config: Converter configuration.
        """
        super().__init__(config)
        self._cached_doc = None
        self._cached_path = None

    def __del__(self) -> None:
        """Ensure the cached document is closed when the converter is destroyed."""
        self._close_cached_doc()

    def _close_cached_doc(self) -> None:
        """Close the cached document if it exists."""
        if self._cached_doc:
            try:
                self._cached_doc.close()
            except Exception:
                pass
            finally:
                self._cached_doc = None
                self._cached_path = None
    
    def can_convert(self, file_path: Path) -> bool:
        """Check if PDF contains extractable text.
        
        Args:
            file_path: Path to the PDF file.
            
        Returns:
            True if PDF contains text, False otherwise.
        """
        try:
            if file_path.suffix.lower() != '.pdf':
                return False

            # If already cached this file, reuse it
            if self._cached_doc and self._cached_path == file_path:
                doc = self._cached_doc
            else:
                self._close_cached_doc()
                doc = fitz.open(file_path)

            # Check first page for text
            if len(doc) > 0:
                text = doc[0].get_text()
                if len(text.strip()) > 0:
                    # Cache the document for the subsequent conversion call
                    self._cached_doc = doc
                    self._cached_path = file_path
                    return True

            # If we opened it but it's not a text PDF, close it
            doc.close()
            return False
        except Exception:
            self._close_cached_doc()
            return False

    def convert(self, file_path: Path) -> Optional[Path]:
        """Convert PDF to markdown with cached document cleanup.

        Args:
            file_path: Path to the PDF file.

        Returns:
            Path to the output markdown file.
        """
        try:
            return super().convert(file_path)
        finally:
            self._close_cached_doc()
    
    def _convert_to_markdown(self, file_path: Path) -> str:
        """Convert PDF to markdown using text extraction.
        
        Args:
            file_path: Path to the PDF file.
            
        Returns:
            Markdown text content.
            
        Raises:
            ConversionError: If conversion fails.
        """
        try:
            print(f"Processing: {file_path}")
            print("Using text extraction method...")
            
            # Use cached document if available, otherwise open file
            if self._cached_doc and self._cached_path == file_path:
                doc_to_convert = self._cached_doc
            else:
                self._close_cached_doc()
                doc_to_convert = str(file_path)

            # Use pymupdf4llm for conversion
            md_text = pymupdf4llm.to_markdown(doc_to_convert)
            
            print(f"Extracted {len(md_text)} characters")
            return md_text
            
        except Exception as e:
            raise ConversionError(
                str(file_path),
                f"Text extraction failed: {str(e)}"
            )
