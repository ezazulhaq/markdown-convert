"""Tests for converter classes."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from markdown_convert.config import ConverterConfig
from markdown_convert.converters import (
    PDFConverter,
    OCRConverter,
    ConverterFactory,
)
from markdown_convert.exceptions import ConversionError


class TestPDFConverter:
    """Tests for PDFConverter class."""
    
    def test_init_with_default_config(self):
        """Test PDFConverter initialization with default config."""
        converter = PDFConverter()
        assert converter.config is not None
        assert isinstance(converter.config, ConverterConfig)
    
    def test_init_with_custom_config(self):
        """Test PDFConverter initialization with custom config."""
        config = ConverterConfig(max_pages=10, force_ocr=True)
        converter = PDFConverter(config)
        assert converter.config.max_pages == 10
        assert converter.config.force_ocr is True
    
    @patch('markdown_convert.converters.pdf_converter.fitz.open')
    def test_can_convert_returns_true_for_text_pdf(self, mock_fitz_open):
        """Test can_convert returns True for PDFs with text."""
        # Mock PDF document with text
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Sample text content"
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz_open.return_value = mock_doc
        
        converter = PDFConverter()
        result = converter.can_convert(Path("test.pdf"))
        
        assert result is True
        mock_doc.close.assert_called_once()
    
    @patch('markdown_convert.converters.pdf_converter.fitz.open')
    def test_can_convert_returns_false_for_scanned_pdf(self, mock_fitz_open):
        """Test can_convert returns False for PDFs without text."""
        # Mock PDF document without text
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = ""
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz_open.return_value = mock_doc
        
        converter = PDFConverter()
        result = converter.can_convert(Path("test.pdf"))
        
        assert result is False


class TestOCRConverter:
    """Tests for OCRConverter class."""
    
    def test_init_with_default_config(self):
        """Test OCRConverter initialization with default config."""
        converter = OCRConverter()
        assert converter.config is not None
        assert isinstance(converter.config, ConverterConfig)
    
    def test_can_convert_returns_true_for_pdf(self):
        """Test can_convert returns True for PDF files."""
        converter = OCRConverter()
        result = converter.can_convert(Path("any.pdf"))
        assert result is True

    def test_can_convert_returns_false_for_non_pdf(self):
        """Test can_convert returns False for non-PDF files."""
        converter = OCRConverter()
        result = converter.can_convert(Path("any.docx"))
        assert result is False
    
    def test_init_with_custom_config(self):
        """Test OCRConverter initialization with custom config."""
        config = ConverterConfig(ocr_dpi=3, progress_interval=10)
        converter = OCRConverter(config)
        assert converter.config.ocr_dpi == 3
        assert converter.config.progress_interval == 10


class TestConverterFactory:
    """Tests for ConverterFactory class."""
    
    def test_create_returns_ocr_converter_when_force_ocr(self):
        """Test factory returns OCRConverter when force_ocr is True."""
        config = ConverterConfig(force_ocr=True)
        converter = ConverterFactory.create(Path("test.pdf"), config)
        assert isinstance(converter, OCRConverter)
    
    @patch('markdown_convert.converters.pdf_converter.PDFConverter.can_convert')
    def test_create_returns_pdf_converter_for_text_pdf(self, mock_can_convert):
        """Test factory returns PDFConverter for text-based PDFs."""
        mock_can_convert.return_value = True
        
        converter = ConverterFactory.create(Path("test.pdf"))
        assert isinstance(converter, PDFConverter)
    
    @patch('markdown_convert.converters.pdf_converter.PDFConverter.can_convert')
    def test_create_returns_ocr_converter_for_scanned_pdf(self, mock_can_convert):
        """Test factory returns OCRConverter for scanned PDFs."""
        mock_can_convert.return_value = False
        
        converter = ConverterFactory.create(Path("test.pdf"))
        assert isinstance(converter, OCRConverter)
    
    def test_create_pdf_converter(self):
        """Test create_pdf_converter returns PDFConverter."""
        converter = ConverterFactory.create_pdf_converter()
        assert isinstance(converter, PDFConverter)
    
    def test_create_ocr_converter(self):
        """Test create_ocr_converter returns OCRConverter."""
        converter = ConverterFactory.create_ocr_converter()
        assert isinstance(converter, OCRConverter)


class TestBaseConverter:
    """Tests for base converter functionality."""
    
    def test_convert_raises_error_for_nonexistent_file(self):
        """Test convert raises FileNotFoundError for non-existent files."""
        converter = PDFConverter()
        
        with pytest.raises(FileNotFoundError):
            converter.convert(Path("/nonexistent/file.pdf"))
