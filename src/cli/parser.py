"""
CLI argument parsing for the Short Video Merger application.

Provides command-line interface using argparse.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from src.core.config import (
    MergeConfig,
    OUTPUT_FORMATS,
    TRANSITION_EFFECTS,
    RESOLUTION_OPTIONS
)


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser.
    
    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog='video_merger',
        description='Merge short videos from a folder into a single output video.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Merge 5 random videos
  python -m src.main --input /path/to/videos --output merged.mp4 --count 5

  # Merge all videos with fade transitions
  python -m src.main -i /path/to/videos -o output.mp4 --transition fade

  # Merge with audio normalization and specific seed
  python -m src.main -i /path/to/videos -o output.mp4 -c 10 --normalize --seed 42

  # Launch GUI mode
  python -m src.main --gui
        '''
    )
    
    # Mode selection
    parser.add_argument(
        '--gui', '-g',
        action='store_true',
        help='Launch the graphical user interface'
    )
    
    # Input/Output
    parser.add_argument(
        '--input', '-i',
        type=str,
        metavar='FOLDER',
        help='Input folder containing video files'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        metavar='FILE',
        help='Output file path for merged video'
    )
    
    # Video selection
    parser.add_argument(
        '--count', '-c',
        type=int,
        default=0,
        metavar='N',
        help='Number of videos to randomly select (default: all)'
    )
    
    parser.add_argument(
        '--seed', '-s',
        type=int,
        metavar='SEED',
        help='Random seed for reproducible selection'
    )
    
    # Output settings
    parser.add_argument(
        '--format', '-f',
        type=str,
        choices=OUTPUT_FORMATS,
        default='mp4',
        help='Output video format (default: mp4)'
    )
    
    # Transitions
    parser.add_argument(
        '--transition', '-t',
        type=str,
        choices=TRANSITION_EFFECTS,
        default='none',
        help='Transition effect between videos (default: none)'
    )
    
    parser.add_argument(
        '--transition-duration',
        type=float,
        default=1.0,
        metavar='SECONDS',
        help='Duration of transitions in seconds (default: 1.0)'
    )
    
    # Audio
    parser.add_argument(
        '--normalize', '-n',
        action='store_true',
        help='Enable audio normalization'
    )
    
    # Resolution
    parser.add_argument(
        '--resolution',
        type=str,
        choices=RESOLUTION_OPTIONS,
        default='keep',
        help='Resolution handling mode (default: keep)'
    )
    
    # Verbosity
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    # Version
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    return parser


def parse_args(args: Optional[list] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Args:
        args: Optional list of arguments. Uses sys.argv if None.
        
    Returns:
        Parsed arguments namespace.
    """
    parser = create_parser()
    return parser.parse_args(args)


def validate_cli_args(args: argparse.Namespace) -> tuple:
    """
    Validate parsed CLI arguments.
    
    Args:
        args: Parsed arguments namespace.
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # GUI mode doesn't require input/output
    if args.gui:
        return True, []
    
    # Check required arguments for CLI mode
    if not args.input:
        errors.append("--input is required in CLI mode")
    elif not Path(args.input).is_dir():
        errors.append(f"Input folder does not exist: {args.input}")
    
    if not args.output:
        errors.append("--output is required in CLI mode")
    else:
        output_path = Path(args.output)
        if not output_path.parent.exists():
            errors.append(f"Output directory does not exist: {output_path.parent}")
    
    # Validate transition duration
    if args.transition_duration < 0 or args.transition_duration > 3:
        errors.append("Transition duration must be between 0 and 3 seconds")
    
    # Validate count
    if args.count < 0:
        errors.append("Count cannot be negative")
    
    return len(errors) == 0, errors


def args_to_config(args: argparse.Namespace) -> MergeConfig:
    """
    Convert parsed arguments to a MergeConfig object.
    
    Args:
        args: Parsed arguments namespace.
        
    Returns:
        MergeConfig instance.
    """
    return MergeConfig(
        input_folder=args.input or "",
        output_path=args.output or "",
        video_count=args.count,
        output_format=args.format,
        transition=args.transition,
        transition_duration=args.transition_duration,
        resolution_mode=args.resolution,
        normalize_audio=args.normalize,
        random_seed=args.seed
    )
