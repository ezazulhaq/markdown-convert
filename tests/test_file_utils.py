import pytest
import os
import shutil
from pathlib import Path
from markdown_convert.utils.file_utils import find_supported_files

@pytest.fixture
def test_dir(tmp_path):
    """Setup a temporary directory with various files."""
    d = tmp_path / "test_data"
    d.mkdir()

    # Create supported files
    (d / "file1.pdf").touch()
    (d / "file2.docx").touch()
    (d / "file3.doc").touch()

    # Create unsupported files
    (d / "file4.txt").touch()
    (d / "file5.jpg").touch()

    # Create a subdirectory with more files
    sub = d / "subdir"
    sub.mkdir()
    (sub / "subfile1.pdf").touch()
    (sub / "subfile2.txt").touch()

    return d

def test_find_supported_files_non_recursive(test_dir):
    """Test finding files in a directory without recursion."""
    files = find_supported_files([str(test_dir)], recursive=False)

    filenames = {p.name for p in files}
    assert filenames == {"file1.pdf", "file2.docx", "file3.doc"}
    assert all(isinstance(p, Path) for p in files)

def test_find_supported_files_recursive(test_dir):
    """Test finding files in a directory with recursion."""
    files = find_supported_files([str(test_dir)], recursive=True)

    filenames = {p.name for p in files}
    assert filenames == {"file1.pdf", "file2.docx", "file3.doc", "subfile1.pdf"}

def test_find_supported_files_direct_path(test_dir):
    """Test finding a specific file by its path."""
    pdf_path = test_dir / "file1.pdf"
    files = find_supported_files([str(pdf_path)])

    assert len(files) == 1
    assert files[0].name == "file1.pdf"

def test_find_supported_files_glob_pattern(test_dir):
    """Test finding files using a glob pattern."""
    pattern = str(test_dir / "*.pdf")
    files = find_supported_files([pattern])

    assert len(files) == 1
    assert files[0].name == "file1.pdf"

def test_find_supported_files_multiple_paths(test_dir):
    """Test finding files from multiple input paths."""
    pdf_path = test_dir / "file1.pdf"
    docx_path = test_dir / "file2.docx"

    files = find_supported_files([str(pdf_path), str(docx_path)])

    filenames = {p.name for p in files}
    assert filenames == {"file1.pdf", "file2.docx"}

def test_find_supported_files_deduplication(test_dir):
    """Test that duplicate paths are removed."""
    pdf_path = test_dir / "file1.pdf"

    # Pass the same path twice and also via the directory
    files = find_supported_files([str(pdf_path), str(pdf_path), str(test_dir)], recursive=False)

    filenames = [p.name for p in files]
    assert filenames.count("file1.pdf") == 1
    assert "file2.docx" in filenames
    assert "file3.doc" in filenames
