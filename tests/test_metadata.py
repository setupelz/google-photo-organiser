"""Tests for metadata extraction module."""

import json
from datetime import datetime
from pathlib import Path

import pytest

from photo_organiser.metadata import (
    extract_year,
    get_best_date,
    get_file_modification_date,
    parse_json_metadata,
    read_exif_date,
)

# Test fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestParseJsonMetadata:
    """Test JSON metadata parsing from Google Takeout companion files."""

    def test_parse_valid_json(self):
        """Test parsing valid Google Takeout JSON metadata."""
        json_path = FIXTURES_DIR / "valid_metadata.json"
        result = parse_json_metadata(json_path)

        assert result is not None
        # Timestamp 1577836800 = Jan 1, 2020, 12:00:00 AM UTC
        assert result.year == 2020
        assert result.month == 1
        assert result.day == 1

    def test_parse_malformed_json(self):
        """Test handling of malformed JSON file."""
        json_path = FIXTURES_DIR / "malformed_metadata.json"
        result = parse_json_metadata(json_path)

        assert result is None

    def test_parse_missing_photo_time_field(self):
        """Test handling of JSON missing photoTakenTime field."""
        json_path = FIXTURES_DIR / "missing_photo_time.json"
        result = parse_json_metadata(json_path)

        assert result is None

    def test_parse_nonexistent_file(self):
        """Test handling of non-existent JSON file."""
        json_path = FIXTURES_DIR / "does_not_exist.json"
        result = parse_json_metadata(json_path)

        assert result is None

    def test_parse_missing_timestamp_field(self, tmp_path):
        """Test handling of JSON with photoTakenTime but no timestamp field."""
        # Create JSON with photoTakenTime but missing timestamp
        json_file = tmp_path / "no_timestamp.json"
        json_file.write_text(
            json.dumps(
                {
                    "title": "test.jpg",
                    "photoTakenTime": {
                        "formatted": "Jan 1, 2021, 12:00:00 AM UTC"
                        # timestamp field missing
                    },
                }
            )
        )

        result = parse_json_metadata(json_file)
        assert result is None

    def test_parse_invalid_timestamp_format(self, tmp_path):
        """Test handling of invalid timestamp value."""
        json_file = tmp_path / "invalid_timestamp.json"
        json_file.write_text(
            json.dumps(
                {
                    "title": "test.jpg",
                    "photoTakenTime": {
                        "timestamp": "not_a_number",
                        "formatted": "Invalid",
                    },
                }
            )
        )

        result = parse_json_metadata(json_file)
        assert result is None


class TestReadExifDate:
    """Test EXIF metadata reading from image files."""

    def test_read_exif_from_2020_photo(self):
        """Test reading EXIF date from photo with 2020 timestamp."""
        image_path = FIXTURES_DIR / "photo_with_exif_2020.jpg"
        result = read_exif_date(image_path)

        assert result is not None
        assert result.year == 2020
        assert result.month == 6
        assert result.day == 15

    def test_read_exif_from_2021_photo(self):
        """Test reading EXIF date from photo with 2021 timestamp."""
        image_path = FIXTURES_DIR / "photo_with_exif_2021.jpg"
        result = read_exif_date(image_path)

        assert result is not None
        assert result.year == 2021
        assert result.month == 3
        assert result.day == 20

    def test_read_exif_no_metadata(self):
        """Test reading EXIF from photo without EXIF metadata."""
        image_path = FIXTURES_DIR / "photo_no_exif.jpg"
        result = read_exif_date(image_path)

        # Should return None if no EXIF data
        assert result is None

    def test_read_exif_nonexistent_file(self):
        """Test handling of non-existent image file."""
        image_path = FIXTURES_DIR / "does_not_exist.jpg"
        result = read_exif_date(image_path)

        assert result is None

    def test_read_exif_png_file(self):
        """Test reading EXIF from PNG file (may not have EXIF)."""
        image_path = FIXTURES_DIR / "sample.png"
        result = read_exif_date(image_path)

        # PNG files might not have EXIF data, should handle gracefully
        # Result can be None or a valid date if EXIF exists
        assert result is None or isinstance(result, datetime)

    def test_read_exif_corrupted_file(self, tmp_path):
        """Test handling of corrupted image file."""
        corrupted_file = tmp_path / "corrupted.jpg"
        corrupted_file.write_bytes(b"Not a valid JPEG file")

        result = read_exif_date(corrupted_file)
        assert result is None


