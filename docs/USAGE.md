# Short Video Merger - Usage Guide

This document provides detailed usage instructions for the Short Video Merger application.

## Table of Contents

- [Installation](#installation)
- [GUI Mode](#gui-mode)
- [CLI Mode](#cli-mode)
- [Configuration Options](#configuration-options)
- [Advanced Features](#advanced-features)
- [Tips and Best Practices](#tips-and-best-practices)

## Installation

### Prerequisites

1. **Python 3.8 or higher**
2. **FFmpeg** - Required for video processing
3. **Tkinter** - Required for GUI mode (usually included with Python)

### Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3 python3-pip ffmpeg python3-tk

# Verify FFmpeg installation
ffmpeg -version
```

### Install Python Dependencies

```bash
cd short-video-merger
pip install -r requirements.txt
```

Or install as a package:

```bash
pip install -e .
```

## GUI Mode

### Launching the GUI

```bash
# Default launch (opens GUI)
python -m src.main

# Explicitly request GUI
python -m src.main --gui
```

### Main Window Overview

The GUI is divided into several sections:

#### 1. Input Folder Section

- **Video Folder**: Enter or browse for the folder containing your videos
- **Scan Folder**: Button to scan the folder and find all video files
- **Video Count**: Shows how many videos were found

#### 2. Video List Panel

Displays all discovered videos with:
- Filename
- Duration (MM:SS format)
- Resolution (e.g., 1920x1080)
- File size

You can:
- Click to select individual videos
- Ctrl+Click to select multiple videos
- The list supports highlighting for random selections

#### 3. Configuration Panel

**Videos to merge**: Number of videos to randomly select (0 = all)

**Output file**: Where to save the merged video

**Output format**: Choose from MP4, AVI, MOV, or MKV

**Transition**: Effect between videos
- `none`: Direct cut between videos
- `fade`: Fade to black between videos
- `dissolve`: Cross-dissolve effect
- `crossfade`: Blend videos together

**Transition duration**: Length of transition effect (0-3 seconds)

**Resolution**: How to handle different resolutions
- `keep`: Keep original resolutions (may cause issues)
- `resize`: Resize all videos to match the first video
- `crop`: Crop videos to match (not fully implemented)
- `pad`: Add black bars to match (not fully implemented)

**Normalize audio**: Checkbox to normalize audio levels

**Random seed**: For reproducible random selection

#### 4. Control Buttons

- **Randomize Selection**: Select random videos based on settings
- **Clear**: Reset all fields
- **Cancel**: Cancel ongoing merge operation
- **Start Merge**: Begin the merge process

#### 5. Progress Panel

Shows:
- Current status message
- Progress bar (percentage)
- Processing details in log panel

### Typical GUI Workflow

1. Click "Browse..." next to Video Folder
2. Select your folder containing videos
3. Click "Scan Folder"
4. Review the video list
5. Set the number of videos to merge (or leave at 0 for all)
6. Choose output location and format
7. Configure transitions if desired
8. Click "Randomize Selection" to see which videos will be selected
9. Click "Start Merge"
10. Wait for completion

## CLI Mode

### Basic Usage

```bash
python -m src.main --input <folder> --output <file> [options]
```

### Required Arguments

| Argument | Short | Description |
|----------|-------|-------------|
| `--input` | `-i` | Path to folder containing video files |
| `--output` | `-o` | Path for the output merged video |

### Optional Arguments

| Argument | Short | Default | Description |
|----------|-------|---------|-------------|
| `--count` | `-c` | 0 (all) | Number of videos to randomly select |
| `--format` | `-f` | mp4 | Output format |
| `--transition` | `-t` | none | Transition effect |
| `--transition-duration` | | 1.0 | Duration of transitions |
| `--normalize` | `-n` | false | Enable audio normalization |
| `--resolution` | | keep | Resolution handling mode |
| `--seed` | `-s` | random | Random seed for reproducibility |
| `--verbose` | `-v` | false | Show detailed output |

### CLI Examples

#### Merge All Videos
```bash
python -m src.main -i ~/Videos/clips -o ~/Videos/merged.mp4
```

#### Merge 5 Random Videos
```bash
python -m src.main -i ~/Videos/clips -o ~/Videos/merged.mp4 -c 5
```

#### Use Fade Transitions
```bash
python -m src.main -i ~/Videos/clips -o ~/Videos/merged.mp4 \
    --transition fade --transition-duration 1.5
```

#### Reproducible Random Selection
```bash
# Same seed = same videos selected
python -m src.main -i ~/Videos/clips -o ~/Videos/merged.mp4 -c 10 --seed 42
```

#### Verbose Output with Normalization
```bash
python -m src.main -i ~/Videos/clips -o ~/Videos/merged.mp4 \
    --normalize --verbose
```

#### Output as AVI with Resize
```bash
python -m src.main -i ~/Videos/clips -o ~/Videos/merged.avi \
    --format avi --resolution resize
```

## Configuration Options

### Video Count

- Set to `0` to merge all videos in the folder
- Set to a specific number to randomly select that many videos
- If the count exceeds available videos, all videos are used

### Output Formats

| Format | Extension | Codec Used | Best For |
|--------|-----------|------------|----------|
| MP4 | .mp4 | libx264/AAC | Universal compatibility |
| AVI | .avi | mpeg4/mp3 | Older software |
| MOV | .mov | libx264/AAC | Apple devices |
| MKV | .mkv | libx264/AAC | Feature-rich container |

### Transitions

| Transition | Description | Performance Impact |
|------------|-------------|-------------------|
| none | Direct cuts | Fastest |
| fade | Fade to black | Low |
| dissolve | Cross-dissolve | Medium |
| crossfade | Blend videos | Medium |

### Resolution Modes

| Mode | Description | When to Use |
|------|-------------|-------------|
| keep | Keep original resolutions | When all videos are same resolution |
| resize | Resize to match first video | Mixed resolutions |
| crop | Crop to match | Not recommended (loses content) |
| pad | Add letterboxing | Preserve all content |

## Advanced Features

### Configuration Files

Save your settings for reuse:

1. In GUI: File → Save Configuration
2. Creates a JSON file with all settings
3. Load later: File → Load Configuration

Configuration JSON format:
```json
{
  "input_folder": "/path/to/videos",
  "output_path": "/path/to/output.mp4",
  "video_count": 5,
  "output_format": "mp4",
  "transition": "fade",
  "transition_duration": 1.0,
  "resolution_mode": "resize",
  "normalize_audio": true,
  "random_seed": 42
}
```

### Reproducible Selection

Use the `--seed` option or Random seed field to get the same video selection each time:

```bash
# Always selects the same 5 videos
python -m src.main -i ~/Videos -o output.mp4 -c 5 --seed 12345
```

## Tips and Best Practices

### For Best Results

1. **Same Resolution**: Use videos with the same resolution for smoothest merging
2. **Same Format**: Using same input format reduces processing time
3. **Short Clips**: Shorter clips merge faster and use less memory
4. **Disk Space**: Ensure you have at least 2x the total video size free

### Performance Tips

1. **Use SSD**: Faster disk = faster processing
2. **Close Other Apps**: Video processing is CPU/memory intensive
3. **Batch Processing**: For many videos, consider merging in batches
4. **Format Choice**: MP4/H.264 is generally fastest to process

### Troubleshooting

#### "No videos found"
- Check folder path is correct
- Ensure videos have supported extensions
- Check file permissions

#### "FFmpeg not found"
- Install ffmpeg: `sudo apt-get install ffmpeg`
- Verify installation: `ffmpeg -version`

#### "Memory error"
- Merge fewer videos at once
- Close other applications
- Consider using a machine with more RAM

#### "Codec error"
- Try converting source videos to MP4 first
- Use `ffmpeg -i input.xyz output.mp4`

### Getting Help

- Check the README for common issues
- Review log output for specific errors
- File an issue on GitHub for bugs
