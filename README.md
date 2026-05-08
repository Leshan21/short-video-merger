# Short Video Merger

A Python-based application for merging short videos with both GUI and CLI support. Randomly select videos from a folder and combine them into a single output video.

![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![License MIT](https://img.shields.io/badge/license-MIT-green.svg)

## Features

- **Dual Interface**: Both graphical (GUI) and command-line (CLI) modes
- **Random Selection**: Randomly select videos for merging with optional seed for reproducibility
- **Multiple Formats**: Support for MP4, AVI, MOV, MKV, WEBM, FLV, and more
- **Transitions**: Apply fade, dissolve, or crossfade effects between videos
- **Audio Normalization**: Normalize audio levels across merged videos
- **Progress Tracking**: Real-time progress updates and logging
- **Configuration Saving**: Save and load merge configurations

## Installation

### System Dependencies

First, install the required system dependencies:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3 python3-pip ffmpeg python3-tk

# Fedora
sudo dnf install python3 python3-pip ffmpeg python3-tkinter

# Arch Linux
sudo pacman -S python python-pip ffmpeg tk
```

### Python Package Installation

#### Option 1: Install from source
```bash
git clone https://github.com/Leshan21/short-video-merger.git
cd short-video-merger
pip install -r requirements.txt
```

#### Option 2: Install as package
```bash
pip install -e .
```

## Quick Start

### GUI Mode

Launch the graphical interface:

```bash
# Run directly
python -m src.main --gui

# Or simply (launches GUI by default)
python -m src.main
```

### CLI Mode

Merge videos from command line:

```bash
# Merge 5 random videos
python -m src.main --input /path/to/videos --output merged.mp4 --count 5

# Merge all videos with fade transitions
python -m src.main -i /path/to/videos -o output.mp4 --transition fade

# Merge with specific seed for reproducibility
python -m src.main -i /path/to/videos -o output.mp4 -c 10 --seed 42

# Merge with audio normalization
python -m src.main -i /path/to/videos -o output.mp4 --normalize
```

## CLI Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--input` | `-i` | Input folder with video files | Required |
| `--output` | `-o` | Output file path | Required |
| `--count` | `-c` | Number of videos to merge | All |
| `--format` | `-f` | Output format (mp4, avi, mov, mkv) | mp4 |
| `--transition` | `-t` | Transition effect (none, fade, dissolve, crossfade) | none |
| `--transition-duration` | | Duration of transitions (0-3 seconds) | 1.0 |
| `--normalize` | `-n` | Enable audio normalization | False |
| `--resolution` | | Resolution handling (keep, resize, crop, pad) | keep |
| `--seed` | `-s` | Random seed for reproducibility | None |
| `--verbose` | `-v` | Enable verbose output | False |
| `--gui` | `-g` | Launch GUI mode | False |

## GUI Usage

1. **Select Folder**: Click "Browse..." to select a folder containing video files
2. **Scan Videos**: Click "Scan Folder" to find all videos in the folder
3. **Configure**: Set merge options (count, format, transitions, etc.)
4. **Select Videos**: Either manually select videos or click "Randomize Selection"
5. **Merge**: Click "Start Merge" to begin the merge process
6. **Monitor**: Watch progress in the progress bar and log panel

## Supported Video Formats

- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- MKV (.mkv)
- WebM (.webm)
- FLV (.flv)
- WMV (.wmv)
- M4V (.m4v)

## Project Structure

```
short-video-merger/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   ├── gui/
│   │   ├── main_window.py      # Main GUI window
│   │   ├── widgets.py          # Custom widgets
│   │   └── styles.py           # GUI styling
│   ├── cli/
│   │   └── parser.py           # CLI argument parsing
│   ├── core/
│   │   ├── video_processor.py  # Video merging logic
│   │   ├── file_handler.py     # File operations
│   │   └── config.py           # Configuration
│   └── utils/
│       ├── logger.py           # Logging utilities
│       └── validators.py       # Input validation
├── tests/
│   ├── test_file_handler.py
│   └── test_video_processor.py
├── docs/
│   └── USAGE.md
├── requirements.txt
├── setup.py
└── LICENSE
```

## Troubleshooting

### FFmpeg not found
If you get an error about ffmpeg not being found:
```bash
sudo apt-get install ffmpeg  # Ubuntu/Debian
```

### Tkinter not available
If the GUI won't launch:
```bash
sudo apt-get install python3-tk  # Ubuntu/Debian
```

### Video loading errors
- Ensure videos are not corrupted
- Check that ffmpeg supports the video codec
- Try converting videos to MP4 format first

### Memory issues with large videos
- Merge fewer videos at a time
- Close other applications
- Consider using a machine with more RAM

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Running with Coverage
```bash
pytest tests/ --cov=src --cov-report=html
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
