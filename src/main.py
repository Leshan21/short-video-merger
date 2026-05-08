#!/usr/bin/env python3
"""
Short Video Merger - Main entry point.

Provides both GUI and CLI interfaces for merging short videos.
"""

import sys
import logging
from pathlib import Path

from src.cli.parser import parse_args, validate_cli_args, args_to_config
from src.core.file_handler import FileHandler
from src.core.video_processor import VideoProcessor, MergeResult
from src.utils.logger import setup_logger, ProgressCallback


def run_cli(args) -> int:
    """
    Run the application in CLI mode.
    
    Args:
        args: Parsed command-line arguments.
        
    Returns:
        Exit code (0 for success, 1 for error).
    """
    # Set up logging
    logger = setup_logger(verbose=args.verbose)
    
    # Validate arguments
    is_valid, errors = validate_cli_args(args)
    if not is_valid:
        for error in errors:
            logger.error(error)
        return 1
    
    # Create configuration from arguments
    config = args_to_config(args)
    
    # Initialize file handler and scan folder
    logger.info(f"Scanning folder: {config.input_folder}")
    file_handler = FileHandler(config.input_folder)
    videos = file_handler.scan_folder()
    
    if not videos:
        logger.error(f"No video files found in {config.input_folder}")
        return 1
    
    logger.info(f"Found {len(videos)} video files")
    
    # Get random selection
    count = config.video_count if config.video_count > 0 else len(videos)
    selected = file_handler.get_random_selection(count, config.random_seed)
    
    logger.info(f"Selected {len(selected)} videos for merging:")
    for i, video in enumerate(selected, 1):
        logger.info(f"  {i}. {video.filename} ({video.duration_formatted})")
    
    # Create progress callback
    def progress_update(progress: float, message: str):
        if args.verbose or progress == 0 or progress >= 1:
            percent = int(progress * 100)
            print(f"\r[{'=' * (percent // 2)}{' ' * (50 - percent // 2)}] {percent}% {message}", end='')
            if progress >= 1:
                print()  # New line at completion
    
    progress = ProgressCallback(callback=progress_update)
    
    # Initialize video processor
    processor = VideoProcessor(progress)
    
    if not processor.is_available:
        logger.error("moviepy is not available. Please install it: pip install moviepy")
        return 1
    
    # Perform merge
    logger.info(f"Starting merge to {config.output_path}")
    result = processor.merge_videos(selected, config, progress)
    
    # Report result
    if result.success:
        logger.info(f"\nMerge completed successfully!")
        logger.info(f"Output file: {result.output_path}")
        if result.duration:
            logger.info(f"Output duration: {result.duration:.1f} seconds")
        if result.processing_time:
            logger.info(f"Processing time: {result.processing_time:.1f} seconds")
        
        for warning in result.warnings:
            logger.warning(warning)
        
        return 0
    else:
        logger.error(f"\nMerge failed: {result.error_message}")
        for warning in result.warnings:
            logger.warning(warning)
        return 1


def run_gui() -> int:
    """
    Run the application in GUI mode.
    
    Returns:
        Exit code (0 for success).
    """
    try:
        from src.gui.main_window import launch_gui
        launch_gui()
        return 0
    except ImportError as e:
        print(f"Error: Could not import GUI components: {e}")
        print("Make sure tkinter is installed.")
        return 1
    except Exception as e:
        print(f"Error: Failed to launch GUI: {e}")
        return 1


def main() -> int:
    """
    Main entry point for the application.
    
    Returns:
        Exit code.
    """
    # Parse arguments
    args = parse_args()
    
    # Check if GUI mode is requested
    if args.gui:
        return run_gui()
    
    # If no arguments provided (except defaults), launch GUI
    if not args.input and not args.output:
        return run_gui()
    
    # Run CLI mode
    return run_cli(args)


if __name__ == "__main__":
    sys.exit(main())
