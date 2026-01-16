"""Configuration constants for photo organiser.

This module defines file extensions, directory patterns, and default settings
used throughout the application.
"""

from pathlib import Path
from typing import Set

# Media file extensions
PHOTO_EXTENSIONS: Set[str] = {
    '.jpg',
    '.jpeg',
    '.png',
    '.heic',
    '.webp',
    '.gif',
}

VIDEO_EXTENSIONS: Set[str] = {
    '.mp4',
    '.mov',
    '.avi',
    '.mkv',
    '.webm',
}

# All supported media extensions
MEDIA_EXTENSIONS: Set[str] = PHOTO_EXTENSIONS | VIDEO_EXTENSIONS

# Metadata file extension (Google Takeout companion files)
METADATA_EXTENSION: str = '.json'

# Google Takeout structure patterns
TAKEOUT_ROOT: str = 'Takeout'
GOOGLE_PHOTOS_DIR: str = 'Google Photos'

# Output directory structure
DEFAULT_OUTPUT_DIR: Path = Path('./output')
PHOTOS_SUBDIR: str = 'photos'
VIDEOS_SUBDIR: str = 'videos'

# Filename conflict resolution
DUPLICATE_COUNTER_FORMAT: str = '_{:03d}'  # e.g., _001, _002

# Temporary extraction settings
TEMP_DIR_PREFIX: str = 'photo_organiser_temp_'

# File size limits (for validation)
MAX_FILENAME_LENGTH: int = 255  # Common filesystem limit
LARGE_FILE_WARNING_GB: float = 5.0  # Warn for files larger than this (in GB)
LARGE_FILE_WARNING_BYTES: int = int(LARGE_FILE_WARNING_GB * 1024 * 1024 * 1024)
