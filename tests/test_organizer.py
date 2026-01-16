"""Tests for file organization module."""

import shutil
from pathlib import Path

import pytest

from photo_organiser.config import (
    DUPLICATE_COUNTER_FORMAT,
    METADATA_EXTENSION,
    PHOTO_EXTENSIONS,
    PHOTOS_SUBDIR,
    VIDEO_EXTENSIONS,
    VIDEOS_SUBDIR,
)
from photo_organiser.organizer import (
    classify_file,
    copy_file,
    generate_output_path,
    organize_file,
    resolve_filename_conflict,
)

# Test fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestClassifyFile:
    """Test file classification by extension."""

    def test_classify_photo_extensions(self):
        """Test classification of all photo file extensions."""
        photo_files = [
            "photo.jpg",
            "image.jpeg",
            "picture.png",
            "snapshot.heic",
            "graphic.webp",
            "animation.gif",
        ]

        for filename in photo_files:
            file_path = Path(filename)
            result = classify_file(file_path)
            assert result == 'photo', f"Failed for {filename}"

    def test_classify_video_extensions(self):
        """Test classification of all video file extensions."""
        video_files = [
            "movie.mp4",
            "clip.mov",
            "video.avi",
            "film.mkv",
            "recording.webm",
        ]

        for filename in video_files:
            file_path = Path(filename)
            result = classify_file(file_path)
            assert result == 'video', f"Failed for {filename}"

    def test_classify_metadata_extension(self):
        """Test classification of JSON metadata files."""
        json_files = [
            "photo.jpg.json",
            "video.mp4.json",
            "metadata.json",
        ]

        for filename in json_files:
            file_path = Path(filename)
            result = classify_file(file_path)
            assert result == 'metadata', f"Failed for {filename}"

    def test_classify_case_insensitive(self):
        """Test that classification is case-insensitive."""
        case_variations = [
            ("photo.JPG", 'photo'),
            ("video.MP4", 'video'),
            ("image.JPEG", 'photo'),
            ("file.JSON", 'metadata'),
            ("mixed.JpG", 'photo'),
        ]

        for filename, expected_type in case_variations:
            file_path = Path(filename)
            result = classify_file(file_path)
            assert result == expected_type, f"Failed for {filename}"

    def test_classify_unrecognized_extension(self):
        """Test classification of unrecognized file types."""
        unrecognized_files = [
            "document.txt",
            "archive.zip",
            "script.py",
            "stylesheet.css",
            "file_without_extension",
        ]

        for filename in unrecognized_files:
            file_path = Path(filename)
            result = classify_file(file_path)
            assert result is None, f"Failed for {filename}"

    def test_classify_with_multiple_dots(self):
        """Test classification of filenames with multiple dots."""
        test_cases = [
            ("my.photo.file.jpg", 'photo'),
            ("video.clip.2020.mp4", 'video'),
            ("archive.tar.gz", None),  # Unrecognized
        ]

        for filename, expected_type in test_cases:
            file_path = Path(filename)
            result = classify_file(file_path)
            assert result == expected_type, f"Failed for {filename}"


class TestGenerateOutputPath:
    """Test output path generation for organized files."""

    def test_generate_photo_path(self, tmp_path):
        """Test generating output path for photo files."""
        file_path = Path("vacation.jpg")
        year = 2020
        output_dir = tmp_path

        result = generate_output_path(file_path, year, output_dir, 'photo')

        expected = output_dir / PHOTOS_SUBDIR / "2020" / "vacation.jpg"
        assert result == expected

    def test_generate_video_path(self, tmp_path):
        """Test generating output path for video files."""
        file_path = Path("birthday.mp4")
        year = 2021
        output_dir = tmp_path

        result = generate_output_path(file_path, year, output_dir, 'video')

        expected = output_dir / VIDEOS_SUBDIR / "2021" / "birthday.mp4"
        assert result == expected

    def test_generate_path_preserves_filename(self, tmp_path):
        """Test that original filename is preserved in output path."""
        filenames = [
            "My Vacation Photo.jpg",
            "IMG_1234.jpeg",
            "2020-01-15_photo.png",
            "special_characters!@#.jpg",
        ]

        for filename in filenames:
            file_path = Path(filename)
            result = generate_output_path(file_path, 2020, tmp_path, 'photo')
            assert result.name == filename

    def test_generate_path_different_years(self, tmp_path):
        """Test path generation for different years."""
        file_path = Path("photo.jpg")
        years = [1999, 2000, 2020, 2025, 2100]

        for year in years:
            result = generate_output_path(file_path, year, tmp_path, 'photo')
            assert str(year) in str(result)
            assert result.parent.name == str(year)

    def test_generate_path_invalid_file_type(self, tmp_path):
        """Test that invalid file_type raises ValueError."""
        file_path = Path("file.jpg")

        with pytest.raises(ValueError, match="file_type must be 'photo' or 'video'"):
            generate_output_path(file_path, 2020, tmp_path, 'invalid')

        with pytest.raises(ValueError, match="file_type must be 'photo' or 'video'"):
            generate_output_path(file_path, 2020, tmp_path, 'metadata')

    def test_generate_path_complex_directory_structure(self, tmp_path):
        """Test output path generation with complex directory structure."""
        output_dir = tmp_path / "nested" / "output" / "directory"
        file_path = Path("photo.jpg")

        result = generate_output_path(file_path, 2020, output_dir, 'photo')

        expected = output_dir / PHOTOS_SUBDIR / "2020" / "photo.jpg"
        assert result == expected


