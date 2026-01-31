"""Tests for Docx converter."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from markdown_convert.converters.docx_converter import DocxConverter
from markdown_convert.config import ConverterConfig
from markdown_convert.exceptions import ConversionError


class TestDocxConverter:
    @pytest.fixture
    def converter(self):
        return DocxConverter()

    def test_init_with_default_config(self, converter):
        assert isinstance(converter.config, ConverterConfig)

    def test_can_convert_returns_true_for_docx(self, converter):
        assert converter.can_convert(Path("test.docx")) is True
        assert converter.can_convert(Path("TEST.DOCX")) is True

    def test_can_convert_returns_true_for_doc(self, converter):
        assert converter.can_convert(Path("test.doc")) is True
        assert converter.can_convert(Path("TEST.DOC")) is True

    def test_can_convert_returns_false_for_others(self, converter):
        assert converter.can_convert(Path("test.pdf")) is False
        assert converter.can_convert(Path("test.txt")) is False

    @patch("mammoth.convert_to_html")
    @patch("builtins.open", new_callable=mock_open)
    def test_convert_success(self, mock_file, mock_mammoth, converter):
        # Setup mocks
        mock_result = Mock()
        mock_result.value = "<h1>Title</h1><p>Text</p>"
        mock_result.messages = []
        mock_mammoth.return_value = mock_result

        # Test
        result = converter._convert_to_markdown(Path("test.docx"))

        # Verify
        assert "# Title" in result
        assert "Text" in result
        mock_mammoth.assert_called_once()

    @patch("mammoth.convert_to_html")
    @patch("builtins.open", new_callable=mock_open)
    def test_convert_handles_warnings(self, mock_file, mock_mammoth, converter, capsys):
        # Setup mocks with warnings
        mock_result = Mock()
        mock_result.value = "<p>Text</p>"
        mock_result.messages = ["Warning 1"]
        mock_mammoth.return_value = mock_result

        # Test
        converter._convert_to_markdown(Path("test.docx"))

        # Verify warning printed
        captured = capsys.readouterr()
        assert "Docx warning: Warning 1" in captured.out

    def test_convert_raises_error_on_failure(self, converter):
        with patch("builtins.open", side_effect=Exception("Read error")):
            with pytest.raises(ConversionError) as exc:
                converter._convert_to_markdown(Path("test.docx"))
            assert "Docx conversion failed" in str(exc.value)

    def test_convert_raises_friendly_error_for_binary_doc(self, converter):
        with patch("builtins.open", new_callable=mock_open):
            with patch("mammoth.convert_to_html", side_effect=Exception("File is not a zip file")):
                with pytest.raises(ConversionError) as exc:
                    converter._convert_to_markdown(Path("test.doc"))
                assert "Legacy binary .doc files are not supported" in str(exc.value)

    @patch("mammoth.convert_to_html")
    @patch("builtins.open", new_callable=mock_open)
    def test_convert_strips_images(self, mock_file, mock_mammoth, converter):
        # Setup mocks with HTML containing images
        mock_result = Mock()
        mock_result.value = '<h1>Title</h1><p>Text</p><img src="data:image/jpeg;base64,/9j/4AAQSkZJRg..." /><p>More text</p>'
        mock_result.messages = []
        mock_mammoth.return_value = mock_result

        # Test
        result = converter._convert_to_markdown(Path("test.docx"))

        # Verify images are stripped
        assert "# Title" in result
        assert "Text" in result
        assert "More text" in result
        assert "data:image" not in result
        assert "![" not in result  # No markdown images

    @patch("pytesseract.image_to_string")
    @patch("mammoth.convert_to_html")
    @patch("builtins.open", new_callable=mock_open)
    def test_convert_uses_ocr_when_no_text(self, mock_file, mock_mammoth, mock_ocr, converter):
        # Setup mocks with HTML containing only images (no text)
        mock_result = Mock()
        mock_result.value = '<img src="data:image/jpeg;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==" />'
        mock_result.messages = []
        mock_mammoth.return_value = mock_result
        
        # Mock OCR output
        mock_ocr.return_value = "Text extracted from image via OCR"
        
        # Test
        result = converter._convert_to_markdown(Path("scanned.docx"))
        
        # Verify OCR was called
        assert mock_ocr.called
        assert "Text extracted from image via OCR" in result
        assert "# Image 1" in result

