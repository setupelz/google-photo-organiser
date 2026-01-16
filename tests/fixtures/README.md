# Test Fixtures

This directory contains sample files used for testing the photo organiser.

## JSON Metadata Files

- **valid_metadata.json** - Complete Google Photos metadata with `photoTakenTime` (2020-01-01)
- **missing_photo_time.json** - Metadata missing `photoTakenTime` field (has only `creationTime`)
- **malformed_metadata.json** - Invalid JSON structure (for error handling tests)

## Image Files

- **photo_with_exif_2020.jpg** - JPEG with EXIF DateTimeOriginal: 2020-06-15
- **photo_with_exif_2021.jpg** - JPEG with EXIF DateTimeOriginal: 2021-03-20
- **photo_no_exif.jpg** - JPEG without EXIF data (tests fallback to mtime)
- **sample.png** - PNG image (tests different image format)

## Video Files

- **sample_video.mp4** - Placeholder MP4 file (for classification testing)
- **sample_video.mov** - Placeholder MOV file (for classification testing)

## Zip Archives

- **sample_takeout.zip** - Mimics Google Takeout structure:
  ```
  Takeout/
  └── Google Photos/
      ├── Photos from 2020/
      │   ├── photo_with_exif_2020.jpg
      │   ├── photo_with_exif_2020.jpg.json
      │   └── video_2020.mp4
      └── Summer Vacation/
          ├── photo_with_exif_2021.jpg
          └── photo_with_exif_2021.jpg.json
  ```
- **empty_takeout.zip** - Empty zip file (edge case)
- **no_media_takeout.zip** - Zip with no media files, only text (edge case)

## Usage in Tests

```python
import os

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')

def test_example():
    json_path = os.path.join(FIXTURES_DIR, 'valid_metadata.json')
    # Use fixture in test...
```
