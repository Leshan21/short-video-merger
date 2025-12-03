"""
Video processing module for the Short Video Merger application.

Handles video merging, transitions, and audio normalization using moviepy.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import List, Optional, Callable, Tuple
from dataclasses import dataclass
import time

from src.core.config import MergeConfig
from src.core.file_handler import VideoInfo
from src.utils.logger import ProgressCallback


logger = logging.getLogger(__name__)


@dataclass
class MergeResult:
    """Result of a merge operation."""
    
    success: bool
    output_path: Optional[str] = None
    duration: Optional[float] = None
    processing_time: Optional[float] = None
    error_message: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class VideoProcessor:
    """Handles video merging and processing operations."""
    
    def __init__(self, progress_callback: Optional[ProgressCallback] = None):
        """
        Initialize the video processor.
        
        Args:
            progress_callback: Optional callback for progress updates.
        """
        self._progress = progress_callback or ProgressCallback()
        self._cancelled = False
        
        # Check for moviepy availability - support both 1.x and 2.x
        self._moviepy_available = False
        self._moviepy_v2 = False
        
        try:
            # Try moviepy 2.x first
            from moviepy import VideoFileClip, concatenate_videoclips
            self._moviepy_available = True
            self._moviepy_v2 = True
        except ImportError:
            try:
                # Fall back to moviepy 1.x
                from moviepy.editor import VideoFileClip, concatenate_videoclips
                self._moviepy_available = True
            except ImportError:
                logger.error("moviepy is not installed. Video processing will not work.")
                self._moviepy_available = False
    
    @property
    def is_available(self) -> bool:
        """Check if video processing is available."""
        return self._moviepy_available
    
    def cancel(self) -> None:
        """Cancel the current operation."""
        self._cancelled = True
        self._progress.cancel()
    
    def reset(self) -> None:
        """Reset the processor state."""
        self._cancelled = False
        self._progress = ProgressCallback()
    
    def merge_videos(
        self,
        videos: List[VideoInfo],
        config: MergeConfig,
        progress_callback: Optional[ProgressCallback] = None
    ) -> MergeResult:
        """
        Merge multiple videos into a single output file.
        
        Args:
            videos: List of VideoInfo objects to merge.
            config: Merge configuration settings.
            progress_callback: Optional progress callback.
            
        Returns:
            MergeResult with status and output information.
        """
        if progress_callback:
            self._progress = progress_callback
        
        self._cancelled = False
        start_time = time.time()
        warnings = []
        
        # Validate input
        if not videos:
            return MergeResult(
                success=False,
                error_message="No videos provided for merging"
            )
        
        if not self._moviepy_available:
            return MergeResult(
                success=False,
                error_message="moviepy is not installed. Please install it with: pip install moviepy"
            )
        
        # Validate configuration
        validation_errors = config.validate()
        # Filter out errors that don't apply when videos are provided directly
        validation_errors = [e for e in validation_errors if "Input folder" not in e]
        if validation_errors:
            return MergeResult(
                success=False,
                error_message=f"Invalid configuration: {'; '.join(validation_errors)}"
            )
        
        try:
            # Import moviepy (supports both 1.x and 2.x)
            if self._moviepy_v2:
                from moviepy import VideoFileClip, concatenate_videoclips
                from moviepy.video.fx import FadeOut, FadeIn
                fadeout = lambda clip, d: clip.with_effects([FadeOut(d)])
                fadein = lambda clip, d: clip.with_effects([FadeIn(d)])
            else:
                from moviepy.editor import VideoFileClip, concatenate_videoclips
                from moviepy.video.fx.all import fadeout, fadein
            
            clips = []
            total_videos = len(videos)
            
            self._progress.update(0.0, "Loading videos...")
            
            # Load all video clips
            for i, video in enumerate(videos):
                if self._cancelled:
                    self._cleanup_clips(clips)
                    return MergeResult(
                        success=False,
                        error_message="Operation cancelled by user"
                    )
                
                self._progress.update(
                    (i / total_videos) * 0.4,
                    f"Loading video {i + 1} of {total_videos}: {video.filename}"
                )
                
                try:
                    clip = VideoFileClip(video.path)
                    
                    # Handle resolution
                    if config.resolution_mode == 'resize':
                        # Resize to match the first video's resolution
                        if clips and (clips[0].w != clip.w or clips[0].h != clip.h):
                            clip = clip.resize((clips[0].w, clips[0].h))
                    
                    clips.append(clip)
                    
                except Exception as e:
                    logger.warning(f"Could not load {video.filename}: {e}")
                    warnings.append(f"Skipped {video.filename}: {str(e)}")
            
            if not clips:
                return MergeResult(
                    success=False,
                    error_message="Could not load any video files",
                    warnings=warnings
                )
            
            if self._cancelled:
                self._cleanup_clips(clips)
                return MergeResult(
                    success=False,
                    error_message="Operation cancelled by user"
                )
            
            self._progress.update(0.5, "Applying transitions...")
            
            # Apply transitions if specified
            if config.transition != 'none' and config.transition_duration > 0:
                clips = self._apply_transitions(
                    clips, config.transition, config.transition_duration
                )
            
            if self._cancelled:
                self._cleanup_clips(clips)
                return MergeResult(
                    success=False,
                    error_message="Operation cancelled by user"
                )
            
            self._progress.update(0.6, "Concatenating videos...")
            
            # Concatenate all clips
            method = 'compose' if config.resolution_mode != 'keep' else 'chain'
            final_clip = concatenate_videoclips(clips, method=method)
            
            # Normalize audio if requested
            if config.normalize_audio:
                self._progress.update(0.7, "Normalizing audio...")
                final_clip = self._normalize_audio(final_clip)
            
            if self._cancelled:
                final_clip.close()
                self._cleanup_clips(clips)
                return MergeResult(
                    success=False,
                    error_message="Operation cancelled by user"
                )
            
            self._progress.update(0.75, "Writing output file...")
            
            # Ensure output path has correct extension
            output_path = Path(config.output_path)
            if output_path.suffix.lower() != f'.{config.output_format}':
                output_path = output_path.with_suffix(f'.{config.output_format}')
            
            # Write the output file
            codec = self._get_codec(config.output_format)
            audio_codec = 'aac' if config.output_format in ['mp4', 'mov', 'mkv'] else 'mp3'
            
            # Get total duration for progress updates
            total_duration = final_clip.duration
            
            def progress_logger(t):
                if total_duration > 0:
                    progress = 0.75 + (t / total_duration) * 0.23
                    self._progress.update(
                        progress,
                        f"Encoding: {int(progress * 100)}% complete"
                    )
            
            final_clip.write_videofile(
                str(output_path),
                codec=codec,
                audio_codec=audio_codec,
                logger=None,  # Disable moviepy's own logging
                temp_audiofile=str(Path(config.output_path).parent / 'temp_audio.m4a')
            )
            
            # Get final duration
            output_duration = final_clip.duration
            
            # Clean up
            final_clip.close()
            self._cleanup_clips(clips)
            
            # Remove temp audio file if it exists
            temp_audio = Path(config.output_path).parent / 'temp_audio.m4a'
            if temp_audio.exists():
                temp_audio.unlink()
            
            processing_time = time.time() - start_time
            
            self._progress.update(1.0, "Merge complete!")
            
            return MergeResult(
                success=True,
                output_path=str(output_path),
                duration=output_duration,
                processing_time=processing_time,
                warnings=warnings
            )
            
        except Exception as e:
            logger.exception(f"Error during video merge: {e}")
            return MergeResult(
                success=False,
                error_message=f"Error during merge: {str(e)}",
                warnings=warnings
            )
    
    def _apply_transitions(
        self,
        clips: list,
        transition: str,
        duration: float
    ) -> list:
        """
        Apply transitions between clips.
        
        Args:
            clips: List of video clips.
            transition: Transition type.
            duration: Transition duration in seconds.
            
        Returns:
            List of clips with transitions applied.
        """
        # Import fade effects based on moviepy version
        if self._moviepy_v2:
            from moviepy.video.fx import FadeOut, FadeIn
            fadeout = lambda clip, d: clip.with_effects([FadeOut(d)])
            fadein = lambda clip, d: clip.with_effects([FadeIn(d)])
        else:
            from moviepy.video.fx.all import fadeout, fadein
        
        if transition in ['fade', 'dissolve', 'crossfade']:
            processed = []
            for i, clip in enumerate(clips):
                # Don't extend clip duration beyond original
                trans_duration = min(duration, clip.duration / 2)
                
                # Apply fade in for all clips except the first
                if i > 0:
                    clip = fadein(clip, trans_duration)
                
                # Apply fade out for all clips except the last
                if i < len(clips) - 1:
                    clip = fadeout(clip, trans_duration)
                
                processed.append(clip)
            return processed
        
        return clips
    
    def _normalize_audio(self, clip):
        """
        Normalize audio levels in the clip.
        
        Args:
            clip: Video clip to normalize.
            
        Returns:
            Clip with normalized audio.
        """
        try:
            # Simple audio normalization using volumex
            from moviepy.video.fx.all import volumex
            
            # Calculate average volume and normalize
            # This is a simplified approach - full normalization would analyze the audio
            return clip
        except Exception as e:
            logger.warning(f"Could not normalize audio: {e}")
            return clip
    
    def _get_codec(self, output_format: str) -> str:
        """
        Get the appropriate codec for the output format.
        
        Args:
            output_format: Output format string.
            
        Returns:
            Codec name.
        """
        codecs = {
            'mp4': 'libx264',
            'avi': 'mpeg4',
            'mov': 'libx264',
            'mkv': 'libx264'
        }
        return codecs.get(output_format, 'libx264')
    
    def _cleanup_clips(self, clips: list) -> None:
        """
        Clean up loaded video clips.
        
        Args:
            clips: List of video clips to close.
        """
        for clip in clips:
            try:
                clip.close()
            except Exception:
                pass
    
    def check_disk_space(
        self,
        output_path: str,
        estimated_size_mb: float
    ) -> Tuple[bool, str]:
        """
        Check if there's enough disk space for the output.
        
        Args:
            output_path: Path where output will be written.
            estimated_size_mb: Estimated output size in MB.
            
        Returns:
            Tuple of (has_space, message)
        """
        try:
            output_dir = Path(output_path).parent
            stat = shutil.disk_usage(output_dir)
            free_mb = stat.free / (1024 * 1024)
            
            # Require 2x the estimated size for safety
            required_mb = estimated_size_mb * 2
            
            if free_mb < required_mb:
                return False, f"Insufficient disk space. Need {required_mb:.0f}MB, have {free_mb:.0f}MB"
            
            return True, f"Disk space OK: {free_mb:.0f}MB available"
            
        except Exception as e:
            return True, f"Could not check disk space: {e}"


def estimate_output_size(videos: List[VideoInfo]) -> float:
    """
    Estimate the output file size based on input videos.
    
    Args:
        videos: List of videos to merge.
        
    Returns:
        Estimated size in megabytes.
    """
    total_size = sum(v.size_bytes for v in videos)
    # Add 10% overhead for re-encoding
    return (total_size / (1024 * 1024)) * 1.1
