# PDF to Markdown Converter

A tool to convert PDF files to Markdown format with OCR support.

## Features

- Convert PDF files to Markdown format
- Automatic fallback to OCR for scanned documents
- Batch processing of multiple PDF files
- Support for recursive directory processing
- Control over output directory and page limits

## Usage

```bash
# Convert a single PDF file
python main.py path/to/file.pdf

# Convert multiple PDF files
python main.py file1.pdf file2.pdf file3.pdf

# Convert all PDFs in a directory
python main.py path/to/directory/

# Convert all PDFs in a directory and its subdirectories
python main.py path/to/directory/ --recursive

# Specify an output directory
python main.py path/to/file.pdf --output-dir path/to/output/

# Process only the first 10 pages of each PDF
python main.py path/to/file.pdf --max-pages 10

# Force using OCR even if text can be extracted directly
python main.py path/to/file.pdf --force-ocr

# Overwrite existing output files
python main.py path/to/file.pdf --overwrite
```

## Output Location

If no output directory is specified with `--output-dir`, the script will create a `markdown` directory in the same location as the PDF files and save the converted files there.

## Options

- `-o, --output-dir`: Specify output directory for markdown files
- `-m, --max-pages`: Maximum number of pages to process per PDF
- `--force-ocr`: Force using OCR even if text can be extracted directly
- `-r, --recursive`: Recursively process directories
- `--overwrite`: Overwrite existing output files (by default, existing files are skipped)

## Performance Notes

**Note:** Extracting valid PDFs with text content will perform great, while PDFs with images will take time to extract due to OCR processing requirements.

## Requirements

- Python 3.6+
- pymupdf4llm
- PyMuPDF (fitz)
- pytesseract
- Pillow
- Tesseract OCR installed on your system