"""
Unit tests for the file handler module.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.core.file_handler import FileHandler, VideoInfo
from src.core.config import SUPPORTED_VIDEO_FORMATS


class TestVideoInfo:
    """Tests for the VideoInfo dataclass."""
    
    def test_size_mb_conversion(self):
        """Test file size conversion to megabytes."""
        video = VideoInfo(
            path="/test/video.mp4",
            filename="video.mp4",
            size_bytes=1024 * 1024  # 1 MB
        )
        assert video.size_mb == 1.0
    
    def test_size_mb_conversion_fractional(self):
        """Test fractional megabyte conversion."""
        video = VideoInfo(
            path="/test/video.mp4",
            filename="video.mp4",
            size_bytes=1024 * 1024 * 2 + 512 * 1024  # 2.5 MB
        )
        assert video.size_mb == 2.5
    
    def test_resolution_with_dimensions(self):
        """Test resolution string with known dimensions."""
        video = VideoInfo(
            path="/test/video.mp4",
            filename="video.mp4",
            size_bytes=1024,
            width=1920,
            height=1080
        )
        assert video.resolution == "1920x1080"
    
    def test_resolution_without_dimensions(self):
        """Test resolution string when dimensions are unknown."""
        video = VideoInfo(
            path="/test/video.mp4",
            filename="video.mp4",
            size_bytes=1024
        )
        assert video.resolution == "Unknown"
    
    def test_duration_formatted_with_duration(self):
        """Test formatted duration string."""
        video = VideoInfo(
            path="/test/video.mp4",
            filename="video.mp4",
            size_bytes=1024,
            duration=125.5  # 2:05
        )
        assert video.duration_formatted == "02:05"
    
    def test_duration_formatted_without_duration(self):
        """Test formatted duration when duration is unknown."""
        video = VideoInfo(
            path="/test/video.mp4",
            filename="video.mp4",
            size_bytes=1024
        )
        assert video.duration_formatted == "Unknown"
    
    def test_str_representation(self):
        """Test string representation of VideoInfo."""
        video = VideoInfo(
            path="/test/video.mp4",
            filename="video.mp4",
            size_bytes=1024,
            width=1920,
            height=1080,
            duration=60.0
        )
        assert "video.mp4" in str(video)
        assert "1920x1080" in str(video)


class TestFileHandler:
    """Tests for the FileHandler class."""
    
    def test_init_without_folder(self):
        """Test initialization without folder path."""
        handler = FileHandler()
        assert handler.folder_path is None
        assert handler.videos == []
    
    def test_init_with_valid_folder(self):
        """Test initialization with valid folder path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            handler = FileHandler(tmpdir)
            assert handler.folder_path == tmpdir
    
    def test_init_with_invalid_folder(self):
        """Test initialization with invalid folder path."""
        handler = FileHandler("/nonexistent/path")
        assert handler.folder_path is None
    
    def test_set_folder_valid(self):
        """Test setting a valid folder path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            handler = FileHandler()
            result = handler.set_folder(tmpdir)
            assert result is True
            assert handler.folder_path == tmpdir
    
    def test_set_folder_invalid(self):
        """Test setting an invalid folder path."""
        handler = FileHandler()
        result = handler.set_folder("/nonexistent/path")
        assert result is False
    
    def test_scan_folder_empty(self):
        """Test scanning an empty folder."""
        with tempfile.TemporaryDirectory() as tmpdir:
            handler = FileHandler(tmpdir)
            videos = handler.scan_folder()
            assert videos == []
    
    def test_scan_folder_with_videos(self):
        """Test scanning a folder with video files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some dummy video files
            for ext in ['.mp4', '.avi', '.mov']:
                video_file = Path(tmpdir) / f"video{ext}"
                video_file.write_bytes(b'dummy content')
            
            # Create a non-video file
            (Path(tmpdir) / "readme.txt").write_text("not a video")
            
            handler = FileHandler(tmpdir)
            videos = handler.scan_folder()
            
            assert len(videos) == 3
            filenames = [v.filename for v in videos]
            assert 'video.mp4' in filenames
            assert 'video.avi' in filenames
            assert 'video.mov' in filenames
    
    def test_scan_folder_no_folder_set(self):
        """Test scanning without a folder set."""
        handler = FileHandler()
        videos = handler.scan_folder()
        assert videos == []
    
    def test_get_random_selection(self):
        """Test random selection of videos."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create video files
            for i in range(10):
                (Path(tmpdir) / f"video{i}.mp4").write_bytes(b'content')
            
            handler = FileHandler(tmpdir)
            handler.scan_folder()
            
            selected = handler.get_random_selection(5)
            assert len(selected) == 5
    
    def test_get_random_selection_with_seed(self):
        """Test random selection with seed for reproducibility."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create video files
            for i in range(10):
                (Path(tmpdir) / f"video{i}.mp4").write_bytes(b'content')
            
            handler = FileHandler(tmpdir)
            handler.scan_folder()
            
            selected1 = handler.get_random_selection(5, seed=42)
            selected2 = handler.get_random_selection(5, seed=42)
            
            # Same seed should give same selection
            assert [v.filename for v in selected1] == [v.filename for v in selected2]
    
    def test_get_random_selection_count_exceeds_available(self):
        """Test selection when count exceeds available videos."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create video files
            for i in range(3):
                (Path(tmpdir) / f"video{i}.mp4").write_bytes(b'content')
            
            handler = FileHandler(tmpdir)
            handler.scan_folder()
            
            selected = handler.get_random_selection(10)
            assert len(selected) == 3  # Should return all available
    
    def test_enable_video(self):
        """Test enabling/disabling a video."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "video.mp4").write_bytes(b'content')
            
            handler = FileHandler(tmpdir)
            handler.scan_folder()
            
            # Disable video
            result = handler.enable_video("video.mp4", False)
            assert result is True
            assert handler.enabled_videos == []
            
            # Enable video
            result = handler.enable_video("video.mp4", True)
            assert result is True
            assert len(handler.enabled_videos) == 1
    
    def test_enable_video_not_found(self):
        """Test enabling a non-existent video."""
        with tempfile.TemporaryDirectory() as tmpdir:
            handler = FileHandler(tmpdir)
            handler.scan_folder()
            
            result = handler.enable_video("nonexistent.mp4", True)
            assert result is False
    
    def test_enable_all(self):
        """Test enabling/disabling all videos."""
        with tempfile.TemporaryDirectory() as tmpdir:
            for i in range(5):
                (Path(tmpdir) / f"video{i}.mp4").write_bytes(b'content')
            
            handler = FileHandler(tmpdir)
            handler.scan_folder()
            
            # Disable all
            handler.enable_all(False)
            assert len(handler.enabled_videos) == 0
            
            # Enable all
            handler.enable_all(True)
            assert len(handler.enabled_videos) == 5
    
    def test_get_video_by_filename(self):
        """Test getting a video by filename."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "video.mp4").write_bytes(b'content')
            
            handler = FileHandler(tmpdir)
            handler.scan_folder()
            
            video = handler.get_video_by_filename("video.mp4")
            assert video is not None
            assert video.filename == "video.mp4"
    
    def test_get_video_by_filename_not_found(self):
        """Test getting a non-existent video."""
        with tempfile.TemporaryDirectory() as tmpdir:
            handler = FileHandler(tmpdir)
            handler.scan_folder()
            
            video = handler.get_video_by_filename("nonexistent.mp4")
            assert video is None
    
    def test_get_total_duration(self):
        """Test calculating total duration."""
        videos = [
            VideoInfo(path="v1.mp4", filename="v1.mp4", size_bytes=1024, duration=10.0),
            VideoInfo(path="v2.mp4", filename="v2.mp4", size_bytes=1024, duration=20.0),
            VideoInfo(path="v3.mp4", filename="v3.mp4", size_bytes=1024, duration=30.0),
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            handler = FileHandler(tmpdir)
            total = handler.get_total_duration(videos)
            assert total == 60.0
    
    def test_validate_videos_all_exist(self):
        """Test validation when all videos exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = Path(tmpdir) / "video.mp4"
            video_path.write_bytes(b'content')
            
            videos = [
                VideoInfo(path=str(video_path), filename="video.mp4", size_bytes=1024)
            ]
            
            handler = FileHandler(tmpdir)
            is_valid, errors = handler.validate_videos(videos)
            
            assert is_valid is True
            assert errors == []
    
    def test_validate_videos_some_missing(self):
        """Test validation when some videos are missing."""
        videos = [
            VideoInfo(path="/nonexistent/video.mp4", filename="video.mp4", size_bytes=1024)
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            handler = FileHandler(tmpdir)
            is_valid, errors = handler.validate_videos(videos)
            
            assert is_valid is False
            assert len(errors) == 1
