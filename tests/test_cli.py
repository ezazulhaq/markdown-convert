"""Tests for CLI functionality."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

from markdown_convert.cli import create_parser, main, process_files
from markdown_convert.config import ConverterConfig


class TestCLIParser:
    """Tests for CLI argument parser."""
    
    def test_parser_accepts_single_file(self):
        """Test parser accepts single file argument."""
        parser = create_parser()
        args = parser.parse_args(['test.pdf'])
        assert args.input == ['test.pdf']

    def test_parser_accepts_docx_file(self):
        """Test parser accepts docx file argument."""
        parser = create_parser()
        args = parser.parse_args(['test.docx'])
        assert args.input == ['test.docx']
    
    def test_parser_accepts_multiple_files(self):
        """Test parser accepts multiple file arguments."""
        parser = create_parser()
        args = parser.parse_args(['file1.pdf', 'file2.pdf'])
        assert args.input == ['file1.pdf', 'file2.pdf']
    
    def test_parser_accepts_output_dir(self):
        """Test parser accepts output directory option."""
        parser = create_parser()
        args = parser.parse_args(['test.pdf', '-o', 'output/'])
        assert args.output_dir == Path('output/')
    
    def test_parser_accepts_max_pages(self):
        """Test parser accepts max-pages option."""
        parser = create_parser()
        args = parser.parse_args(['test.pdf', '--max-pages', '10'])
        assert args.max_pages == 10
    
    def test_parser_accepts_force_ocr(self):
        """Test parser accepts force-ocr flag."""
        parser = create_parser()
        args = parser.parse_args(['test.pdf', '--force-ocr'])
        assert args.force_ocr is True
    
    def test_parser_accepts_recursive(self):
        """Test parser accepts recursive flag."""
        parser = create_parser()
        args = parser.parse_args(['dir/', '-r'])
        assert args.recursive is True
    
    def test_parser_accepts_overwrite(self):
        """Test parser accepts overwrite flag."""
        parser = create_parser()
        args = parser.parse_args(['test.pdf', '--overwrite'])
        assert args.overwrite is True


class TestCLIMain:
    """Tests for CLI main function."""
    
    @patch('markdown_convert.cli.find_supported_files')
    def test_main_returns_error_when_no_files_found(self, mock_find):
        """Test main returns error code when no supported files found."""
        mock_find.return_value = []
        
        exit_code = main(['test.pdf'])
        assert exit_code == 1
    
    @patch('markdown_convert.cli.process_files')
    @patch('markdown_convert.cli.find_supported_files')
    def test_main_returns_success_when_files_processed(self, mock_find, mock_process):
        """Test main returns success code when files are processed."""
        mock_find.return_value = [Path('test.pdf')]
        mock_process.return_value = (1, 1)  # 1 successful, 1 total
        
        exit_code = main(['test.pdf'])
        assert exit_code == 0
    
    @patch('markdown_convert.cli.process_files')
    @patch('markdown_convert.cli.find_supported_files')
    def test_main_returns_error_when_no_files_successful(self, mock_find, mock_process):
        """Test main returns error code when no files are successfully processed."""
        mock_find.return_value = [Path('test.pdf')]
        mock_process.return_value = (0, 1)  # 0 successful, 1 total
        
        exit_code = main(['test.pdf'])
        assert exit_code == 1


class TestProcessFiles:
    """Tests for process_files function."""
    
    @patch('markdown_convert.cli.ConverterFactory.create')
    def test_process_files_handles_conversion_errors(self, mock_create):
        """Test process_files handles conversion errors gracefully."""
        # Mock converter that raises an error
        mock_converter = MagicMock()
        mock_converter.convert.side_effect = Exception("Test error")
        mock_create.return_value = mock_converter
        
        config = ConverterConfig()
        pdf_files = [Path('test.pdf')]
        
        successful, total = process_files(pdf_files, config)
        
        assert successful == 0
        assert total == 1