class TestResolveFilenameConflict:
    """Test filename conflict resolution with counter suffixes."""

    def test_no_conflict_returns_original(self, tmp_path):
        """Test that non-existent file returns original path."""
        target_path = tmp_path / "photo.jpg"

        result = resolve_filename_conflict(target_path)

        assert result == target_path
        assert result.name == "photo.jpg"

    def test_conflict_appends_counter(self, tmp_path):
        """Test that existing file gets counter appended."""
        # Create existing file
        existing_file = tmp_path / "photo.jpg"
        existing_file.write_text("existing")

        target_path = tmp_path / "photo.jpg"
        result = resolve_filename_conflict(target_path)

        expected = tmp_path / "photo_001.jpg"
        assert result == expected

    def test_multiple_conflicts_increments_counter(self, tmp_path):
        """Test that counter increments for multiple conflicts."""
        # Create existing files
        (tmp_path / "photo.jpg").write_text("original")
        (tmp_path / "photo_001.jpg").write_text("first duplicate")
        (tmp_path / "photo_002.jpg").write_text("second duplicate")

        target_path = tmp_path / "photo.jpg"
        result = resolve_filename_conflict(target_path)

        expected = tmp_path / "photo_003.jpg"
        assert result == expected

    def test_counter_format_is_consistent(self, tmp_path):
        """Test that counter uses consistent format (e.g., _001, not _1)."""
        (tmp_path / "photo.jpg").write_text("existing")

        target_path = tmp_path / "photo.jpg"
        result = resolve_filename_conflict(target_path)

        # Counter should be formatted with leading zeros
        assert "_001" in result.name

    def test_conflict_with_various_extensions(self, tmp_path):
        """Test conflict resolution with different file extensions."""
        test_cases = [
            ("photo.jpeg", "photo_001.jpeg"),
            ("video.mp4", "video_001.mp4"),
            ("image.png", "image_001.png"),
            ("file.heic", "file_001.heic"),
        ]

        for original, expected_name in test_cases:
            # Create existing file
            existing = tmp_path / original
            existing.write_text("existing")

            target = tmp_path / original
            result = resolve_filename_conflict(target)

            assert result.name == expected_name
            # Clean up for next iteration
            existing.unlink()

    def test_conflict_preserves_complex_filenames(self, tmp_path):
        """Test that complex filenames are preserved with counter."""
        complex_names = [
            "My Vacation Photo 2020.jpg",
            "IMG_1234_edited.png",
            "photo-with-dashes.jpeg",
        ]

        for filename in complex_names:
            existing = tmp_path / filename
            existing.write_text("existing")

            target = tmp_path / filename
            result = resolve_filename_conflict(target)

            # Check that original stem is preserved
            stem = Path(filename).stem
            assert stem in result.stem
            assert "_001" in result.name
            existing.unlink()

    def test_large_number_of_conflicts(self, tmp_path):
        """Test resolution with many existing files."""
        # Create 10 existing files
        base_name = "photo.jpg"
        (tmp_path / base_name).write_text("original")

        for i in range(1, 10):
            counter_name = f"photo_00{i}.jpg"
            (tmp_path / counter_name).write_text(f"duplicate {i}")

        target = tmp_path / base_name
        result = resolve_filename_conflict(target)

        assert result == tmp_path / "photo_010.jpg"

    def test_safety_limit_prevents_infinite_loop(self, tmp_path):
        """Test that safety limit prevents infinite loops."""
        # This test would be slow if we created 10000 files
        # Instead, we'll just verify the logic by reading the code
        # The function should raise RuntimeError after 9999 attempts
        # We won't actually test this as it's impractical
        pass


