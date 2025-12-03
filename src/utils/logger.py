"""
Logger utility for the Short Video Merger application.

Provides centralized logging configuration and utilities.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


def setup_logger(
    name: str = "short_video_merger",
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    verbose: bool = False
) -> logging.Logger:
    """
    Set up and configure a logger instance.
    
    Args:
        name: Logger name.
        level: Logging level (default: INFO).
        log_file: Optional file path to write logs.
        verbose: If True, set level to DEBUG.
        
    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Set level
    if verbose:
        level = logging.DEBUG
    logger.setLevel(level)
    
    # Create formatters
    console_format = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger


def get_default_log_file() -> str:
    """Get the default log file path."""
    log_dir = Path.home() / '.local' / 'share' / 'short-video-merger' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return str(log_dir / f'merger_{timestamp}.log')


class ProgressCallback:
    """
    Callback class for reporting progress during operations.
    
    This can be subclassed or used with callback functions for
    both GUI and CLI progress reporting.
    """
    
    def __init__(self, callback=None):
        """
        Initialize the progress callback.
        
        Args:
            callback: Optional callable that receives (progress, message)
        """
        self._callback = callback
        self._progress = 0.0
        self._message = ""
        self._cancelled = False
    
    def update(self, progress: float, message: str = "") -> None:
        """
        Update progress status.
        
        Args:
            progress: Progress value between 0.0 and 1.0
            message: Optional status message
        """
        self._progress = min(1.0, max(0.0, progress))
        self._message = message
        if self._callback:
            self._callback(self._progress, self._message)
    
    @property
    def progress(self) -> float:
        """Get current progress value."""
        return self._progress
    
    @property
    def message(self) -> str:
        """Get current status message."""
        return self._message
    
    def cancel(self) -> None:
        """Signal cancellation of the operation."""
        self._cancelled = True
    
    @property
    def is_cancelled(self) -> bool:
        """Check if operation was cancelled."""
        return self._cancelled
