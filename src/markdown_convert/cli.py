"""Command-line interface for markdown-convert."""

import argparse
import sys
import time
from pathlib import Path
from typing import List, Optional

from .config import ConverterConfig
from .converters import ConverterFactory
from .utils import find_supported_files
from .exceptions import MarkdownConvertError


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.
    
    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog='smart-file2md',
        description='Convert PDF, Docx, and Doc files to Markdown with OCR support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert a single file (PDF, Docx, Doc)
  smart-file2md document.pdf
  smart-file2md document.docx
  
  # Convert multiple files
  smart-file2md file1.pdf file2.docx
  
  # Convert all supported files in a directory
  smart-file2md /path/to/files/
  
  # Convert with custom output directory
  smart-file2md document.pdf -o output/
  
  # Force OCR for all PDF files
  smart-file2md document.pdf --force-ocr
  
  # Process only first 10 pages (PDF only)
  smart-file2md document.pdf --max-pages 10
        """
    )
    
    parser.add_argument(
        'input',
        nargs='+',
        help='Input file(s) or directory (PDF, Docx, Doc)'
    )
    
    parser.add_argument(
        '-o', '--output-dir',
        type=Path,
        help='Output directory for markdown files'
    )
    
    parser.add_argument(
        '-m', '--max-pages',
        type=int,
        help='Maximum number of pages to process per PDF'
    )
    
    parser.add_argument(
        '--force-ocr',
        action='store_true',
        help='Force using OCR even if text can be extracted directly (PDF only)'
    )
    
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Recursively process directories'
    )
    
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing output files (default: skip existing)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    return parser


def process_files(files: List[Path], config: ConverterConfig) -> dict:
    """Process a list of files.
    
    Args:
        files: List of file paths to process.
        config: Converter configuration.
        
    Returns:
        Dictionary with 'converted', 'skipped', 'failed', and 'total' counts.
    """
    converted = 0
    skipped = 0
    failed = 0
    total = len(files)
    
    for i, file_path in enumerate(files, 1):
        print(f"\n[{i}/{total}] Processing: {file_path}")
        
        try:
            # Create appropriate converter
            converter = ConverterFactory.create(file_path, config)
            
            # Convert the file
            result = converter.convert(file_path)
            
            if result:
                converted += 1
            else:
                skipped += 1
                
        except MarkdownConvertError as e:
            print(f"Error: {e}")
            failed += 1
        except Exception as e:
            print(f"Unexpected error: {e}")
            failed += 1
    
    return {
        'converted': converted,
        'skipped': skipped,
        'failed': failed,
        'total': total
    }


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI.
    
    Args:
        argv: Command-line arguments. If None, uses sys.argv.
        
    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = create_parser()
    args = parser.parse_args(argv)
    
    try:
        # Find all supported files
        files = find_supported_files(args.input, recursive=args.recursive)
        
        if not files:
            print("No supported files found (PDF, Docx)!")
            return 1
        
        print(f"Found {len(files)} file(s) to process")
        
        # Create configuration
        config = ConverterConfig(
            output_dir=args.output_dir,
            max_pages=args.max_pages,
            force_ocr=args.force_ocr,
            skip_existing=not args.overwrite,
        )
        
        # Process files
        start_time = time.time()
        results = process_files(files, config)
        elapsed_time = time.time() - start_time
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"Conversion Summary:")
        print(f"  Converted: {results['converted']}/{results['total']}")
        if results['skipped'] > 0:
            print(f"  Skipped:   {results['skipped']} (already exist)")
        if results['failed'] > 0:
            print(f"  Failed:    {results['failed']}")
        print(f"Time elapsed: {elapsed_time:.2f} seconds")
        print(f"{'='*60}")
        
        return 0 if results['converted'] > 0 or results['skipped'] > 0 else 1
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 130
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
