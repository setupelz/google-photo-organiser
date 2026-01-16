"""File organization logic for photo organiser.

This module handles classifying media files, generating output paths,
resolving filename conflicts, and copying files to the organized structure.
"""

from pathlib import Path
from typing import Tuple, Optional
import shutil

from .config import (
    PHOTO_EXTENSIONS,
    VIDEO_EXTENSIONS,
    PHOTOS_SUBDIR,
    VIDEOS_SUBDIR,
    DUPLICATE_COUNTER_FORMAT,
    METADATA_EXTENSION,
)


def classify_file(file_path: Path) -> Optional[str]:
    """Classify a file as photo, video, or metadata.

    Args:
        file_path: Path to the file to classify

    Returns:
        'photo', 'video', 'metadata', or None if unrecognized
    """
    suffix = file_path.suffix.lower()

    if suffix == METADATA_EXTENSION:
        return 'metadata'
    elif suffix in PHOTO_EXTENSIONS:
        return 'photo'
    elif suffix in VIDEO_EXTENSIONS:
        return 'video'

    return None


def generate_output_path(
    file_path: Path,
    year: int,
    output_dir: Path,
    file_type: str
) -> Path:
    """Generate the output path for a media file.

    Args:
        file_path: Original file path
        year: Year to organize under
        output_dir: Base output directory
        file_type: 'photo' or 'video'

    Returns:
        Complete output path: output_dir/photos|videos/YYYY/filename

    Raises:
        ValueError: If file_type is not 'photo' or 'video'
    """
    if file_type == 'photo':
        subdir = PHOTOS_SUBDIR
    elif file_type == 'video':
        subdir = VIDEOS_SUBDIR
    else:
        raise ValueError(f"file_type must be 'photo' or 'video', got '{file_type}'")

    return output_dir / subdir / str(year) / file_path.name


def resolve_filename_conflict(target_path: Path) -> Path:
    """Resolve filename conflicts by appending a counter.

    If target_path exists, append _001, _002, etc. before the extension
    until a non-existent path is found.

    Args:
        target_path: Desired output path

    Returns:
        Path that doesn't exist (may be original or with counter appended)

    Examples:
        photo.jpg -> photo_001.jpg -> photo_002.jpg
        video.mp4 -> video_001.mp4
    """
    if not target_path.exists():
        return target_path

    # Split filename into stem and suffix
    stem = target_path.stem
    suffix = target_path.suffix
    parent = target_path.parent

    counter = 1
    while True:
        counter_str = DUPLICATE_COUNTER_FORMAT.format(counter)
        new_path = parent / f"{stem}{counter_str}{suffix}"

        if not new_path.exists():
            return new_path

        counter += 1

        # Safety check to prevent infinite loops
        if counter > 9999:
            raise RuntimeError(f"Too many duplicates for {target_path.name}")


def copy_file(source: Path, destination: Path) -> None:
    """Copy a file to destination, creating parent directories if needed.

    Args:
        source: Source file path
        destination: Destination file path

    Raises:
        OSError: If copy operation fails (disk space, permissions, etc.)
        PermissionError: If lacking permissions to read source or write destination
    """
    try:
        # Create parent directory if it doesn't exist
        destination.parent.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        raise PermissionError(f"Permission denied creating directory {destination.parent}: {e}")
    except OSError as e:
        if "No space left on device" in str(e) or e.errno == 28:
            raise OSError(f"Insufficient disk space to create directory {destination.parent}")
        raise OSError(f"Cannot create directory {destination.parent}: {e}")

    try:
        # Copy file preserving metadata
        shutil.copy2(source, destination)
    except PermissionError as e:
        raise PermissionError(f"Permission denied copying {source.name} to {destination}: {e}")
    except OSError as e:
        # Check for disk space issues
        if "No space left on device" in str(e) or e.errno == 28:
            raise OSError(f"Insufficient disk space to copy {source.name}")
        raise OSError(f"Cannot copy {source.name}: {e}")


def organize_file(
    file_path: Path,
    year: int,
    output_dir: Path
) -> Optional[Tuple[str, Path]]:
    """Organize a single file into the output directory structure.

    This is the main entry point for organizing a file. It:
    1. Classifies the file type
    2. Skips metadata files
    3. Generates output path
    4. Resolves conflicts
    5. Copies the file

    Args:
        file_path: Path to file to organize
        year: Year to organize under
        output_dir: Base output directory

    Returns:
        Tuple of (file_type, destination_path) if file was organized,
        None if file was skipped (metadata or unrecognized)

    Raises:
        ValueError: If year is invalid
        OSError: If file operations fail
    """
    # Validate year
    if not (1900 <= year <= 2100):
        raise ValueError(f"Invalid year: {year}")

    # Classify file
    file_type = classify_file(file_path)

    # Skip metadata files and unrecognized files
    if file_type is None or file_type == 'metadata':
        return None

    # Generate output path
    target_path = generate_output_path(file_path, year, output_dir, file_type)

    # Resolve conflicts
    final_path = resolve_filename_conflict(target_path)

    # Copy file
    copy_file(file_path, final_path)

    return (file_type, final_path)
