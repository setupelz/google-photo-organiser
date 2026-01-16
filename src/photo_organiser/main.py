"""Main entry point for the Google Photos Organiser.

This module provides the CLI interface for processing Google Takeout zip files
and organizing media files by year and type.
"""

import argparse
import sys
from pathlib import Path


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
    for zip_file in args.zip_files:
        if not zip_file.exists():
            print(f"Error: File not found: {zip_file}", file=sys.stderr)
            return 1
        if not zip_file.is_file():
            print(f"Error: Not a file: {zip_file}", file=sys.stderr)
            return 1

    # Create output directory if it doesn't exist
    args.output.mkdir(parents=True, exist_ok=True)

    print(f"Photo Organiser v0.1.0")
    print(f"Processing {len(args.zip_files)} zip file(s)...")
    print(f"Output directory: {args.output.absolute()}")

    if args.verbose:
        print("\nVerbose mode enabled")
        print(f"Input files:")
        for zip_file in args.zip_files:
            print(f"  - {zip_file.absolute()}")

    # TODO: Implement processing logic in Phase 2
    print("\n[Processing not yet implemented - Phase 2 pending]")

    return 0


if __name__ == '__main__':
    sys.exit(main())
