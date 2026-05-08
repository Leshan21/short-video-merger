"""
Configuration management for the Short Video Merger application.

This module provides configuration handling for both GUI and CLI modes,
including saving/loading configuration presets.
"""

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, List
import os


# Supported video formats for input files
# These formats are commonly supported by moviepy/ffmpeg.
# Note: Actual playback depends on having appropriate codecs installed.
# Formats with asterisk (*) may require additional codec support.
SUPPORTED_VIDEO_FORMATS = {
    '.mp4',   # MPEG-4 Part 14 - widely supported
    '.avi',   # Audio Video Interleave - legacy but common
    '.mov',   # QuickTime File Format
    '.mkv',   # Matroska Video - container format
    '.webm',  # WebM - open web video format
    '.flv',   # Flash Video - legacy format *
    '.wmv',   # Windows Media Video *
    '.m4v',   # iTunes Video File Format
}

# Supported output formats for merged videos
OUTPUT_FORMATS = ['mp4', 'avi', 'mov', 'mkv']

# Transition effects available for video merging
TRANSITION_EFFECTS = ['none', 'fade', 'dissolve', 'crossfade']

# Resolution handling options when merging videos with different resolutions
RESOLUTION_OPTIONS = ['keep', 'resize', 'crop', 'pad']


@dataclass
class MergeConfig:
    """Configuration settings for video merging operations."""
    
    input_folder: str = ""
    output_path: str = ""
    video_count: int = 0  # 0 means all videos
    output_format: str = "mp4"
    transition: str = "none"
    transition_duration: float = 1.0
    resolution_mode: str = "keep"
    normalize_audio: bool = False
    random_seed: Optional[int] = None
    selected_videos: List[str] = field(default_factory=list)
    
    def validate(self) -> List[str]:
        """
        Validate configuration settings.
        
        Returns:
            List of validation error messages. Empty if valid.
        """
        errors = []
        
        if not self.input_folder:
            errors.append("Input folder is required")
        elif not Path(self.input_folder).is_dir():
            errors.append(f"Input folder does not exist: {self.input_folder}")
            
        if not self.output_path:
            errors.append("Output path is required")
        else:
            output_dir = Path(self.output_path).parent
            if not output_dir.exists():
                errors.append(f"Output directory does not exist: {output_dir}")
                
        if self.video_count < 0:
            errors.append("Video count cannot be negative")
            
        if self.output_format not in OUTPUT_FORMATS:
            errors.append(f"Invalid output format: {self.output_format}")
            
        if self.transition not in TRANSITION_EFFECTS:
            errors.append(f"Invalid transition effect: {self.transition}")
            
        if self.transition_duration < 0 or self.transition_duration > 3:
            errors.append("Transition duration must be between 0 and 3 seconds")
            
        if self.resolution_mode not in RESOLUTION_OPTIONS:
            errors.append(f"Invalid resolution mode: {self.resolution_mode}")
            
        return errors
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MergeConfig':
        """Create configuration from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    def save(self, filepath: str) -> None:
        """
        Save configuration to a JSON file.
        
        Args:
            filepath: Path to save the configuration file.
        """
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> 'MergeConfig':
        """
        Load configuration from a JSON file.
        
        Args:
            filepath: Path to the configuration file.
            
        Returns:
            MergeConfig instance with loaded settings.
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


def get_default_output_path() -> str:
    """Get a default output path in the user's home directory."""
    home = Path.home()
    videos_dir = home / "Videos"
    if not videos_dir.exists():
        videos_dir = home
    return str(videos_dir / "merged_output.mp4")


def get_config_dir() -> Path:
    """Get the application configuration directory."""
    config_home = os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config'))
    config_dir = Path(config_home) / 'short-video-merger'
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir
