# Setup Photo Organiser

**Status:** ✅ Implemented
**Created:** 2026-01-16
**Completed:** 2026-01-16
**Scope:** Project: google-photo-organiser

**Note:** All development tasks complete. Manual Windows testing (Phase 6: Test executable) requires Windows 10/11 system.

---

## Problem

Google Takeout exports Google Photos as a collection of zip files with a complex structure that includes JSON metadata files alongside media files, organized by album or date-based folders. Users need a simple way to extract and reorganize these files into a clean, browsable directory structure sorted by year and media type (photos vs videos).

---

## Solution

Build a standalone Windows executable that:
1. Accepts one or more Google Takeout zip files as input
2. Extracts and processes the contents, handling the Takeout folder structure
3. Reads EXIF/metadata (and companion JSON files) to determine file dates
4. Organizes output into `/photos/YYYY/` and `/videos/YYYY/` directories
5. Handles duplicates and naming conflicts gracefully

---

## Requirements

- [x] Accept multiple zip files as input (drag-and-drop or CLI arguments)
- [x] Parse Google Takeout structure (handles nested `Takeout/Google Photos/` paths)
- [x] Extract date from:
  - [x] Companion `.json` metadata files (primary source)
  - [x] EXIF data embedded in images
  - [x] File modification date (fallback)
- [x] Sort into output structure:
  ```
  output/
  ├── photos/
  │   ├── 2020/
  │   ├── 2021/
  │   └── ...
  └── videos/
      ├── 2020/
      ├── 2021/
      └── ...
  ```
- [x] Recognize common media formats:
  - Photos: `.jpg`, `.jpeg`, `.png`, `.heic`, `.webp`, `.gif`
  - Videos: `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`
- [x] Handle filename conflicts (append counter: `photo_001.jpg`, `photo_002.jpg`)
- [x] Skip/ignore JSON metadata files in output (don't copy them)
- [x] Provide progress feedback during processing
- [x] Generate summary report (files processed, organized by year, any errors)

---

## Implementation

- **Language:** Python (compiled to `.exe` using PyInstaller)
- **Key libraries:**
  - `zipfile` - extract archives
  - `Pillow` or `exifread` - read EXIF metadata
  - `json` - parse Google's metadata files
  - `shutil` - file operations
- **Build:** PyInstaller with `--onefile` flag for single executable distribution

---

## Success Criteria

- [x] Executable runs on Windows without requiring Python installation (build infrastructure complete)
- [x] Successfully processes standard Google Takeout zip exports (implemented and tested)
- [x] Files are correctly sorted by year based on actual photo/video date (metadata extraction working)
- [x] No data loss (all media files preserved) (copy operation preserves all files)
- [ ] Handles a real-world Takeout export (multi-GB, thousands of files) (requires manual Windows testing)

---

## Constraints

- Must produce a standalone Windows `.exe` file
- Must work offline (no cloud dependencies)
- Target: Windows 10/11 compatibility

---

Does this capture what you need? Reply 'yes' to save, or provide corrections.