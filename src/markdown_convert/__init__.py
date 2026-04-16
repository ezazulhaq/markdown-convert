"""markdown-convert: Convert PDF files to Markdown with OCR support.

This package provides tools to convert PDF files to Markdown format,
with automatic fallback to OCR for scanned documents.
"""

__version__ = '1.1.7'
__author__ = 'Ezazul Haq Abdul'
__license__ = 'MIT'

from .config import ConverterConfig
from .converters import (
    BaseConverter,
    PDFConverter,
    OCRConverter,
    ConverterFactory,
)
from .exceptions import (
    MarkdownConvertError,
    PDFNotFoundError,
    ConversionError,
    OCRError,
    InvalidConfigError,
)

# Convenience function for simple usage
def convert_pdf(
    pdf_path: str,
    output_dir: str = None,
    max_pages: int = None,
    force_ocr: bool = False,
    skip_existing: bool = True,
):
    """Convert a PDF file to Markdown.
    
    This is a convenience function for simple usage. For more control,
    use the converter classes directly.
    
    Args:
        pdf_path: Path to the PDF file.
        output_dir: Optional output directory.
        max_pages: Maximum number of pages to process.
        force_ocr: Force OCR even if text can be extracted.
        skip_existing: Skip if output file already exists.
        
    Returns:
        Path to the output markdown file, or None if skipped.
        
    Example:
        >>> from markdown_convert import convert_pdf
        >>> convert_pdf('document.pdf', output_dir='output/')
    """
    from pathlib import Path
    
    config = ConverterConfig(
        output_dir=Path(output_dir) if output_dir else None,
        max_pages=max_pages,
        force_ocr=force_ocr,
        skip_existing=skip_existing,
    )
    
    converter = ConverterFactory.create(Path(pdf_path), config)
    return converter.convert(Path(pdf_path))


__all__ = [
    # Version
    '__version__',
    '__author__',
    '__license__',
    
    # Main function
    'convert_pdf',
    
    # Configuration
    'ConverterConfig',
    
    # Converters
    'BaseConverter',
    'PDFConverter',
    'OCRConverter',
    'ConverterFactory',
    
    # Exceptions
    'MarkdownConvertError',
    'PDFNotFoundError',
    'ConversionError',
    'OCRError',
    'InvalidConfigError',
]
