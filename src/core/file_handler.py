"""
File handling module for the Short Video Merger application.

Provides functionality for scanning folders, discovering video files,
and extracting video metadata.
"""

import os
import random
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Tuple
import logging

from src.core.config import SUPPORTED_VIDEO_FORMATS


logger = logging.getLogger(__name__)


@dataclass
class VideoInfo:
    """Information about a video file."""
    
    path: str
    filename: str
    size_bytes: int
    duration: Optional[float] = None  # Duration in seconds
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    codec: Optional[str] = None
    enabled: bool = True  # Whether to include in merge
    
    @property
    def size_mb(self) -> float:
        """Get file size in megabytes."""
        return self.size_bytes / (1024 * 1024)
    
    @property
    def resolution(self) -> str:
        """Get resolution as string."""
        if self.width and self.height:
            return f"{self.width}x{self.height}"
        return "Unknown"
    
    @property
    def duration_formatted(self) -> str:
        """Get duration as formatted string (MM:SS)."""
        if self.duration is None:
            return "Unknown"
        minutes = int(self.duration // 60)
        seconds = int(self.duration % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def __str__(self) -> str:
        return f"{self.filename} ({self.resolution}, {self.duration_formatted})"


class FileHandler:
    """Handles file operations for video discovery and validation."""
    
    def __init__(self, folder_path: Optional[str] = None):
        """
        Initialize the file handler.
        
        Args:
            folder_path: Optional path to the video folder.
        """
        self._folder_path: Optional[Path] = None
        self._videos: List[VideoInfo] = []
        self._moviepy_available = False
        self._moviepy_v2 = False
        
        if folder_path:
            self.set_folder(folder_path)
        
        # Try to import moviepy for metadata extraction (supports both 1.x and 2.x)
        try:
            from moviepy import VideoFileClip
            self._moviepy_available = True
            self._moviepy_v2 = True
        except ImportError:
            try:
                from moviepy.editor import VideoFileClip
                self._moviepy_available = True
            except ImportError:
                logger.warning("moviepy not available. Video metadata will be limited.")
    
    def set_folder(self, folder_path: str) -> bool:
        """
        Set the folder to scan for videos.
        
        Args:
            folder_path: Path to the folder.
            
        Returns:
            True if folder is valid, False otherwise.
        """
        path = Path(folder_path)
        if not path.is_dir():
            logger.error(f"Invalid folder path: {folder_path}")
            return False
        
        self._folder_path = path
        self._videos = []
        return True
    
    @property
    def folder_path(self) -> Optional[str]:
        """Get the current folder path."""
        return str(self._folder_path) if self._folder_path else None
    
    @property
    def videos(self) -> List[VideoInfo]:
        """Get list of discovered videos."""
        return self._videos.copy()
    
    @property
    def enabled_videos(self) -> List[VideoInfo]:
        """Get list of enabled videos."""
        return [v for v in self._videos if v.enabled]
    
    def scan_folder(self, recursive: bool = False) -> List[VideoInfo]:
        """
        Scan the folder for video files.
        
        Args:
            recursive: Whether to scan subdirectories.
            
        Returns:
            List of VideoInfo objects for discovered videos.
        """
        if not self._folder_path:
            logger.error("No folder path set")
            return []
        
        self._videos = []
        pattern = '**/*' if recursive else '*'
        
        for file_path in self._folder_path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_VIDEO_FORMATS:
                video_info = self._create_video_info(file_path)
                if video_info:
                    self._videos.append(video_info)
        
        # Sort by filename
        self._videos.sort(key=lambda v: v.filename.lower())
        
        logger.info(f"Found {len(self._videos)} video files in {self._folder_path}")
        return self._videos
    
    def _create_video_info(self, file_path: Path) -> Optional[VideoInfo]:
        """
        Create a VideoInfo object for a file.
        
        Args:
            file_path: Path to the video file.
            
        Returns:
            VideoInfo object or None if file is invalid.
        """
        try:
            stat = file_path.stat()
            video_info = VideoInfo(
                path=str(file_path),
                filename=file_path.name,
                size_bytes=stat.st_size
            )
            
            # Try to extract metadata using moviepy
            if self._moviepy_available:
                self._extract_metadata(video_info)
            
            return video_info
            
        except OSError as e:
            logger.warning(f"Could not read file {file_path}: {e}")
            return None
    
    def _extract_metadata(self, video_info: VideoInfo) -> None:
        """
        Extract video metadata using moviepy.
        
        Args:
            video_info: VideoInfo object to update with metadata.
        """
        try:
            # Import based on moviepy version
            if self._moviepy_v2:
                from moviepy import VideoFileClip
            else:
                from moviepy.editor import VideoFileClip
            
            with VideoFileClip(video_info.path) as clip:
                video_info.duration = clip.duration
                video_info.width = clip.w
                video_info.height = clip.h
                video_info.fps = clip.fps
                
        except Exception as e:
            logger.debug(f"Could not extract metadata from {video_info.filename}: {e}")
    
    def get_random_selection(
        self,
        count: int,
        seed: Optional[int] = None,
        only_enabled: bool = True
    ) -> List[VideoInfo]:
        """
        Get a random selection of videos.
        
        Args:
            count: Number of videos to select.
            seed: Random seed for reproducibility.
            only_enabled: Whether to only select from enabled videos.
            
        Returns:
            List of randomly selected VideoInfo objects.
        """
        source = self.enabled_videos if only_enabled else self._videos
        
        if count <= 0 or count >= len(source):
            return source.copy()
        
        # Use a local random instance to avoid affecting global random state
        rng = random.Random(seed)
        return rng.sample(source, count)
    
    def enable_video(self, filename: str, enabled: bool = True) -> bool:
        """
        Enable or disable a video for merging.
        
        Args:
            filename: Name of the video file.
            enabled: Whether to enable the video.
            
        Returns:
            True if video was found, False otherwise.
        """
        for video in self._videos:
            if video.filename == filename:
                video.enabled = enabled
                return True
        return False
    
    def enable_all(self, enabled: bool = True) -> None:
        """
        Enable or disable all videos.
        
        Args:
            enabled: Whether to enable all videos.
        """
        for video in self._videos:
            video.enabled = enabled
    
    def get_video_by_filename(self, filename: str) -> Optional[VideoInfo]:
        """
        Get video info by filename.
        
        Args:
            filename: Name of the video file.
            
        Returns:
            VideoInfo object or None if not found.
        """
        for video in self._videos:
            if video.filename == filename:
                return video
        return None
    
    def get_total_duration(self, videos: Optional[List[VideoInfo]] = None) -> float:
        """
        Calculate total duration of videos.
        
        Args:
            videos: List of videos to sum. Uses all enabled if None.
            
        Returns:
            Total duration in seconds.
        """
        if videos is None:
            videos = self.enabled_videos
        
        total = 0.0
        for video in videos:
            if video.duration:
                total += video.duration
        return total
    
    def validate_videos(self, videos: List[VideoInfo]) -> Tuple[bool, List[str]]:
        """
        Validate that all videos in a list exist and are readable.
        
        Args:
            videos: List of VideoInfo objects to validate.
            
        Returns:
            Tuple of (all_valid, list_of_error_messages)
        """
        errors = []
        
        for video in videos:
            path = Path(video.path)
            if not path.exists():
                errors.append(f"File not found: {video.filename}")
            elif not os.access(path, os.R_OK):
                errors.append(f"File not readable: {video.filename}")
        
        return len(errors) == 0, errors
