#!/usr/bin/env python3
"""
Setup script for Short Video Merger.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="short-video-merger",
    version="1.0.0",
    description="A Python-based application for merging short videos with GUI and CLI support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Short Video Merger Team",
    author_email="",
    url="https://github.com/Leshan21/short-video-merger",
    license="MIT",
    
    packages=find_packages(exclude=["tests", "tests.*", "docs"]),
    
    python_requires=">=3.8",
    
    install_requires=[
        "moviepy>=1.0.3",
        "Pillow>=9.0.0",
        "tqdm>=4.65.0",
    ],
    
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    
    entry_points={
        "console_scripts": [
            "video-merger=src.main:main",
        ],
    },
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Video",
    ],
    
    keywords="video merger concatenate combine short videos GUI CLI",
)
