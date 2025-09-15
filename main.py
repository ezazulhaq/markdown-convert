import pymupdf4llm
import fitz  # PyMuPDF
import pathlib
import os
import pytesseract
from PIL import Image
import argparse
import glob
import time

# Function to extract text using OCR
def extract_text_with_ocr(pdf_path, max_pages=None):
    doc = fitz.open(pdf_path)
    text = ""
    
    # Determine number of pages to process
    num_pages = len(doc) if max_pages is None else min(max_pages, len(doc))
    print(f"Processing {num_pages} pages with OCR...")
    
    for page_num in range(num_pages):
        # Get the page
        page = doc[page_num]
        
        # Render page to an image (higher resolution for better OCR)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        
        # Convert to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Use OCR to extract text
        page_text = pytesseract.image_to_string(img)
        
        # Add page number and text to result
        text += f"\n\n# Page {page_num + 1}\n\n{page_text}"
        
        # Print progress
        if page_num % 5 == 0 or page_num == num_pages - 1:
            print(f"Processed page {page_num + 1}/{num_pages}")
    
    doc.close()
    return text

# Function to process a single PDF file
def process_pdf(pdf_path, output_dir=None, max_pages=None, force_ocr=False, skip_existing=True):
    print(f"\nProcessing: {pdf_path}")
    print(f"File exists: {os.path.exists(pdf_path)}")
    
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        return False
    
    try:
        # Get the base filename without extension
        pdf_basename = os.path.basename(pdf_path)
        pdf_name = os.path.splitext(pdf_basename)[0]
        
        # Determine output path
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{pdf_name}.md")
        else:
            # Create a markdown directory in the same location as the PDF
            pdf_dir = os.path.dirname(pdf_path)
            markdown_dir = os.path.join(pdf_dir, "markdown")
            os.makedirs(markdown_dir, exist_ok=True)
            output_path = os.path.join(markdown_dir, f"{pdf_name}.md")
            
        # Check if output file already exists
        if skip_existing and os.path.exists(output_path):
            print(f"Output file already exists: {output_path}")
            print("Skipping conversion (use --overwrite to force conversion)")
            return True
        
        # First check if we can extract text directly with PyMuPDF
        doc = fitz.open(pdf_path)
        print(f"PDF has {len(doc)} pages")
        
        # Check if the first page has text
        page = doc[0]
        text = page.get_text()
        print(f"First page text length: {len(text)}")
        
        # Try with pymupdf4llm if not forcing OCR
        md_text = ""
        if not force_ocr:
            print("Trying with pymupdf4llm...")
            md_text = pymupdf4llm.to_markdown(pdf_path)
            print(f"Markdown text length: {len(md_text)}")
        
        # If both methods failed or force_ocr is True, use OCR
        if force_ocr or (not md_text and not text):
            print("Using OCR to extract text...")
            md_text = extract_text_with_ocr(pdf_path, max_pages=max_pages)
            print(f"OCR extracted text length: {len(md_text)}")
        
        # Save the Markdown to a file
        if md_text:
            pathlib.Path(output_path).write_bytes(md_text.encode())
            print(f"Saved markdown to {os.path.abspath(output_path)}")
            return True
        else:
            print("No text extracted, not saving empty file")
            return False
            
        doc.close()
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return False

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Convert PDF files to Markdown with OCR support')
    parser.add_argument('input', nargs='+', help='Input PDF file(s) or directory')
    parser.add_argument('-o', '--output-dir', help='Output directory for markdown files')
    parser.add_argument('-m', '--max-pages', type=int, help='Maximum number of pages to process')
    parser.add_argument('--force-ocr', action='store_true', help='Force using OCR even if text can be extracted directly')
    parser.add_argument('-r', '--recursive', action='store_true', help='Recursively process directories')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing output files')
    
    args = parser.parse_args()
    
    # Collect all PDF files to process
    pdf_files = []
    for path in args.input:
        if os.path.isdir(path):
            # If path is a directory, find all PDF files
            if args.recursive:
                pdf_files.extend(glob.glob(os.path.join(path, '**', '*.pdf'), recursive=True))
            else:
                pdf_files.extend(glob.glob(os.path.join(path, '*.pdf')))
        elif os.path.isfile(path) and path.lower().endswith('.pdf'):
            # If path is a PDF file
            pdf_files.append(path)
        elif '*' in path or '?' in path:
            # If path contains wildcards
            pdf_files.extend(glob.glob(path))
    
    # Remove duplicates and sort
    pdf_files = sorted(set(pdf_files))
    
    if not pdf_files:
        print("No PDF files found!")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    # Process each PDF file
    start_time = time.time()
    successful = 0
    
    for i, pdf_path in enumerate(pdf_files):
        print(f"\n[{i+1}/{len(pdf_files)}] Processing: {pdf_path}")
        if process_pdf(pdf_path, args.output_dir, args.max_pages, args.force_ocr, not args.overwrite):
            successful += 1
    
    elapsed_time = time.time() - start_time
    print(f"\nProcessed {successful}/{len(pdf_files)} files successfully in {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()
