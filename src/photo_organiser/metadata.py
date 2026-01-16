"""Extract date metadata from media files and companion JSON files.

This module handles extracting photo/video dates from multiple sources:
1. Google Takeout companion JSON files (primary source)
2. EXIF data embedded in image files
3. File modification time (fallback)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from PIL import Image
from PIL.ExifTags import TAGS


def parse_json_metadata(json_path: Path) -> Optional[datetime]:
    """Parse date from Google Takeout companion JSON file.

    Google Takeout creates companion JSON files with metadata like:
    {
        "photoTakenTime": {
            "timestamp": "1609459200",  # Unix timestamp
            "formatted": "Jan 1, 2021, 12:00:00 AM UTC"
        },
        ...
    }

    Args:
        json_path: Path to the JSON metadata file

    Returns:
        datetime object if successful, None otherwise
    """
    if not json_path.exists():
        return None

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract photoTakenTime.timestamp field
        if 'photoTakenTime' in data:
            photo_taken = data['photoTakenTime']
            if 'timestamp' in photo_taken:
                timestamp = int(photo_taken['timestamp'])
                return datetime.fromtimestamp(timestamp)

        return None

    except (json.JSONDecodeError, ValueError, KeyError, OSError):
        # Failed to parse JSON or extract timestamp
        return None


def read_exif_date(image_path: Path) -> Optional[datetime]:
    """Read date from EXIF metadata in image file.

    Looks for the DateTimeOriginal EXIF tag (0x9003), which represents
    when the photo was taken.

    Args:
        image_path: Path to the image file

    Returns:
        datetime object if EXIF date found, None otherwise
    """
    if not image_path.exists():
        return None

    try:
        with Image.open(image_path) as img:
            # Get EXIF data
            exif_data = img._getexif()
            if not exif_data:
                return None

            # Find DateTimeOriginal tag (36867 = 0x9003)
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                if tag_name == 'DateTimeOriginal':
                    # EXIF date format: "YYYY:MM:DD HH:MM:SS"
                    return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')

            return None

    except (OSError, AttributeError, ValueError, KeyError):
        # Failed to read image or parse EXIF
        return None
    except PermissionError:
        # Lacking permissions to read file
        return None
    except Exception:
        # Catch-all for corrupted images or unsupported formats
        # Return None to fall back to other metadata sources
        return None


def get_file_modification_date(file_path: Path) -> datetime:
    """Get file modification time as fallback date.

    Args:
        file_path: Path to the file

    Returns:
        datetime object from file's modification time
    """
    mtime = file_path.stat().st_mtime
    return datetime.fromtimestamp(mtime)


def get_best_date(media_path: Path) -> Optional[datetime]:
    """Determine the best date for a media file.

    Priority order:
    1. Companion JSON file (Google Takeout metadata)
    2. EXIF data from image

    Args:
        media_path: Path to the media file

    Returns:
        datetime object if a reliable date was found, None otherwise
    """
    # Try companion JSON first (e.g., photo.jpg.json)
    json_path = Path(str(media_path) + '.json')
    date = parse_json_metadata(json_path)
    if date:
        return date

    # Try EXIF data (images only)
    if media_path.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'}:
        date = read_exif_date(media_path)
        if date:
            return date

    # No reliable date found
    return None


def extract_year(date: datetime) -> int:
    """Extract year from datetime object.

    Args:
        date: datetime object

    Returns:
        Year as integer (e.g., 2021)
    """
    return date.year
