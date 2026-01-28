"""OCR-based PDF converter for scanned documents."""

from pathlib import Path
from typing import Optional

import fitz
import pytesseract
from PIL import Image

from .base import BaseConverter
from ..config import ConverterConfig
from ..exceptions import ConversionError, OCRError


class OCRConverter(BaseConverter):
    """Converter for scanned PDFs using OCR.
    
    This converter renders PDF pages as images and uses Tesseract OCR
    to extract text. It's slower but works for scanned documents and
    image-based PDFs.
    """
    
    def __init__(self, config: Optional[ConverterConfig] = None):
        """Initialize the OCR converter.
        
        Args:
            config: Converter configuration.
        """
        super().__init__(config)
    
    def can_convert(self, file_path: Path) -> bool:
        """OCR can convert any PDF.
        
        Args:
            file_path: Path to the PDF file.
            
        Returns:
            True if file is a PDF, False otherwise.
        """
        # OCR is only implemented for PDFs currently
        return file_path.suffix.lower() == '.pdf'
    
    def _convert_to_markdown(self, file_path: Path) -> str:
        """Convert PDF to markdown using OCR.
        
        Args:
            file_path: Path to the PDF file.
            
        Returns:
            Markdown text content.
            
        Raises:
            ConversionError: If conversion fails.
        """
        try:
            print(f"Processing: {file_path}")
            print("Using OCR method...")
            
            doc = fitz.open(file_path)
            
            # Determine number of pages to process
            total_pages = len(doc)
            num_pages = (
                min(self.config.max_pages, total_pages)
                if self.config.max_pages
                else total_pages
            )
            
            print(f"Processing {num_pages} of {total_pages} pages with OCR...")
            
            markdown_parts = []
            
            for page_num in range(num_pages):
                try:
                    # Get the page
                    page = doc[page_num]
                    
                    # Render page to image with configured DPI
                    matrix = fitz.Matrix(self.config.ocr_dpi, self.config.ocr_dpi)
                    pix = page.get_pixmap(matrix=matrix)
                    
                    # Convert to PIL Image
                    img = Image.frombytes(
                        "RGB",
                        [pix.width, pix.height],
                        pix.samples
                    )
                    
                    # Use OCR to extract text
                    page_text = pytesseract.image_to_string(img)
                    
                    # Add page header and text
                    markdown_parts.append(f"\n\n# Page {page_num + 1}\n\n{page_text}")
                    
                    # Show progress
                    if (page_num % self.config.progress_interval == 0 or 
                        page_num == num_pages - 1):
                        print(f"Processed page {page_num + 1}/{num_pages}")
                        
                except Exception as e:
                    raise OCRError(str(file_path), page_num + 1, str(e))
            
            doc.close()
            
            result = "".join(markdown_parts)
            print(f"Extracted {len(result)} characters via OCR")
            return result
            
        except OCRError:
            raise
        except Exception as e:
            raise ConversionError(
                str(file_path),
                f"OCR processing failed: {str(e)}"
            )