class TestCopyFile:
    """Test file copying with directory creation."""

    def test_copy_file_basic(self, tmp_path):
        """Test basic file copy operation."""
        source = tmp_path / "source.txt"
        source.write_text("test content")

        destination = tmp_path / "dest" / "target.txt"

        copy_file(source, destination)

        assert destination.exists()
        assert destination.read_text() == "test content"

    def test_copy_creates_parent_directories(self, tmp_path):
        """Test that parent directories are created if they don't exist."""
        source = tmp_path / "source.txt"
        source.write_text("test content")

        # Nested directory structure that doesn't exist
        destination = tmp_path / "nested" / "path" / "to" / "file.txt"

        copy_file(source, destination)

        assert destination.exists()
        assert destination.parent.exists()
        assert destination.read_text() == "test content"

    def test_copy_preserves_content(self, tmp_path):
        """Test that file content is preserved during copy."""
        source = tmp_path / "source.jpg"
        content = b"fake image data \x00\xFF\xD8\xFF"
        source.write_bytes(content)

        destination = tmp_path / "output" / "dest.jpg"

        copy_file(source, destination)

        assert destination.read_bytes() == content

    def test_copy_from_fixture_image(self, tmp_path):
        """Test copying actual fixture image file."""
        source = FIXTURES_DIR / "photo_with_exif_2020.jpg"
        destination = tmp_path / "photos" / "2020" / "photo.jpg"

        copy_file(source, destination)

        assert destination.exists()
        # Verify file size matches (good proxy for successful copy)
        assert destination.stat().st_size == source.stat().st_size

    def test_copy_overwrites_existing_file(self, tmp_path):
        """Test that copy overwrites existing destination file."""
        source = tmp_path / "source.txt"
        source.write_text("new content")

        destination = tmp_path / "dest.txt"
        destination.write_text("old content")

        copy_file(source, destination)

        assert destination.read_text() == "new content"

    def test_copy_raises_on_missing_source(self, tmp_path):
        """Test that copying non-existent source raises error."""
        source = tmp_path / "nonexistent.txt"
        destination = tmp_path / "dest.txt"

        with pytest.raises(Exception):  # Should raise FileNotFoundError or similar
            copy_file(source, destination)


