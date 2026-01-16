# Implementation Plan

**Generated:** 2026-01-16
**Spec:** `specs/setup-photo-organiser.md`

---

## Current Focus: Photo Organiser Core Functionality

Build a standalone Windows executable that processes Google Takeout zip files and organizes media files by year and type.

---

## Phase 1: Project Setup and Dependencies

### Tasks

- [x] Update `pyproject.toml` with required dependencies:
  - `Pillow` for EXIF reading
  - `pyinstaller` for executable creation
  - `tqdm` for progress bars
  - Remove unused research dependencies (pandas, numpy, matplotlib, seaborn, scipy, jupyter)
- [x] Create `src/photo_organiser/` package structure
- [x] Create `src/photo_organiser/__init__.py`
- [x] Create `src/photo_organiser/main.py` entry point
- [x] Remove placeholder research scripts (`scripts/01-acquire.py`, `02-clean.py`, `03-analyze.py`, `04-visualize.py`)

### Verification
- `uv sync` completes successfully
- Project structure is clean

---

## Phase 2: Core Processing Logic

### Tasks

- [x] Create `src/photo_organiser/extractor.py`:
  - Function to extract zip files to temporary directory
  - Handle Google Takeout nested structure (`Takeout/Google Photos/`)
  - Clean up temporary files after processing
- [x] Create `src/photo_organiser/metadata.py`:
  - Function to parse companion JSON files (extract `photoTakenTime` field)
  - Function to read EXIF data from images using Pillow (`DateTimeOriginal` tag)
  - Function to extract file modification date (fallback)
  - Function to determine best date source (priority: JSON > EXIF > file mtime)
  - Return year from extracted date
- [x] Create `src/photo_organiser/organizer.py`:
  - Function to classify files into photos vs videos (by extension)
  - Function to generate output path: `photos/YYYY/` or `videos/YYYY/`
  - Function to handle filename conflicts (append counter `_001`, `_002`, etc.)
  - Function to copy files to organized structure
  - Skip JSON metadata files in output
- [x] Create `src/photo_organiser/config.py`:
  - Define photo extensions: `.jpg`, `.jpeg`, `.png`, `.heic`, `.webp`, `.gif`
  - Define video extensions: `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`
  - Define default output directory path

### Verification
- Unit tests pass for each module
- Can extract a sample zip file
- Can parse metadata correctly
- Files organized into correct year folders

---

## Phase 3: CLI Interface and Progress Reporting

### Tasks

- [x] Implement CLI in `main.py`:
  - Use `argparse` to accept multiple zip file paths
  - Add `--output` flag for custom output directory (default: `./output/`)
  - Add `--verbose` flag for detailed logging
  - Validate input files exist and are valid zip files
- [x] Add progress reporting:
  - Use `tqdm` library for progress bar
  - Track files processed vs total files
  - Display current file being processed in verbose mode
- [x] Generate summary report:
  - Count total files processed
  - Count files organized by year
  - List any errors or skipped files
  - Save report to `output/processing_report.txt`
  - Print summary to console

### Verification
- Can run: `python -m photo_organiser file1.zip file2.zip`
- Progress bar displays during processing
- Summary report generated and accurate

---

## Phase 4: Testing

### Tasks

- [x] Create `tests/test_metadata.py`:
  - Test JSON parsing with valid data
  - Test JSON parsing with missing/malformed data
  - Test EXIF reading from sample images
  - Test date fallback logic (JSON > EXIF > mtime)
  - Test year extraction from various date formats
- [x] Create `tests/test_organizer.py`:
  - Test file classification (photo vs video) for all extensions
  - Test path generation for different years and media types
  - Test duplicate handling (append counter logic)
  - Test JSON file skipping
- [x] Create `tests/test_extractor.py`:
  - Test zip extraction to temporary directory
  - Test handling of Takeout nested structure
  - Test cleanup of temporary files
- [x] Create test fixtures in `tests/fixtures/`:
  - Sample JPEG images with EXIF data
  - Sample JSON metadata files (Google format)
  - Sample zip mimicking Google Takeout structure
  - Edge cases: no metadata, corrupted files, etc.

### Verification
- `pytest` passes all tests
- Code coverage >80% on core modules

---

## Phase 5: Error Handling and Robustness

### Tasks

- [x] Add error handling for:
  - Corrupted or invalid zip files
  - Missing or malformed JSON metadata
  - Images without EXIF data
  - Disk space issues (catch `OSError`)
  - Permission errors during file operations
  - Invalid file formats (unknown extensions)
