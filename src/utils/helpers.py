"""
Utility functions for the Age Detection App.
"""
import os
import datetime
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

def validate_face_detection(analysis_result: Dict[str, Any]) -> bool:
    """
    Validate if a face was detected in the analysis result.
    
    Args:
        analysis_result: The analysis result from deepface
        
    Returns:
        bool: True if a face was detected, False otherwise
    """
    # Check if the analysis result contains the expected keys
    return (analysis_result is not None and 
            isinstance(analysis_result, dict) and 
            'age' in analysis_result)

def get_default_export_path() -> Path:
    """
    Get the default path for exporting results.
    
    Returns:
        Path: The default export path
    """
    documents_dir = Path.home() / "Documents"
    if not documents_dir.exists():
        documents_dir = Path.home()
    
    export_dir = documents_dir / "AgeDetectionExports"
    export_dir.mkdir(exist_ok=True)
    
    return export_dir

def generate_timestamp_filename(prefix: str, extension: str) -> str:
    """
    Generate a filename with a timestamp.
    
    Args:
        prefix: The prefix for the filename
        extension: The file extension
        
    Returns:
        str: The generated filename
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"

def format_confidence(confidence: float) -> str:
    """
    Format a confidence value as a percentage string.
    
    Args:
        confidence: The confidence value (0-1)
        
    Returns:
        str: The formatted confidence string
    """
    return f"{confidence*100:.1f}%"

def ensure_directory_exists(directory_path: Path) -> None:
    """
    Ensure that a directory exists, create it if it doesn't.
    
    Args:
        directory_path: The directory path to check/create
    """
    if not directory_path.exists():
        directory_path.mkdir(parents=True)

def get_supported_image_extensions() -> List[str]:
    """
    Get a list of supported image file extensions.
    
    Returns:
        List[str]: List of supported extensions
    """
    return ['.jpg', '.jpeg', '.png', '.bmp']

def is_supported_image(file_path: Path) -> bool:
    """
    Check if a file is a supported image type.
    
    Args:
        file_path: The file path to check
        
    Returns:
        bool: True if the file is a supported image, False otherwise
    """
    return file_path.suffix.lower() in get_supported_image_extensions()