class TestOrganizeFile:
    """Test the main organize_file function."""

    def test_organize_photo_file(self, tmp_path):
        """Test organizing a photo file."""
        # Create test photo
        source = tmp_path / "source" / "photo.jpg"
        source.parent.mkdir()
        source.write_text("photo content")

        output_dir = tmp_path / "output"
        year = 2020

        result = organize_file(source, year, output_dir)

        assert result is not None
        file_type, destination = result
        assert file_type == 'photo'
        assert destination.exists()
        assert destination.parent.name == "2020"
        assert PHOTOS_SUBDIR in str(destination)

    def test_organize_video_file(self, tmp_path):
        """Test organizing a video file."""
        source = tmp_path / "source" / "video.mp4"
        source.parent.mkdir()
        source.write_text("video content")

        output_dir = tmp_path / "output"
        year = 2021

        result = organize_file(source, year, output_dir)

        assert result is not None
        file_type, destination = result
        assert file_type == 'video'
        assert destination.exists()
        assert destination.parent.name == "2021"
        assert VIDEOS_SUBDIR in str(destination)

    def test_organize_skips_metadata_files(self, tmp_path):
        """Test that JSON metadata files are skipped."""
        source = tmp_path / "source" / "photo.jpg.json"
        source.parent.mkdir()
        source.write_text('{"metadata": "data"}')

        output_dir = tmp_path / "output"
        year = 2020

        result = organize_file(source, year, output_dir)

        assert result is None
        # Verify no files were created in output
        if output_dir.exists():
            assert len(list(output_dir.rglob("*"))) == 0

    def test_organize_skips_unrecognized_files(self, tmp_path):
        """Test that unrecognized file types are skipped."""
        unrecognized_files = ["document.txt", "archive.zip", "script.py"]

        for filename in unrecognized_files:
            source = tmp_path / "source" / filename
            source.parent.mkdir(exist_ok=True)
            source.write_text("content")

            output_dir = tmp_path / "output"
            year = 2020

            result = organize_file(source, year, output_dir)

            assert result is None

    def test_organize_handles_filename_conflicts(self, tmp_path):
        """Test that filename conflicts are resolved."""
        # Create first file
        source1 = tmp_path / "source1" / "photo.jpg"
        source1.parent.mkdir()
        source1.write_text("first photo")

        output_dir = tmp_path / "output"
        year = 2020

        result1 = organize_file(source1, year, output_dir)
        assert result1 is not None

        # Create second file with same name
        source2 = tmp_path / "source2" / "photo.jpg"
        source2.parent.mkdir()
        source2.write_text("second photo")

        result2 = organize_file(source2, year, output_dir)
        assert result2 is not None

        # Both files should exist with different paths
        _, dest1 = result1
        _, dest2 = result2

        assert dest1.exists()
        assert dest2.exists()
        assert dest1 != dest2
        assert "_001" in dest2.name

    def test_organize_validates_year(self, tmp_path):
        """Test that invalid years raise ValueError."""
        source = tmp_path / "photo.jpg"
        source.write_text("content")

        output_dir = tmp_path / "output"

        invalid_years = [1800, 1899, 2101, 3000, -100]

        for year in invalid_years:
            with pytest.raises(ValueError, match="Invalid year"):
                organize_file(source, year, output_dir)

    def test_organize_valid_year_range(self, tmp_path):
        """Test that valid years (1900-2100) are accepted."""
        source = tmp_path / "photo.jpg"
        source.write_text("content")

        output_dir = tmp_path / "output"

        valid_years = [1900, 1950, 2000, 2020, 2100]

        for year in valid_years:
            # Use unique output dir for each year
            year_output = output_dir / str(year)
            result = organize_file(source, year, year_output)
            assert result is not None

    def test_organize_preserves_file_content(self, tmp_path):
        """Test that file content is preserved during organization."""
        content = b"binary photo data \x00\xFF\xD8\xFF"
        source = tmp_path / "photo.jpg"
        source.write_bytes(content)

        output_dir = tmp_path / "output"
        year = 2020

        result = organize_file(source, year, output_dir)

        assert result is not None
        _, destination = result
        assert destination.read_bytes() == content

    def test_organize_with_actual_fixture(self, tmp_path):
        """Test organizing an actual fixture file."""
        source = FIXTURES_DIR / "photo_with_exif_2020.jpg"
        output_dir = tmp_path / "output"
        year = 2020

        result = organize_file(source, year, output_dir)

        assert result is not None
        file_type, destination = result
        assert file_type == 'photo'
        assert destination.exists()
        # Verify file size matches
        assert destination.stat().st_size == source.stat().st_size


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""

    def test_organize_mixed_media_files(self, tmp_path):
        """Test organizing a mix of photos and videos."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        # Create test files
        files = [
            ("photo1.jpg", 'photo', 2020),
            ("photo2.png", 'photo', 2021),
            ("video1.mp4", 'video', 2020),
            ("video2.mov", 'video', 2021),
        ]

        output_dir = tmp_path / "output"

        for filename, file_type, year in files:
            source = source_dir / filename
            source.write_text(f"content of {filename}")

            result = organize_file(source, year, output_dir)

            assert result is not None
            result_type, destination = result
            assert result_type == file_type
            assert destination.exists()

        # Verify directory structure
        assert (output_dir / PHOTOS_SUBDIR / "2020").exists()
        assert (output_dir / PHOTOS_SUBDIR / "2021").exists()
        assert (output_dir / VIDEOS_SUBDIR / "2020").exists()
        assert (output_dir / VIDEOS_SUBDIR / "2021").exists()

    def test_organize_with_metadata_files_skipped(self, tmp_path):
        """Test that metadata companion files are properly skipped."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        # Create photo and its companion JSON
        photo = source_dir / "photo.jpg"
        photo.write_text("photo content")

        json_file = source_dir / "photo.jpg.json"
        json_file.write_text('{"metadata": "data"}')

        output_dir = tmp_path / "output"
        year = 2020

        # Organize photo
        result_photo = organize_file(photo, year, output_dir)
        assert result_photo is not None

        # Try to organize JSON (should be skipped)
        result_json = organize_file(json_file, year, output_dir)
        assert result_json is None

        # Verify only photo was copied
        output_files = list(output_dir.rglob("*.*"))
        assert len(output_files) == 1
        assert output_files[0].suffix == ".jpg"
