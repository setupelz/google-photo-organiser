"""Tests for zip extraction and Google Takeout processing."""

import shutil
import tempfile
import zipfile
from pathlib import Path

import pytest

from photo_organiser.extractor import (
    cleanup_temp_dir,
    create_temp_extraction_dir,
    extract_zip,
    find_media_files,
    process_zip_file,
)

# Test fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestCreateTempExtractionDir:
    """Test temporary directory creation."""

    def test_creates_temp_directory(self):
        """Test that a temporary directory is created."""
        temp_dir = create_temp_extraction_dir()

        assert temp_dir.exists()
        assert temp_dir.is_dir()
        assert "photo_organiser_" in temp_dir.name

        # Cleanup
        shutil.rmtree(temp_dir)

    def test_creates_unique_directories(self):
        """Test that multiple calls create unique directories."""
        temp_dir1 = create_temp_extraction_dir()
        temp_dir2 = create_temp_extraction_dir()

        assert temp_dir1 != temp_dir2
        assert temp_dir1.exists()
        assert temp_dir2.exists()

        # Cleanup
        shutil.rmtree(temp_dir1)
        shutil.rmtree(temp_dir2)

    def test_directory_is_writable(self):
        """Test that created directory is writable."""
        temp_dir = create_temp_extraction_dir()

        # Try writing a file to verify write permissions
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")

        assert test_file.exists()
        assert test_file.read_text() == "test content"

        # Cleanup
        shutil.rmtree(temp_dir)


class TestCleanupTempDir:
    """Test temporary directory cleanup."""

    def test_cleanup_removes_directory(self):
        """Test that cleanup removes the temporary directory."""
        temp_dir = Path(tempfile.mkdtemp(prefix="test_cleanup_"))
        temp_dir.mkdir(exist_ok=True)

        # Add some files
        (temp_dir / "file1.txt").write_text("content1")
        (temp_dir / "file2.txt").write_text("content2")

        cleanup_temp_dir(temp_dir)

        assert not temp_dir.exists()

    def test_cleanup_removes_nested_structure(self):
        """Test that cleanup removes nested directory structure."""
        temp_dir = Path(tempfile.mkdtemp(prefix="test_cleanup_"))

        # Create nested structure
        nested = temp_dir / "level1" / "level2" / "level3"
        nested.mkdir(parents=True)
        (nested / "file.txt").write_text("nested content")

        cleanup_temp_dir(temp_dir)

        assert not temp_dir.exists()

    def test_cleanup_nonexistent_directory(self):
        """Test that cleanup handles non-existent directories gracefully."""
        temp_dir = Path("/nonexistent/directory/path")

        # Should not raise an error
        cleanup_temp_dir(temp_dir)

        assert not temp_dir.exists()

    def test_cleanup_with_many_files(self):
        """Test cleanup with many files."""
        temp_dir = Path(tempfile.mkdtemp(prefix="test_cleanup_"))

        # Create many files
        for i in range(100):
            (temp_dir / f"file_{i}.txt").write_text(f"content {i}")

        cleanup_temp_dir(temp_dir)

        assert not temp_dir.exists()


