"""
Unit tests for the video processor module.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock

from src.core.video_processor import VideoProcessor, MergeResult, estimate_output_size
from src.core.file_handler import VideoInfo
from src.core.config import MergeConfig
from src.utils.logger import ProgressCallback


class TestMergeResult:
    """Tests for the MergeResult dataclass."""
    
    def test_success_result(self):
        """Test creating a successful result."""
        result = MergeResult(
            success=True,
            output_path="/path/to/output.mp4",
            duration=120.5,
            processing_time=45.2
        )
        assert result.success is True
        assert result.output_path == "/path/to/output.mp4"
        assert result.duration == 120.5
        assert result.processing_time == 45.2
        assert result.warnings == []
    
    def test_failure_result(self):
        """Test creating a failure result."""
        result = MergeResult(
            success=False,
            error_message="Something went wrong"
        )
        assert result.success is False
        assert result.error_message == "Something went wrong"
    
    def test_result_with_warnings(self):
        """Test result with warnings."""
        result = MergeResult(
            success=True,
            warnings=["Warning 1", "Warning 2"]
        )
        assert len(result.warnings) == 2


class TestVideoProcessor:
    """Tests for the VideoProcessor class."""
    
    def test_init(self):
        """Test processor initialization."""
        processor = VideoProcessor()
        # is_available depends on moviepy installation
        assert isinstance(processor.is_available, bool)
    
    def test_init_with_progress_callback(self):
        """Test initialization with progress callback."""
        callback = ProgressCallback()
        processor = VideoProcessor(progress_callback=callback)
        assert processor is not None
    
    def test_cancel(self):
        """Test cancellation."""
        processor = VideoProcessor()
        processor.cancel()
        # Verify cancellation state is set
        assert processor._cancelled is True
    
    def test_reset(self):
        """Test reset after cancellation."""
        processor = VideoProcessor()
        processor.cancel()
        processor.reset()
        assert processor._cancelled is False
    
    def test_merge_videos_no_videos(self):
        """Test merge with no videos."""
        processor = VideoProcessor()
        config = MergeConfig(output_path="/tmp/output.mp4")
        
        result = processor.merge_videos([], config)
        
        assert result.success is False
        assert "No videos" in result.error_message
    
    def test_merge_videos_invalid_config(self):
        """Test merge with invalid configuration."""
        processor = VideoProcessor()
        videos = [
            VideoInfo(path="/test/v1.mp4", filename="v1.mp4", size_bytes=1024)
        ]
        config = MergeConfig(
            output_path="",  # Invalid - empty path
            transition_duration=10  # Invalid - too long
        )
        
        result = processor.merge_videos(videos, config)
        
        assert result.success is False
    
    def test_merge_videos_moviepy_not_available(self):
        """Test merge when moviepy is not available."""
        processor = VideoProcessor()
        # Manually set moviepy as unavailable
        processor._moviepy_available = False
        
        videos = [
            VideoInfo(path="/test/v1.mp4", filename="v1.mp4", size_bytes=1024)
        ]
        config = MergeConfig(output_path="/tmp/output.mp4")
        
        result = processor.merge_videos(videos, config)
        
        assert result.success is False
        assert "moviepy" in result.error_message.lower()
    
    def test_check_disk_space(self):
        """Test disk space check."""
        processor = VideoProcessor()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.mp4")
            has_space, message = processor.check_disk_space(output_path, 10)
            
            # Should have space for 10MB in temp directory
            assert has_space is True
    
    def test_check_disk_space_insufficient(self):
        """Test disk space check with insufficient space."""
        processor = VideoProcessor()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.mp4")
            # Request impossibly large amount
            has_space, message = processor.check_disk_space(
                output_path, 
                1000000000  # 1 petabyte
            )
            
            assert has_space is False
    
    def test_get_codec(self):
        """Test codec selection for different formats."""
        processor = VideoProcessor()
        
        assert processor._get_codec('mp4') == 'libx264'
        assert processor._get_codec('avi') == 'mpeg4'
        assert processor._get_codec('mov') == 'libx264'
        assert processor._get_codec('mkv') == 'libx264'
        assert processor._get_codec('unknown') == 'libx264'


class TestEstimateOutputSize:
    """Tests for the estimate_output_size function."""
    
    def test_estimate_single_video(self):
        """Test estimation with single video."""
        videos = [
            VideoInfo(path="/test/v1.mp4", filename="v1.mp4", size_bytes=1024 * 1024)
        ]
        
        estimate = estimate_output_size(videos)
        
        # Should be 1MB + 10% overhead = 1.1MB
        assert estimate == pytest.approx(1.1, rel=0.01)
    
    def test_estimate_multiple_videos(self):
        """Test estimation with multiple videos."""
        videos = [
            VideoInfo(path="/test/v1.mp4", filename="v1.mp4", size_bytes=1024 * 1024),
            VideoInfo(path="/test/v2.mp4", filename="v2.mp4", size_bytes=2 * 1024 * 1024),
            VideoInfo(path="/test/v3.mp4", filename="v3.mp4", size_bytes=3 * 1024 * 1024),
        ]
        
        estimate = estimate_output_size(videos)
        
        # Should be 6MB + 10% overhead = 6.6MB
        assert estimate == pytest.approx(6.6, rel=0.01)
    
    def test_estimate_empty_list(self):
        """Test estimation with empty list."""
        estimate = estimate_output_size([])
        assert estimate == 0.0


class TestProgressCallback:
    """Tests for the ProgressCallback class."""
    
    def test_init(self):
        """Test callback initialization."""
        callback = ProgressCallback()
        assert callback.progress == 0.0
        assert callback.message == ""
        assert callback.is_cancelled is False
    
    def test_update(self):
        """Test progress update."""
        callback = ProgressCallback()
        callback.update(0.5, "Processing...")
        
        assert callback.progress == 0.5
        assert callback.message == "Processing..."
    
    def test_update_clamps_value(self):
        """Test that progress is clamped to 0-1 range."""
        callback = ProgressCallback()
        
        callback.update(1.5, "Too high")
        assert callback.progress == 1.0
        
        callback.update(-0.5, "Too low")
        assert callback.progress == 0.0
    
    def test_cancel(self):
        """Test cancellation."""
        callback = ProgressCallback()
        callback.cancel()
        assert callback.is_cancelled is True
    
    def test_callback_function(self):
        """Test callback function invocation."""
        results = []
        
        def on_update(progress, message):
            results.append((progress, message))
        
        callback = ProgressCallback(callback=on_update)
        callback.update(0.25, "First")
        callback.update(0.75, "Second")
        
        assert len(results) == 2
        assert results[0] == (0.25, "First")
        assert results[1] == (0.75, "Second")
