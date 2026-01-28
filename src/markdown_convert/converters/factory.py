"""Factory for creating appropriate converters."""

from pathlib import Path
from typing import Optional

from .base import BaseConverter
from .pdf_converter import PDFConverter
from .ocr_converter import OCRConverter
from .docx_converter import DocxConverter
from ..config import ConverterConfig


class ConverterFactory:
    """Factory for creating appropriate converters based on file type.
    
    This factory implements the Factory pattern to automatically select
    the best converter for a given file.
    """
    
    @staticmethod
    def create(
        file_path: Path,
        config: Optional[ConverterConfig] = None
    ) -> BaseConverter:
        """Create an appropriate converter for the given file.
        
        Selection logic:
        1. If .docx, use DocxConverter
        2. If .pdf:
           a. If force_ocr is True, use OCRConverter
           b. If PDF has extractable text, use PDFConverter
           c. Otherwise, fall back to OCRConverter
        
        Args:
            file_path: Path to the file.
            config: Converter configuration.
            
        Returns:
            An appropriate converter instance.
        """
        config = config or ConverterConfig.default()
        
        file_path = Path(file_path)
        
        # Check for Docx/Doc
        docx_converter = DocxConverter(config)
        if docx_converter.can_convert(file_path):
            return docx_converter

        # Handle PDF
        if file_path.suffix.lower() == '.pdf':
            # If forcing OCR, use OCR converter
            if config.force_ocr:
                print("Force OCR enabled, using OCR converter")
                return OCRConverter(config)

            # Try PDF converter first (faster)
            pdf_converter = PDFConverter(config)
            if pdf_converter.can_convert(file_path):
                print("PDF contains text, using standard converter")
                return pdf_converter

            # Fall back to OCR
            print("PDF appears to be scanned, using OCR converter")
            return OCRConverter(config)

        raise ValueError(f"Unsupported file type: {file_path.suffix}")
    
    @staticmethod
    def create_pdf_converter(
        config: Optional[ConverterConfig] = None
    ) -> PDFConverter:
        """Create a standard PDF converter.
        
        Args:
            config: Converter configuration.
            
        Returns:
            PDFConverter instance.
        """
        return PDFConverter(config)
    
    @staticmethod
    def create_ocr_converter(
        config: Optional[ConverterConfig] = None
    ) -> OCRConverter:
        """Create an OCR converter.
        
        Args:
            config: Converter configuration.
            
        Returns:
            OCRConverter instance.
        """
        return OCRConverter(config)

    @staticmethod
    def create_docx_converter(
        config: Optional[ConverterConfig] = None
    ) -> DocxConverter:
        """Create a Docx converter.

        Args:
            config: Converter configuration.

        Returns:
            DocxConverter instance.
        """
        return DocxConverter(config)