class TestExtractZip:
    """Test zip file extraction."""

    def test_extract_valid_zip(self, tmp_path):
        """Test extracting a valid zip file."""
        zip_path = FIXTURES_DIR / "sample_takeout.zip"
        temp_dir = tmp_path / "extraction"
        temp_dir.mkdir()

        result = extract_zip(zip_path, temp_dir)

        assert result.exists()
        assert result.is_dir()

    def test_extract_handles_takeout_structure(self, tmp_path):
        """Test that Google Takeout nested structure is handled."""
        zip_path = FIXTURES_DIR / "sample_takeout.zip"
        temp_dir = tmp_path / "extraction"
        temp_dir.mkdir()

        result = extract_zip(zip_path, temp_dir)

        # Should return path to Takeout/Google Photos/
        assert "Google Photos" in str(result) or result == temp_dir

    def test_extract_nonexistent_file(self, tmp_path):
        """Test that non-existent zip file raises FileNotFoundError."""
        zip_path = tmp_path / "nonexistent.zip"
        temp_dir = tmp_path / "extraction"
        temp_dir.mkdir()

        with pytest.raises(FileNotFoundError, match="Zip file not found"):
            extract_zip(zip_path, temp_dir)

    def test_extract_invalid_zip_file(self, tmp_path):
        """Test that invalid zip file raises ValueError."""
        # Create a non-zip file
        fake_zip = tmp_path / "fake.zip"
        fake_zip.write_text("This is not a zip file")

        temp_dir = tmp_path / "extraction"
        temp_dir.mkdir()

        with pytest.raises(ValueError, match="Not a valid zip file"):
            extract_zip(fake_zip, temp_dir)

    def test_extract_corrupted_zip(self, tmp_path):
        """Test that corrupted zip file raises ValueError or BadZipFile."""
        # Create a corrupted zip file
        corrupted_zip = tmp_path / "corrupted.zip"
        # Write valid zip header but truncate the file
        with zipfile.ZipFile(corrupted_zip, 'w') as zf:
            zf.writestr("file.txt", "content")

        # Corrupt by truncating
        with open(corrupted_zip, 'rb') as f:
            data = f.read()
        with open(corrupted_zip, 'wb') as f:
            f.write(data[:len(data) // 2])  # Write only half the data

        temp_dir = tmp_path / "extraction"
        temp_dir.mkdir()

        # Corrupted zip is caught by is_zipfile() check and raises ValueError
        with pytest.raises(ValueError, match="Not a valid zip file"):
            extract_zip(corrupted_zip, temp_dir)

    def test_extract_empty_zip(self, tmp_path):
        """Test extracting an empty zip file."""
        zip_path = FIXTURES_DIR / "empty_takeout.zip"
        temp_dir = tmp_path / "extraction"
        temp_dir.mkdir()

        result = extract_zip(zip_path, temp_dir)

        assert result.exists()
        assert result.is_dir()

    def test_extract_without_takeout_structure(self, tmp_path):
        """Test extraction of zip without Takeout structure returns root."""
        # Create a simple zip without Takeout structure
        simple_zip = tmp_path / "simple.zip"
        with zipfile.ZipFile(simple_zip, 'w') as zf:
            zf.writestr("photo.jpg", "photo content")
            zf.writestr("video.mp4", "video content")

        temp_dir = tmp_path / "extraction"
        temp_dir.mkdir()

        result = extract_zip(simple_zip, temp_dir)

        # Should return temp_dir since no Takeout structure
        assert result == temp_dir
        assert (result / "photo.jpg").exists()
        assert (result / "video.mp4").exists()

    def test_extract_preserves_nested_structure(self, tmp_path):
        """Test that nested directory structure is preserved."""
        # Create zip with nested structure
        nested_zip = tmp_path / "nested.zip"
        with zipfile.ZipFile(nested_zip, 'w') as zf:
            zf.writestr("Takeout/Google Photos/Album1/photo.jpg", "photo1")
            zf.writestr("Takeout/Google Photos/Album2/photo.jpg", "photo2")

        temp_dir = tmp_path / "extraction"
        temp_dir.mkdir()

        result = extract_zip(nested_zip, temp_dir)

        # Should find the Google Photos directory
        assert result.name == "Google Photos"
        assert result.exists()


class TestFindMediaFiles:
    """Test finding media files in a directory."""

    def test_find_files_in_flat_directory(self, tmp_path):
        """Test finding files in a flat directory structure."""
        # Create test files
        (tmp_path / "photo1.jpg").write_text("photo1")
        (tmp_path / "photo2.png").write_text("photo2")
        (tmp_path / "video.mp4").write_text("video")

        result = find_media_files(tmp_path)

        assert len(result) == 3
        filenames = {f.name for f in result}
        assert filenames == {"photo1.jpg", "photo2.png", "video.mp4"}

    def test_find_files_in_nested_structure(self, tmp_path):
        """Test finding files in nested directory structure."""
        # Create nested structure
        (tmp_path / "album1").mkdir()
        (tmp_path / "album2").mkdir()
        (tmp_path / "album1" / "photo1.jpg").write_text("photo1")
        (tmp_path / "album2" / "photo2.jpg").write_text("photo2")
        (tmp_path / "album2" / "video.mp4").write_text("video")

        result = find_media_files(tmp_path)

        assert len(result) == 3
        filenames = {f.name for f in result}
        assert filenames == {"photo1.jpg", "photo2.jpg", "video.mp4"}

    def test_find_files_empty_directory(self, tmp_path):
        """Test finding files in an empty directory."""
        result = find_media_files(tmp_path)

        assert len(result) == 0
        assert result == []

    def test_find_files_includes_json_metadata(self, tmp_path):
        """Test that JSON metadata files are included in results."""
        (tmp_path / "photo.jpg").write_text("photo")
        (tmp_path / "photo.jpg.json").write_text('{"metadata": "data"}')

        result = find_media_files(tmp_path)

        assert len(result) == 2
        filenames = {f.name for f in result}
        assert filenames == {"photo.jpg", "photo.jpg.json"}

    def test_find_files_deeply_nested(self, tmp_path):
        """Test finding files in deeply nested structure."""
        # Create deep nesting
        deep_path = tmp_path / "level1" / "level2" / "level3" / "level4"
        deep_path.mkdir(parents=True)
        (deep_path / "photo.jpg").write_text("photo")

        result = find_media_files(tmp_path)

        assert len(result) == 1
        assert result[0].name == "photo.jpg"

    def test_find_files_ignores_directories(self, tmp_path):
        """Test that directories are not included in results."""
        # Create directories and files
        (tmp_path / "dir1").mkdir()
        (tmp_path / "dir2").mkdir()
        (tmp_path / "file.txt").write_text("content")

        result = find_media_files(tmp_path)

        # Should only return the file, not directories
        assert len(result) == 1
        assert result[0].name == "file.txt"

    def test_find_files_with_various_extensions(self, tmp_path):
        """Test finding files with various extensions."""
        extensions = [".jpg", ".jpeg", ".png", ".mp4", ".mov", ".json", ".txt", ".heic"]
        for i, ext in enumerate(extensions):
            (tmp_path / f"file{i}{ext}").write_text(f"content{i}")

        result = find_media_files(tmp_path)

        assert len(result) == len(extensions)

    def test_find_files_from_extracted_fixture(self, tmp_path):
        """Test finding files from an extracted fixture zip."""
        zip_path = FIXTURES_DIR / "sample_takeout.zip"

        # Extract zip
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(tmp_path)

        result = find_media_files(tmp_path)

        # Should find files in the extracted structure
        assert len(result) > 0


class TestProcessZipFile:
    """Test the complete zip processing workflow."""

    def test_process_valid_zip(self):
        """Test processing a valid Google Takeout zip file."""
        zip_path = FIXTURES_DIR / "sample_takeout.zip"

        media_files, temp_dir = process_zip_file(zip_path)

        assert isinstance(media_files, list)
        assert len(media_files) > 0
        assert temp_dir.exists()
        assert temp_dir.is_dir()

        # Cleanup
        cleanup_temp_dir(temp_dir)

    def test_process_returns_temp_dir_for_cleanup(self):
        """Test that process_zip_file returns temp directory for cleanup."""
        zip_path = FIXTURES_DIR / "sample_takeout.zip"

        media_files, temp_dir = process_zip_file(zip_path)

        # Verify temp_dir is valid and can be cleaned up
        assert temp_dir.exists()

        cleanup_temp_dir(temp_dir)

        assert not temp_dir.exists()

    def test_process_nonexistent_zip(self):
        """Test that processing non-existent zip raises FileNotFoundError."""
        zip_path = Path("/nonexistent/file.zip")

        with pytest.raises(FileNotFoundError):
            process_zip_file(zip_path)

    def test_process_invalid_zip(self, tmp_path):
        """Test that processing invalid zip raises ValueError."""
        fake_zip = tmp_path / "fake.zip"
        fake_zip.write_text("Not a zip file")

        with pytest.raises(ValueError):
            process_zip_file(fake_zip)

    def test_process_cleans_up_on_error(self, tmp_path, monkeypatch):
        """Test that temp directory is cleaned up when extraction fails."""
        zip_path = FIXTURES_DIR / "sample_takeout.zip"

        # Track created temp directories
        created_dirs = []
        original_mkdtemp = tempfile.mkdtemp

        def tracking_mkdtemp(*args, **kwargs):
            result = original_mkdtemp(*args, **kwargs)
            created_dirs.append(Path(result))
            return result

        monkeypatch.setattr(tempfile, "mkdtemp", tracking_mkdtemp)

        # Mock extract_zip to raise an error
        def mock_extract_zip(zip_path, temp_dir):
            raise zipfile.BadZipFile("Simulated extraction error")

        import photo_organiser.extractor
        monkeypatch.setattr(photo_organiser.extractor, "extract_zip", mock_extract_zip)

        # Attempt to process (should fail)
        with pytest.raises(zipfile.BadZipFile):
            process_zip_file(zip_path)

        # Verify temp directory was cleaned up
        for temp_dir in created_dirs:
            assert not temp_dir.exists(), f"Temp directory {temp_dir} was not cleaned up"

    def test_process_empty_zip(self):
        """Test processing an empty zip file."""
        zip_path = FIXTURES_DIR / "empty_takeout.zip"

        media_files, temp_dir = process_zip_file(zip_path)

        # Should return empty list but valid temp_dir
        assert isinstance(media_files, list)
        assert len(media_files) == 0
        assert temp_dir.exists()

        # Cleanup
        cleanup_temp_dir(temp_dir)

    def test_process_zip_without_takeout_structure(self, tmp_path):
        """Test processing zip without Google Takeout structure."""
        # Create simple zip
        simple_zip = tmp_path / "simple.zip"
        with zipfile.ZipFile(simple_zip, 'w') as zf:
            zf.writestr("photo.jpg", "photo content")
            zf.writestr("video.mp4", "video content")

        media_files, temp_dir = process_zip_file(simple_zip)

        assert len(media_files) == 2
        filenames = {f.name for f in media_files}
        assert filenames == {"photo.jpg", "video.mp4"}

        # Cleanup
        cleanup_temp_dir(temp_dir)

    def test_process_multiple_zips_sequentially(self):
        """Test processing multiple zip files sequentially."""
        zip_path = FIXTURES_DIR / "sample_takeout.zip"

        results = []
        for _ in range(3):
            media_files, temp_dir = process_zip_file(zip_path)
            results.append((media_files, temp_dir))

        # All should succeed
        assert len(results) == 3

        # Each should have unique temp directory
        temp_dirs = [temp_dir for _, temp_dir in results]
        assert len(set(temp_dirs)) == 3

        # Cleanup all
        for _, temp_dir in results:
            cleanup_temp_dir(temp_dir)

    def test_process_returns_correct_file_paths(self, tmp_path):
        """Test that returned file paths are correct and accessible."""
        # Create test zip
        test_zip = tmp_path / "test.zip"
        with zipfile.ZipFile(test_zip, 'w') as zf:
            zf.writestr("Takeout/Google Photos/photo.jpg", "photo content")
            zf.writestr("Takeout/Google Photos/video.mp4", "video content")

        media_files, temp_dir = process_zip_file(test_zip)

        # All returned paths should exist
        for file_path in media_files:
            assert file_path.exists()
            assert file_path.is_file()

        # Cleanup
        cleanup_temp_dir(temp_dir)


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""

    def test_full_extraction_workflow(self):
        """Test the complete extraction workflow."""
        zip_path = FIXTURES_DIR / "sample_takeout.zip"

        # 1. Process zip file
        media_files, temp_dir = process_zip_file(zip_path)

        # 2. Verify files were extracted
        assert len(media_files) > 0
        assert temp_dir.exists()

        # 3. Verify files are accessible
        for file_path in media_files:
            assert file_path.exists()
            # Should be able to read file
            _ = file_path.stat()

        # 4. Cleanup
        cleanup_temp_dir(temp_dir)

        # 5. Verify cleanup
        assert not temp_dir.exists()

    def test_handle_zip_with_mixed_content(self, tmp_path):
        """Test handling zip with photos, videos, and metadata."""
        # Create comprehensive test zip
        test_zip = tmp_path / "mixed.zip"
        with zipfile.ZipFile(test_zip, 'w') as zf:
            zf.writestr("Takeout/Google Photos/Album/photo.jpg", "photo")
            zf.writestr("Takeout/Google Photos/Album/photo.jpg.json", '{"metadata": "data"}')
            zf.writestr("Takeout/Google Photos/Album/video.mp4", "video")
            zf.writestr("Takeout/Google Photos/Album/video.mp4.json", '{"metadata": "data"}')

        media_files, temp_dir = process_zip_file(test_zip)

        # Should find all 4 files (2 media + 2 metadata)
        assert len(media_files) == 4

        filenames = {f.name for f in media_files}
        assert "photo.jpg" in filenames
        assert "photo.jpg.json" in filenames
        assert "video.mp4" in filenames
        assert "video.mp4.json" in filenames

        # Cleanup
        cleanup_temp_dir(temp_dir)

    def test_extraction_with_unicode_filenames(self, tmp_path):
        """Test extraction with unicode characters in filenames."""
        # Create zip with unicode filenames
        unicode_zip = tmp_path / "unicode.zip"
        with zipfile.ZipFile(unicode_zip, 'w') as zf:
            zf.writestr("Takeout/Google Photos/Vacation 🌴/photo_日本.jpg", "photo")
            zf.writestr("Takeout/Google Photos/Café ☕/image.png", "image")

        media_files, temp_dir = process_zip_file(unicode_zip)

        # Should handle unicode filenames
        assert len(media_files) == 2

        # Cleanup
        cleanup_temp_dir(temp_dir)
