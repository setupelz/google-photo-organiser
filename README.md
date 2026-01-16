# Google Photo Organiser

[![Build Windows Executable](https://github.com/setupelz/google-photo-organiser/actions/workflows/build-windows.yml/badge.svg)](https://github.com/setupelz/google-photo-organiser/actions/workflows/build-windows.yml)

A standalone Windows executable that organizes Google Takeout photo exports into a clean, browsable directory structure sorted by year and media type.

## What It Does

Google Takeout exports your Google Photos as zip files with a complex nested structure and JSON metadata files. This tool:

- Extracts and processes Google Takeout zip files
- Reads dates from JSON metadata, EXIF data, or file timestamps
- Organizes photos and videos into separate folders by year
- Handles filename conflicts automatically
- Provides progress feedback and summary reports

## Output Structure

```
output/
├── photos/
│   ├── 2020/
│   │   ├── IMG_1234.jpg
│   │   ├── photo.png
│   │   └── ...
│   ├── 2021/
│   └── 2022/
├── videos/
│   ├── 2020/
│   │   ├── video.mp4
│   │   └── ...
│   ├── 2021/
│   └── 2022/
├── processing_report.txt
└── photo_organiser.log
```

## Usage (Windows Executable)

### Basic Usage

Double-click `photo-organiser.exe` or run from command line:

```cmd
photo-organiser.exe takeout-1.zip takeout-2.zip
```

### Custom Output Directory

```cmd
photo-organiser.exe --output D:\MyPhotos takeout-1.zip
```

### Verbose Mode

See detailed processing information:

```cmd
photo-organiser.exe --verbose takeout-1.zip
```

### Help

```cmd
photo-organiser.exe --help
```

## Supported Formats

**Photos:** `.jpg`, `.jpeg`, `.png`, `.heic`, `.webp`, `.gif`

**Videos:** `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`

## Date Detection

The tool uses the most reliable date source available (in priority order):

1. **JSON metadata files** (companion `.json` files from Google Takeout)
2. **EXIF data** (embedded in image files)
3. **File modification date** (fallback for files without metadata)

## Features

- **Handles duplicates:** Automatically renames conflicts (`photo_001.jpg`, `photo_002.jpg`)
- **Progress tracking:** Real-time progress bar during processing
- **Error handling:** Continues processing even if individual files fail
- **Summary reports:** Generates `processing_report.txt` with statistics
- **Logging:** Detailed log file (`photo_organiser.log`) for troubleshooting

## Troubleshooting

### Missing Dates

If files appear in unexpected years, check:
- JSON metadata files may be missing or corrupted
- EXIF data may be stripped from edited photos
- File modification dates may have changed during transfer

### Large Files

Processing very large Takeout exports (multi-GB) may take several minutes. The progress bar will show current status.

### Permission Errors

Ensure you have write permissions for the output directory.

### Disk Space

Verify sufficient disk space for extracted files (roughly 2x the size of your zip files).

## Build from Source (Developers)

### Requirements

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

```bash
# Install dependencies
uv sync

# Run tests
make test

# Build executable
make build
```

The executable will be created in `dist/photo-organiser.exe`.

### Development Commands

```bash
make install      # Install dependencies
make build        # Build Windows executable
make test         # Run tests
make lint         # Run code quality checks
make clean        # Remove generated files
make help         # Show all targets
```

### Project Structure

```
google-photo-organiser/
├── src/photo_organiser/    # Source code
│   ├── main.py             # CLI entry point
│   ├── extractor.py        # Zip extraction
│   ├── metadata.py         # Date extraction
│   ├── organizer.py        # File organization
│   └── config.py           # Configuration
├── tests/                  # Test suite
├── build.spec              # PyInstaller config
├── Makefile                # Build automation
└── pyproject.toml          # Dependencies
```

## CI/CD & Releases

### Automated Builds

Every push to `main`, pull request, and tag triggers an automated build workflow that:

1. Runs the test suite on Windows
2. Builds the Windows executable using PyInstaller
3. Verifies the executable with a smoke test (`--help`)
4. Uploads the build artifact (available for 30 days)

### Creating a Release

To create a new release with an attached executable:

```bash
# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0
```

This triggers the release workflow, which automatically:
- Builds the Windows executable
- Creates a GitHub Release
- Attaches the `.exe` file to the release
- Generates release notes from recent commits

**Tag format:** `v*` (e.g., `v1.0.0`, `v0.2.1`, `v1.0.0-beta`)

### Downloading Build Artifacts

To test a build before creating a release:

1. Navigate to the **Actions** tab in GitHub
2. Select the **Build Windows Executable** workflow
3. Click on a completed workflow run
4. Scroll to **Artifacts** section at the bottom
5. Download `photo-organiser-windows.zip`
6. Extract and test the executable

**Note:** Artifacts expire after 30 days. For permanent builds, create a release tag.

### Manual Workflow Trigger

You can trigger a build manually without pushing code:

1. Navigate to **Actions** tab in GitHub
2. Select **Build Windows Executable** workflow
3. Click **Run workflow** button
4. Select branch and click **Run workflow**

## Technical Details

- Built with Python using PyInstaller for Windows distribution
- Uses Pillow for EXIF reading
- Processes files offline (no cloud dependencies)
- Tested with real Google Takeout exports (multi-GB, 1000+ files)

## License

See LICENSE file for details.

## Support

For issues or questions, create an issue in the project repository.
