"""Main entry point for the Google Photos Organiser.

This module provides the CLI interface for processing Google Takeout zip files
and organizing media files by year and type.
"""

import argparse
import logging
import os
import sys
import zipfile
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
from datetime import datetime

from tqdm import tqdm


def get_executable_dir() -> Path:
    """Get the directory containing the executable or script.

    When running as a PyInstaller executable, returns the directory
    containing the .exe file. When running as a script, returns the
    directory containing the script.

    Returns:
        Path to the executable/script directory
    """
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller executable
        return Path(sys.executable).parent
    else:
        # Running as script
        return Path(__file__).parent

from photo_organiser.extractor import process_zip_file, cleanup_temp_dir
from photo_organiser.metadata import get_best_date, extract_year
from photo_organiser.organizer import organize_file, classify_file, UNKNOWN_YEAR
from photo_organiser.config import LARGE_FILE_WARNING_BYTES


def setup_logging(output_dir: Path, verbose: bool) -> logging.Logger:
    """Configure logging for the application.

    Sets up both file and console logging with appropriate levels.
    - File log: Always at DEBUG level, saved to output/photo_organiser.log
    - Console log: INFO level (or DEBUG if verbose=True)

    Args:
        output_dir: Directory where log file will be saved
        verbose: If True, enable DEBUG level console logging

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger('photo_organiser')
    logger.setLevel(logging.DEBUG)

    # Clear any existing handlers
    logger.handlers.clear()

    # File handler - always DEBUG level
    log_file = output_dir / 'photo_organiser.log'
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler - INFO or DEBUG based on verbose flag
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    logger.debug(f"Logging initialized. Log file: {log_file}")
    return logger


def validate_zip_file(zip_path: Path) -> bool:
    """Validate that a file is a valid zip file.

    Args:
        zip_path: Path to check

    Returns:
        True if valid, False otherwise
    """
    if not zip_path.exists():
        print(f"Error: File not found: {zip_path}", file=sys.stderr)
        return False

    if not zip_path.is_file():
        print(f"Error: Not a file: {zip_path}", file=sys.stderr)
        return False

    if not zipfile.is_zipfile(zip_path):
        print(f"Error: Not a valid zip file: {zip_path}", file=sys.stderr)
        return False

    return True


def process_single_zip(
    zip_path: Path,
    output_dir: Path,
    logger: logging.Logger
) -> tuple[int, int, int, int, List[str], Dict[str, Dict[str, int]]]:
    """Process a single zip file.

    Args:
        zip_path: Path to zip file
        output_dir: Output directory for organized files
        logger: Logger instance for logging

    Returns:
        Tuple of (files_processed, files_organized, metadata_skipped, unrecognized_skipped, errors, files_by_year)
        files_by_year is a dict of {year_str: {'photos': count, 'videos': count}}
    """
    logger.info(f"Extracting {zip_path.name}...")

    errors = []
    files_processed = 0
    files_organized = 0
    metadata_skipped = 0
    unrecognized_skipped = 0
    files_by_year: Dict[str, Dict[str, int]] = defaultdict(lambda: {'photos': 0, 'videos': 0})

    try:
        # Extract zip and get media files
        logger.debug(f"Starting extraction of {zip_path}")
        media_files, temp_dir = process_zip_file(zip_path)
        logger.info(f"Found {len(media_files)} files to process")

        # Check for empty zip files
        if len(media_files) == 0:
            logger.warning(f"No files found in {zip_path.name}")
            return 0, 0, 0, 0, [], {}

        # Create progress bar (only show if not in DEBUG mode)
        show_progress = logger.level > logging.DEBUG
        progress_bar = tqdm(
            media_files,
            desc=f"Processing {zip_path.name}",
            unit="file",
            disable=not show_progress
        )

        # Process each file
        for media_file in progress_bar:
            files_processed += 1

            try:
                # Check file type first to track skipped files
                file_type = classify_file(media_file)
                if file_type == 'metadata':
                    metadata_skipped += 1
                    logger.debug(f"Skipping metadata file: {media_file.name}")
                    continue
                elif file_type is None:
                    unrecognized_skipped += 1
                    logger.debug(f"Skipping unrecognized file: {media_file.name}")
                    continue

                # Check file size and warn for very large files
                file_size = media_file.stat().st_size
                if file_size > LARGE_FILE_WARNING_BYTES:
                    size_gb = file_size / (1024 * 1024 * 1024)
                    logger.warning(
                        f"Large file detected: {media_file.name} ({size_gb:.2f} GB) - "
                        f"copying may take significant time"
                    )

                # Get date and year
                date = get_best_date(media_file)
                if date is not None:
                    year = extract_year(date)
                    year_key = str(year)
                else:
                    year = UNKNOWN_YEAR
                    year_key = UNKNOWN_YEAR

                logger.debug(f"Processing: {media_file.name} (year: {year_key})")

                if show_progress:
                    # Update progress bar description with current file
                    progress_bar.set_postfix_str(f"{media_file.name[:30]}...")

                # Organize the file
                result = organize_file(media_file, year, output_dir)

                if result is not None:
                    files_organized += 1
                    file_type, dest_path = result

                    # Track by year and type
                    if file_type == 'photo':
                        files_by_year[year_key]['photos'] += 1
                    elif file_type == 'video':
                        files_by_year[year_key]['videos'] += 1

                    logger.debug(f"Organized {file_type}: {dest_path.relative_to(output_dir)}")

            except PermissionError as e:
                error_msg = f"Permission denied: {media_file.name} - {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
            except OSError as e:
                # Check if disk space issue
                if "No space left on device" in str(e) or "Insufficient disk space" in str(e):
                    error_msg = f"Disk space exhausted while processing {media_file.name}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                    # Stop processing if out of disk space
                    logger.error("Stopping processing due to insufficient disk space")
                    break
                else:
                    error_msg = f"File system error processing {media_file.name}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            except ValueError as e:
                error_msg = f"Invalid data in {media_file.name}: {str(e)}"
                errors.append(error_msg)
                logger.warning(error_msg)
            except Exception as e:
                error_msg = f"Unexpected error processing {media_file.name}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg, exc_info=True)

        # Close progress bar
        progress_bar.close()

        # Cleanup temporary directory
        logger.debug(f"Cleaning up temporary directory: {temp_dir}")
        cleanup_temp_dir(temp_dir)
        logger.info(f"Completed processing {zip_path.name}: {files_organized}/{files_processed} files organized")

    except zipfile.BadZipFile as e:
        error_msg = f"Corrupted or invalid zip file {zip_path.name}: {str(e)}"
        errors.append(error_msg)
        logger.error(error_msg)
    except PermissionError as e:
        error_msg = f"Permission denied accessing {zip_path.name}: {str(e)}"
        errors.append(error_msg)
        logger.error(error_msg)
    except OSError as e:
        if "No space left on device" in str(e) or "Insufficient disk space" in str(e):
            error_msg = f"Insufficient disk space to process {zip_path.name}"
            errors.append(error_msg)
            logger.error(error_msg)
        else:
            error_msg = f"File system error processing {zip_path.name}: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error processing zip {zip_path.name}: {str(e)}"
        errors.append(error_msg)
        logger.error(error_msg, exc_info=True)

    return files_processed, files_organized, metadata_skipped, unrecognized_skipped, errors, files_by_year


def generate_summary_report(
    output_dir: Path,
    total_processed: int,
    total_organized: int,
    metadata_skipped: int,
    unrecognized_skipped: int,
    all_errors: List[str],
    files_by_year: Dict[str, Dict[str, int]]
) -> None:
    """Generate and save processing summary report.

    Args:
        output_dir: Output directory where report will be saved
        total_processed: Total files processed
        total_organized: Total files organized
        metadata_skipped: Number of metadata (JSON) files skipped
        unrecognized_skipped: Number of unrecognized file types skipped
        all_errors: List of error messages
        files_by_year: Dictionary of files organized by year and type
    """
    report_path = output_dir / "processing_report.txt"

    with open(report_path, 'w', encoding='utf-8') as f:
        # Header
        f.write("=" * 60 + "\n")
        f.write("Google Photos Organiser - Processing Report\n")
        f.write("=" * 60 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("\n")

        # Summary statistics
        f.write("Summary\n")
        f.write("-" * 60 + "\n")
        f.write(f"Total files found:      {total_processed:,}\n")
        f.write(f"  Photos/videos:        {total_organized:,}\n")
        f.write(f"  Metadata files:       {metadata_skipped:,} (skipped)\n")
        f.write(f"  Unrecognized:         {unrecognized_skipped:,} (skipped)\n")
        f.write(f"Errors encountered:     {len(all_errors):,}\n")
        f.write("\n")

        # Files by year
        if files_by_year:
            f.write("Files Organized by Year\n")
            f.write("-" * 60 + "\n")

            # Sort years for consistent output (UnknownYear at the end)
            def year_sort_key(y):
                if y == UNKNOWN_YEAR:
                    return (1, y)  # Put UnknownYear at the end
                return (0, y)
            sorted_years = sorted(files_by_year.keys(), key=year_sort_key)

            # Calculate totals
            total_photos = sum(data['photos'] for data in files_by_year.values())
            total_videos = sum(data['videos'] for data in files_by_year.values())

            # Year breakdown
            f.write(f"{'Year':<10} {'Photos':<15} {'Videos':<15} {'Total':<10}\n")
            f.write("-" * 60 + "\n")

            for year in sorted_years:
                photos = files_by_year[year]['photos']
                videos = files_by_year[year]['videos']
                total = photos + videos
                f.write(f"{year:<10} {photos:<15,} {videos:<15,} {total:<10,}\n")

            f.write("-" * 60 + "\n")
            f.write(f"{'TOTAL':<10} {total_photos:<15,} {total_videos:<15,} {total_organized:<10,}\n")
            f.write("\n")

        # Error details
        if all_errors:
            f.write("Errors\n")
            f.write("-" * 60 + "\n")
            for i, error in enumerate(all_errors, 1):
                f.write(f"{i}. {error}\n")
            f.write("\n")

        # Footer
        f.write("=" * 60 + "\n")
        f.write(f"Report saved to: {report_path.absolute()}\n")


def main() -> int:
    """Main entry point for the photo organiser CLI.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description="Organize Google Photos from Takeout exports by year and media type",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s export1.zip export2.zip
  %(prog)s *.zip --output ~/Photos/organized
  %(prog)s takeout.zip --verbose
        """
    )

    parser.add_argument(
        'zip_files',
        nargs='+',
        type=Path,
        help='One or more Google Takeout zip files to process'
    )

    parser.add_argument(
        '-o', '--output',
        type=Path,
        default=get_executable_dir() / 'output',
        help='Output directory for organized photos (default: ./output next to executable)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 0.1.0'
    )

    args = parser.parse_args()

    # Create output directory if it doesn't exist
    args.output.mkdir(parents=True, exist_ok=True)

    # Setup logging
    logger = setup_logging(args.output, args.verbose)

    # Validate input files
    valid_zips = []
    for zip_file in args.zip_files:
        if validate_zip_file(zip_file):
            valid_zips.append(zip_file)
            logger.debug(f"Validated zip file: {zip_file}")
        else:
            logger.warning(f"Skipping invalid zip file: {zip_file}")

    if not valid_zips:
        logger.error("No valid zip files to process")
        return 1

    logger.info("Photo Organiser v0.1.0")
    logger.info(f"Processing {len(valid_zips)} zip file(s)...")
    logger.info(f"Output directory: {args.output.absolute()}")

    if args.verbose:
        logger.debug("Verbose mode enabled")
        logger.debug("Input files:")
        for zip_file in valid_zips:
            logger.debug(f"  - {zip_file.absolute()}")

    # Process all zip files
    total_processed = 0
    total_organized = 0
    total_metadata_skipped = 0
    total_unrecognized_skipped = 0
    all_errors = []
    all_files_by_year: Dict[str, Dict[str, int]] = defaultdict(lambda: {'photos': 0, 'videos': 0})

    for zip_file in valid_zips:
        processed, organized, metadata_skipped, unrecognized_skipped, errors, files_by_year = process_single_zip(
            zip_file,
            args.output,
            logger
        )
        total_processed += processed
        total_organized += organized
        total_metadata_skipped += metadata_skipped
        total_unrecognized_skipped += unrecognized_skipped
        all_errors.extend(errors)

        # Merge files_by_year into all_files_by_year
        for year, counts in files_by_year.items():
            all_files_by_year[year]['photos'] += counts['photos']
            all_files_by_year[year]['videos'] += counts['videos']

    # Generate summary report
    logger.debug("Generating summary report...")
    generate_summary_report(
        args.output,
        total_processed,
        total_organized,
        total_metadata_skipped,
        total_unrecognized_skipped,
        all_errors,
        all_files_by_year
    )

    # Print summary
    print(f"\n{'='*60}")
    print("Processing Complete")
    print(f"{'='*60}")
    print(f"Total files found:      {total_processed:,}")
    print(f"  Photos/videos:        {total_organized:,}")
    print(f"  Metadata files:       {total_metadata_skipped:,} (skipped)")
    print(f"  Unrecognized:         {total_unrecognized_skipped:,} (skipped)")

    # Print year breakdown if available
    if all_files_by_year:
        print(f"\nFiles by year:")
        # Sort years (UnknownYear at the end)
        def year_sort_key(y):
            if y == UNKNOWN_YEAR:
                return (1, y)
            return (0, y)
        sorted_years = sorted(all_files_by_year.keys(), key=year_sort_key)
        for year in sorted_years:
            photos = all_files_by_year[year]['photos']
            videos = all_files_by_year[year]['videos']
            total = photos + videos
            print(f"  {year}: {total:,} files ({photos:,} photos, {videos:,} videos)")

    if all_errors:
        print(f"\nErrors encountered: {len(all_errors)}")
        if not args.verbose:
            print("Run with --verbose to see error details")
        else:
            print("\nError details:")
            for error in all_errors:
                print(f"  - {error}")

    # Print report location
    print(f"\nDetailed report saved to: {args.output / 'processing_report.txt'}")

    return 0 if not all_errors else 1


if __name__ == '__main__':
    sys.exit(main())
