"""Utility functions for file handling."""

import os
import glob
from pathlib import Path
from typing import List, Optional


def find_supported_files(paths: List[str], recursive: bool = False) -> List[Path]:
    """Find all supported files from given paths.

    Supported extensions: .pdf, .docx, .doc
    
    Args:
        paths: List of file paths, directory paths, or glob patterns.
        recursive: If True, search directories recursively.
        
    Returns:
        List of Path objects for found files, sorted and deduplicated.
    """
    found_files = []
    extensions = {'.pdf', '.docx', '.doc'}
    
    for path_str in paths:
        path = Path(path_str)
        
        if path.is_dir():
            # Directory: find all supported files
            # Optimized: single traversal instead of repeated globbing for each extension
            # Also skips common ignore directories to improve performance
            ignore_dirs = {'.git', '__pycache__', 'node_modules', 'venv', '.venv'}
            if recursive:
                for root, dirs, files in os.walk(path):
                    # Filter out ignored directories in-place
                    dirs[:] = [d for d in dirs if d not in ignore_dirs]
                    for file in files:
                        p = Path(root) / file
                        if p.suffix.lower() in extensions:
                            found_files.append(p)
            else:
                # Use scandir for better performance on non-recursive directory listing
                with os.scandir(path) as it:
                    for entry in it:
                        if entry.is_file():
                            p = Path(entry.path)
                            if p.suffix.lower() in extensions:
                                found_files.append(p)
        elif path.is_file() and path.suffix.lower() in extensions:
            # Direct supported file
            found_files.append(path)
        elif '*' in path_str or '?' in path_str:
            # Glob pattern
            for p in glob.glob(path_str):
                p_path = Path(p)
                if p_path.suffix.lower() in extensions:
                    found_files.append(p_path)
    
    # Remove duplicates and sort
    return sorted(set(found_files))


def get_output_path(input_path: Path, output_dir: Optional[Path] = None) -> Path:
    """Determine the output path for a converted markdown file.
    
    Args:
        input_path: Path to the input file.
        output_dir: Optional output directory. If None, creates 'markdown'
                   directory next to the input file.
                   
    Returns:
        Path object for the output markdown file.
    """
    # Get base filename without extension
    md_filename = input_path.stem + '.md'
    
    if output_dir:
        return output_dir / md_filename
    else:
        # Create markdown directory next to input file
        markdown_dir = input_path.parent / 'markdown'
        return markdown_dir / md_filename


def ensure_directory(path: Path) -> None:
    """Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path to ensure exists.
    """
    path.mkdir(parents=True, exist_ok=True)


def should_skip_conversion(output_path: Path, skip_existing: bool) -> bool:
    """Check if conversion should be skipped.
    
    Args:
        output_path: Path to the output file.
        skip_existing: If True, skip if output file exists.
        
    Returns:
        True if conversion should be skipped, False otherwise.
    """
    return skip_existing and output_path.exists()
