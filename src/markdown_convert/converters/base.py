"""Base converter class defining the converter interface."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from ..config import ConverterConfig
from ..utils import get_output_path, ensure_directory, should_skip_conversion


class BaseConverter(ABC):
    """Abstract base class for file to Markdown converters.
    
    This class defines the interface that all converters must implement
    and provides common functionality for validation and file handling.
    """
    
    def __init__(self, config: Optional[ConverterConfig] = None):
        """Initialize the converter.
        
        Args:
            config: Converter configuration. If None, uses default config.
        """
        self.config = config or ConverterConfig.default()
    
    def convert(self, file_path: Path) -> Optional[Path]:
        """Convert a file to Markdown.
        
        Args:
            file_path: Path to the file to convert.
            
        Returns:
            Path to the output markdown file if successful, None if skipped.
            
        Raises:
            FileNotFoundError: If the file doesn't exist.
            ConversionError: If conversion fails.
        """
        # Validate input
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(str(file_path))
        
        # Determine output path
        output_path = get_output_path(file_path, self.config.output_dir)
        
        # Check if we should skip
        if should_skip_conversion(output_path, self.config.skip_existing):
            print(f"Output file already exists: {output_path}")
            print("Skipping conversion (use overwrite option to force)")
            return None
        
        # Ensure output directory exists
        ensure_directory(output_path.parent)
        
        # Perform the actual conversion (implemented by subclasses)
        markdown_text = self._convert_to_markdown(file_path)
        
        # Save the result
        if markdown_text:
            output_path.write_text(markdown_text, encoding='utf-8')
            print(f"Saved markdown to {output_path.absolute()}")
            return output_path
        else:
            print("No text extracted, not saving empty file")
            return None
    
    @abstractmethod
    def _convert_to_markdown(self, file_path: Path) -> str:
        """Convert file to markdown text.
        
        This method must be implemented by subclasses to perform
        the actual conversion logic.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            Markdown text content.
            
        Raises:
            ConversionError: If conversion fails.
        """
        pass
    
    @abstractmethod
    def can_convert(self, file_path: Path) -> bool:
        """Check if this converter can handle the given file.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            True if this converter can handle the file, False otherwise.
        """
        pass