- [x] Add logging system:
  - Use Python `logging` module
  - Log to file: `output/photo_organiser.log`
  - Log level controlled by `--verbose` flag
  - Log all errors, warnings, and processing steps
- [x] Handle edge cases:
  - Empty zip files
  - Zip files without media files
  - Files with same name but different dates
  - Very large files (multi-GB videos)

### Verification
- Error messages are clear and actionable
- Log file aids troubleshooting
- App gracefully handles edge cases without crashing

---

## Phase 6: Windows Executable Build

### Tasks

- [x] Create `build.spec` for PyInstaller:
  - Configure `--onefile` mode for single executable
  - Set entry point to `src/photo_organiser/main.py`
  - Bundle all dependencies (Pillow, etc.)
  - Set console mode (not windowed)
  - Optional: Add icon file
- [x] Create `build.py` or Makefile target:
  - Automate PyInstaller build process
  - Clean previous builds before building
  - Copy executable to `dist/photo-organiser.exe`
- [ ] Test executable:
  - Run on Windows 10/11 without Python installed
  - Test with real Google Takeout export
  - Verify output structure correctness
  - Check executable size (should be <50MB)

### Verification
- `pyinstaller build.spec` completes successfully
- `dist/photo-organiser.exe` runs standalone
- Processes real Google Takeout export without errors

---

## Phase 7: Documentation

### Tasks

- [ ] Update `README.md`:
  - Replace research template content
  - Add project description and purpose
  - Add usage instructions for end users (Windows executable)
  - Add build instructions for developers
  - Add example commands
  - Add troubleshooting section
- [ ] Create `docs/build.md`:
  - Detailed build instructions
  - PyInstaller configuration explanation
  - Development setup (uv, Python version)
- [ ] Add inline documentation:
  - Docstrings for all functions (Google style)
  - Type hints throughout
  - Comments for complex logic (metadata parsing, conflict resolution)

### Verification
- README is clear for non-technical users
- Developers can build from source following docs
- Code is well-documented

---

## Critical Files

1. `src/photo_organiser/main.py` — CLI entry point, orchestrates processing
2. `src/photo_organiser/extractor.py` — Zip extraction and Takeout structure handling
3. `src/photo_organiser/metadata.py` — Date extraction from JSON/EXIF/file
4. `src/photo_organiser/organizer.py` — File classification and organization logic
5. `src/photo_organiser/config.py` — Configuration constants (file extensions, paths)
6. `pyproject.toml` — Dependencies and project metadata
7. `build.spec` — PyInstaller configuration
8. `tests/` — Test suite with fixtures

---

## Assumptions

- Using Pillow for EXIF reading (well-maintained, pure Python, cross-platform)
- PyInstaller for executable creation (industry standard for Python-to-exe)
- Using `tqdm` for progress bars (lightweight, widely used)
- Output directory defaults to `./output/` (configurable via `--output` flag)
- Processing is offline (no network/cloud dependencies)
- Google Takeout JSON format has `photoTakenTime` field (standard in Google Photos exports)
- Using `pytest` for testing framework
- Target Python 3.11+ (as specified in pyproject.toml)
- Temporary extraction directory cleaned up after processing
- Files copied (not moved) to preserve originals in zip
- HEIC format may have limited EXIF support (depends on Pillow version)

---

## Technical Notes

**Date Extraction Priority:**
1. Companion JSON files (`photoTakenTime` field) — most reliable
2. EXIF metadata (`DateTimeOriginal` tag) — embedded in images
3. File modification time — last resort fallback

**Google Takeout Structure:**
```
Takeout.zip
└── Takeout/
    └── Google Photos/
        ├── Album Name/
        │   ├── photo.jpg
        │   ├── photo.jpg.json
        │   └── ...
        └── Photos from 2020/
            ├── IMG_1234.jpg
            ├── IMG_1234.jpg.json
            └── ...
```

**Output Structure:**
```
output/
├── photos/
│   ├── 2020/
│   │   ├── photo.jpg
│   │   ├── IMG_1234.jpg
│   │   └── ...
│   ├── 2021/
│   └── ...
├── videos/
│   ├── 2020/
│   │   ├── video.mp4
│   │   └── ...
│   ├── 2021/
│   └── ...
├── processing_report.txt
└── photo_organiser.log
```

---

## Post-Implementation

After all phases complete:
1. Update `specs/setup-photo-organiser.md` status from `📋 Planned` to `✅ Complete`
2. Add completion date to spec
3. Test with real-world Google Takeout export (multi-GB, 1000+ files)
4. Document any limitations or known issues in README