class TestGetFileModificationDate:
    """Test file modification date extraction."""

    def test_get_mtime_from_existing_file(self):
        """Test getting modification time from existing file."""
        file_path = FIXTURES_DIR / "valid_metadata.json"
        result = get_file_modification_date(file_path)

        assert isinstance(result, datetime)
        # Should be a reasonable date (after 2000, before 2100)
        assert 2000 <= result.year <= 2100

    def test_get_mtime_returns_datetime(self, tmp_path):
        """Test that returned value is always a datetime object."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        result = get_file_modification_date(test_file)
        assert isinstance(result, datetime)


class TestGetBestDate:
    """Test date extraction with fallback priority logic."""

    def test_priority_json_over_exif(self):
        """Test that JSON metadata takes priority over EXIF."""
        # Create scenario where both JSON and EXIF exist
        # JSON has 2020 date, EXIF would have 2021
        # We need to create a test image with companion JSON

        # Use photo_with_exif_2021.jpg (has 2021 EXIF)
        # Create companion JSON with 2020 timestamp
        import shutil
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Copy image to temp location
            temp_image = tmpdir / "test_photo.jpg"
            shutil.copy(FIXTURES_DIR / "photo_with_exif_2021.jpg", temp_image)

            # Create companion JSON with different date (2020)
            companion_json = tmpdir / "test_photo.jpg.json"
            companion_json.write_text(
                json.dumps(
                    {
                        "title": "test_photo.jpg",
                        "photoTakenTime": {
                            "timestamp": "1577836800",  # Jan 1, 2020
                            "formatted": "Jan 1, 2020, 12:00:00 AM UTC",
                        },
                    }
                )
            )

            result = get_best_date(temp_image)

            # Should use JSON date (2020), not EXIF date (2021)
            assert result.year == 2020

    def test_fallback_to_exif_when_no_json(self):
        """Test fallback to EXIF when JSON doesn't exist."""
        image_path = FIXTURES_DIR / "photo_with_exif_2021.jpg"

        # Ensure no companion JSON exists
        json_path = Path(str(image_path) + ".json")
        assert not json_path.exists()

        result = get_best_date(image_path)

        # Should use EXIF date
        assert result.year == 2021

    def test_fallback_to_mtime_when_no_metadata(self):
        """Test fallback to file modification time when no JSON or EXIF."""
        image_path = FIXTURES_DIR / "photo_no_exif.jpg"

        # Ensure no companion JSON
        json_path = Path(str(image_path) + ".json")
        assert not json_path.exists()

        result = get_best_date(image_path)

        # Should fall back to file modification time
        assert isinstance(result, datetime)
        # File mtime should be recent (test fixture was created recently)
        assert 2020 <= result.year <= 2100

    def test_video_file_uses_json_or_mtime(self):
        """Test that video files skip EXIF and use JSON or mtime."""
        video_path = FIXTURES_DIR / "sample_video.mp4"

        # Video files don't have EXIF, so should skip EXIF check
        result = get_best_date(video_path)

        assert isinstance(result, datetime)
        # Should fall back to file mtime (no JSON exists)
        assert 2020 <= result.year <= 2100

    def test_handles_various_image_formats(self):
        """Test that different image formats are handled correctly."""
        formats_to_test = [
            "photo_with_exif_2020.jpg",
            "photo_with_exif_2021.jpg",
            "sample.png",
        ]

        for filename in formats_to_test:
            file_path = FIXTURES_DIR / filename
            if file_path.exists():
                result = get_best_date(file_path)
                assert isinstance(result, datetime)
                assert 2000 <= result.year <= 2100


class TestExtractYear:
    """Test year extraction from datetime objects."""

    def test_extract_year_from_datetime(self):
        """Test extracting year from datetime object."""
        date = datetime(2021, 6, 15, 14, 30, 0)
        result = extract_year(date)

        assert result == 2021
        assert isinstance(result, int)

    def test_extract_year_various_dates(self):
        """Test year extraction from various dates."""
        test_cases = [
            (datetime(2020, 1, 1), 2020),
            (datetime(2021, 12, 31, 23, 59, 59), 2021),
            (datetime(1999, 7, 15), 1999),
            (datetime(2025, 3, 20), 2025),
        ]

        for date, expected_year in test_cases:
            assert extract_year(date) == expected_year


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_json_file(self, tmp_path):
        """Test handling of empty JSON file."""
        empty_json = tmp_path / "empty.json"
        empty_json.write_text("{}")

        result = parse_json_metadata(empty_json)
        assert result is None

    def test_large_timestamp_value(self, tmp_path):
        """Test handling of very large timestamp (far future date)."""
        json_file = tmp_path / "future.json"
        # Year 2100 timestamp
        json_file.write_text(
            json.dumps(
                {
                    "photoTakenTime": {
                        "timestamp": "4102444800",  # Jan 1, 2100
                        "formatted": "Jan 1, 2100, 12:00:00 AM UTC",
                    }
                }
            )
        )

        result = parse_json_metadata(json_file)
        assert result is not None
        assert result.year == 2100

    def test_negative_timestamp(self, tmp_path):
        """Test handling of negative timestamp (dates before 1970)."""
        json_file = tmp_path / "past.json"
        # Negative timestamp for dates before Unix epoch
        json_file.write_text(
            json.dumps(
                {
                    "photoTakenTime": {
                        "timestamp": "-315619200",  # Jan 1, 1960
                        "formatted": "Jan 1, 1960, 12:00:00 AM UTC",
                    }
                }
            )
        )

        result = parse_json_metadata(json_file)
        # Should handle or return None for negative timestamps
        # Implementation may vary based on platform support
        assert result is None or isinstance(result, datetime)
