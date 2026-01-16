"""Extract and process Google Takeout zip files.

This module handles extraction of zip files to temporary directories and
manages the Google Takeout nested folder structure.
"""

import tempfile
import zipfile
from pathlib import Path
from typing import List
import shutil


def extract_zip(zip_path: Path, temp_dir: Path) -> Path:
    """Extract a zip file to a temporary directory.

    Args:
        zip_path: Path to the zip file to extract
        temp_dir: Temporary directory for extraction

    Returns:
        Path to the extracted contents (handles Takeout nested structure)

    Raises:
        FileNotFoundError: If zip file doesn't exist
        ValueError: If not a valid zip file
        zipfile.BadZipFile: If the zip file is corrupted or invalid
        OSError: If there are file system issues during extraction
        PermissionError: If lacking permissions to read zip or write to temp_dir
    """
    if not zip_path.exists():
        raise FileNotFoundError(f"Zip file not found: {zip_path}")

    if not zipfile.is_zipfile(zip_path):
        raise ValueError(f"Not a valid zip file: {zip_path}")

    try:
        # Extract to temp directory
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Test zip integrity before extraction
            bad_file = zip_ref.testzip()
            if bad_file is not None:
                raise zipfile.BadZipFile(f"Corrupted file in zip: {bad_file}")

            zip_ref.extractall(temp_dir)
    except PermissionError as e:
        raise PermissionError(f"Permission denied when extracting {zip_path}: {e}")
    except OSError as e:
        # Catch disk space issues and other OS errors
        if "No space left on device" in str(e) or e.errno == 28:
            raise OSError(f"Insufficient disk space to extract {zip_path}")
        raise OSError(f"File system error during extraction: {e}")

    # Handle Google Takeout nested structure: Takeout/Google Photos/
    takeout_path = temp_dir / "Takeout" / "Google Photos"
    if takeout_path.exists():
        return takeout_path

    # Fallback: Check for just "Google Photos" directory (some exports skip "Takeout")
    google_photos_path = temp_dir / "Google Photos"
    if google_photos_path.exists():
        return google_photos_path

    # Fallback: return root if Takeout structure not found
    # This handles edge case of non-standard zip structures
    return temp_dir


def find_media_files(root_dir: Path) -> List[Path]:
    """Recursively find all files in a directory.

    Args:
        root_dir: Root directory to search

    Returns:
        List of Path objects for all files found

    Note:
        Returns empty list if directory is empty or contains no files.
        This handles the edge case of empty zip archives gracefully.
    """
    media_files = []
    try:
        for item in root_dir.rglob("*"):
            if item.is_file():
                media_files.append(item)
    except PermissionError:
        # Skip directories we don't have permission to read
        pass
    return media_files


def create_temp_extraction_dir() -> Path:
    """Create a temporary directory for extraction.

    Returns:
        Path to temporary directory
    """
    temp_dir = Path(tempfile.mkdtemp(prefix="photo_organiser_"))
    return temp_dir


def cleanup_temp_dir(temp_dir: Path) -> None:
    """Remove temporary extraction directory and all contents.

    Args:
        temp_dir: Path to temporary directory to remove
    """
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


def process_zip_file(zip_path: Path) -> tuple[List[Path], Path]:
    """Extract a zip file and return all media files with cleanup context.

    Args:
        zip_path: Path to the Google Takeout zip file

    Returns:
        Tuple of (list of media file paths, temp directory path for later cleanup)

    Raises:
        FileNotFoundError: If zip file doesn't exist
        ValueError: If not a valid zip file
        zipfile.BadZipFile: If zip file is corrupted
    """
    temp_dir = create_temp_extraction_dir()

    try:
        extracted_root = extract_zip(zip_path, temp_dir)
        media_files = find_media_files(extracted_root)
        return media_files, temp_dir
    except Exception as e:
        # Clean up on failure
        cleanup_temp_dir(temp_dir)
        raise e
