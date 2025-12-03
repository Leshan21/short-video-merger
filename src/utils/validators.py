"""
Input validation utilities for the Short Video Merger application.

Provides validation functions for paths, video files, and configuration options.
"""

import os
from pathlib import Path
from typing import Tuple, Optional
from src.core.config import SUPPORTED_VIDEO_FORMATS, OUTPUT_FORMATS, TRANSITION_EFFECTS


def validate_folder_path(path: str) -> Tuple[bool, str]:
    """
    Validate that a folder path exists and is readable.
    
    Args:
        path: Path to validate.
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not path:
        return False, "Folder path is required"
    
    folder = Path(path)
    
    if not folder.exists():
        return False, f"Folder does not exist: {path}"
    
    if not folder.is_dir():
        return False, f"Path is not a directory: {path}"
    
    if not os.access(folder, os.R_OK):
        return False, f"Folder is not readable: {path}"
    
    return True, ""


def validate_output_path(path: str, check_parent: bool = True) -> Tuple[bool, str]:
    """
    Validate that an output path is valid and writable.
    
    Args:
        path: Output file path to validate.
        check_parent: Whether to check if parent directory exists.
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not path:
        return False, "Output path is required"
    
    output = Path(path)
    
    if check_parent:
        parent = output.parent
        if not parent.exists():
            return False, f"Output directory does not exist: {parent}"
        
        if not os.access(parent, os.W_OK):
            return False, f"Output directory is not writable: {parent}"
    
    # Check if file exists and is writable (if it exists)
    if output.exists() and not os.access(output, os.W_OK):
        return False, f"Cannot overwrite file: {path}"
    
    return True, ""


def validate_video_file(path: str) -> Tuple[bool, str]:
    """
    Validate that a file is a supported video format.
    
    Args:
        path: Path to the video file.
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not path:
        return False, "File path is required"
    
    video_path = Path(path)
    
    if not video_path.exists():
        return False, f"File does not exist: {path}"
    
    if not video_path.is_file():
        return False, f"Path is not a file: {path}"
    
    if video_path.suffix.lower() not in SUPPORTED_VIDEO_FORMATS:
        return False, f"Unsupported video format: {video_path.suffix}"
    
    return True, ""


def validate_video_count(count: int, total_available: int) -> Tuple[bool, str]:
    """
    Validate video count for merging.
    
    Args:
        count: Requested number of videos.
        total_available: Total available videos.
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if count < 0:
        return False, "Video count cannot be negative"
    
    if count > total_available:
        return False, f"Requested {count} videos but only {total_available} available"
    
    return True, ""


def validate_transition_duration(duration: float) -> Tuple[bool, str]:
    """
    Validate transition duration.
    
    Args:
        duration: Duration in seconds.
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if duration < 0:
        return False, "Transition duration cannot be negative"
    
    if duration > 3.0:
        return False, "Transition duration cannot exceed 3 seconds"
    
    return True, ""


def validate_output_format(format_str: str) -> Tuple[bool, str]:
    """
    Validate output format.
    
    Args:
        format_str: Format string (e.g., 'mp4', 'avi').
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    format_lower = format_str.lower()
    if format_lower not in OUTPUT_FORMATS:
        valid_formats = ', '.join(OUTPUT_FORMATS)
        return False, f"Invalid format '{format_str}'. Valid formats: {valid_formats}"
    
    return True, ""


def validate_transition_effect(effect: str) -> Tuple[bool, str]:
    """
    Validate transition effect.
    
    Args:
        effect: Transition effect name.
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    effect_lower = effect.lower()
    if effect_lower not in TRANSITION_EFFECTS:
        valid_effects = ', '.join(TRANSITION_EFFECTS)
        return False, f"Invalid transition '{effect}'. Valid effects: {valid_effects}"
    
    return True, ""


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing/replacing invalid characters.
    
    Args:
        filename: Original filename.
        
    Returns:
        Sanitized filename safe for the filesystem.
    """
    # Characters not allowed in filenames on various systems
    invalid_chars = '<>:"/\\|?*'
    
    result = filename
    for char in invalid_chars:
        result = result.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    result = result.strip('. ')
    
    # Ensure the filename is not empty
    if not result:
        result = "output"
    
    return result
