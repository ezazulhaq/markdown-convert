"""Standard PDF converter using text extraction."""

from pathlib import Path
from typing import Optional

import pymupdf4llm
import fitz

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

            doc = fitz.open(file_path)
            # Check first page for text
            if len(doc) > 0:
                text = doc[0].get_text()
                doc.close()
                return len(text.strip()) > 0
            doc.close()
            return False
        except Exception:
            return False
    
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
            
            # Use pymupdf4llm for conversion
            md_text = pymupdf4llm.to_markdown(str(file_path))
            
            print(f"Extracted {len(md_text)} characters")
            return md_text
            
        except Exception as e:
            raise ConversionError(
                str(file_path),
                f"Text extraction failed: {str(e)}"
            )
