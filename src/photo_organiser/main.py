"""Main entry point for the Google Photos Organiser.

This module provides the CLI interface for processing Google Takeout zip files
and organizing media files by year and type.
"""

import argparse
import sys
import zipfile
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
from datetime import datetime

from tqdm import tqdm

from .extractor import process_zip_file, cleanup_temp_dir
from .metadata import get_best_date, extract_year
from .organizer import organize_file


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
    verbose: bool
) -> tuple[int, int, List[str], Dict[int, Dict[str, int]]]:
    """Process a single zip file.

    Args:
        zip_path: Path to zip file
        output_dir: Output directory for organized files
        verbose: Enable verbose logging

    Returns:
        Tuple of (files_processed, files_organized, errors, files_by_year)
        files_by_year is a dict of {year: {'photos': count, 'videos': count}}
    """
    if verbose:
        print(f"\nExtracting {zip_path.name}...")

    errors = []
    files_processed = 0
    files_organized = 0
    files_by_year: Dict[int, Dict[str, int]] = defaultdict(lambda: {'photos': 0, 'videos': 0})

    try:
        # Extract zip and get media files
        media_files, temp_dir = process_zip_file(zip_path)

        if verbose:
            print(f"Found {len(media_files)} files to process")

        # Create progress bar
        progress_bar = tqdm(
            media_files,
            desc=f"Processing {zip_path.name}",
            unit="file",
            disable=verbose  # Disable if verbose mode (to avoid conflicts with detailed output)
        )

        # Process each file
        for media_file in progress_bar:
            files_processed += 1

            try:
                # Get date and year
                date = get_best_date(media_file)
                year = extract_year(date)

                if verbose:
                    print(f"Processing: {media_file.name} (year: {year})")
                else:
                    # Update progress bar description with current file
                    progress_bar.set_postfix_str(f"{media_file.name[:30]}...")

                # Organize the file
                result = organize_file(media_file, year, output_dir)

                if result is not None:
                    files_organized += 1
                    file_type, dest_path = result

                    # Track by year and type
                    if file_type == 'photo':
                        files_by_year[year]['photos'] += 1
                    elif file_type == 'video':
                        files_by_year[year]['videos'] += 1

                    if verbose:
                        print(f"  → {file_type}: {dest_path.relative_to(output_dir)}")

            except Exception as e:
                error_msg = f"Error processing {media_file.name}: {str(e)}"
                errors.append(error_msg)
                if verbose:
                    print(f"  ! {error_msg}", file=sys.stderr)

        # Close progress bar
        progress_bar.close()

        # Cleanup temporary directory
        cleanup_temp_dir(temp_dir)

    except Exception as e:
        error_msg = f"Error processing zip {zip_path.name}: {str(e)}"
        errors.append(error_msg)
        print(error_msg, file=sys.stderr)

    return files_processed, files_organized, errors, files_by_year


def generate_summary_report(
    output_dir: Path,
    total_processed: int,
    total_organized: int,
    all_errors: List[str],
    files_by_year: Dict[int, Dict[str, int]]
) -> None:
    """Generate and save processing summary report.

    Args:
        output_dir: Output directory where report will be saved
        total_processed: Total files processed
        total_organized: Total files organized
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
        f.write(f"Total files processed:  {total_processed:,}\n")
        f.write(f"Files organized:        {total_organized:,}\n")
        f.write(f"Files skipped:          {total_processed - total_organized:,}\n")
        f.write(f"Errors encountered:     {len(all_errors):,}\n")
        f.write("\n")

        # Files by year
        if files_by_year:
            f.write("Files Organized by Year\n")
            f.write("-" * 60 + "\n")

            # Sort years for consistent output
            sorted_years = sorted(files_by_year.keys())

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
        default=Path('./output'),
        help='Output directory for organized photos (default: ./output)'
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

    # Validate input files
    valid_zips = []
    for zip_file in args.zip_files:
        if validate_zip_file(zip_file):
            valid_zips.append(zip_file)

    if not valid_zips:
        print("Error: No valid zip files to process", file=sys.stderr)
        return 1

    # Create output directory if it doesn't exist
    args.output.mkdir(parents=True, exist_ok=True)

    print(f"Photo Organiser v0.1.0")
    print(f"Processing {len(valid_zips)} zip file(s)...")
    print(f"Output directory: {args.output.absolute()}")

    if args.verbose:
        print("\nVerbose mode enabled")
        print(f"Input files:")
        for zip_file in valid_zips:
            print(f"  - {zip_file.absolute()}")

    # Process all zip files
    total_processed = 0
    total_organized = 0
    all_errors = []
    all_files_by_year: Dict[int, Dict[str, int]] = defaultdict(lambda: {'photos': 0, 'videos': 0})

    for zip_file in valid_zips:
        processed, organized, errors, files_by_year = process_single_zip(
            zip_file,
            args.output,
            args.verbose
        )
        total_processed += processed
        total_organized += organized
        all_errors.extend(errors)

        # Merge files_by_year into all_files_by_year
        for year, counts in files_by_year.items():
            all_files_by_year[year]['photos'] += counts['photos']
            all_files_by_year[year]['videos'] += counts['videos']

    # Generate summary report
    generate_summary_report(
        args.output,
        total_processed,
        total_organized,
        all_errors,
        all_files_by_year
    )

    # Print summary
    print(f"\n{'='*60}")
    print("Processing Complete")
    print(f"{'='*60}")
    print(f"Total files processed: {total_processed:,}")
    print(f"Files organized: {total_organized:,}")
    print(f"Files skipped: {total_processed - total_organized:,}")

    # Print year breakdown if available
    if all_files_by_year:
        print(f"\nFiles by year:")
        sorted_years = sorted(all_files_by_year.keys())
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
