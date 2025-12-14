"""Tests for file_utils module."""

import unittest
import tempfile
import os
from pathlib import Path

from src.utils.file_utils import (
    get_media_extensions,
    is_media_file,
    get_file_type,
    get_file_metadata,
)


class TestFileUtils(unittest.TestCase):
    """Test cases for file_utils functions."""

    def test_get_media_extensions(self):
        """Test getting media extensions."""
        extensions = get_media_extensions()
        self.assertIn("video", extensions)
        self.assertIn("audio", extensions)
        self.assertIn("image", extensions)
        self.assertIn("document", extensions)

        # Check some specific extensions
        self.assertIn(".mp4", extensions["video"])
        self.assertIn(".mp3", extensions["audio"])
        self.assertIn(".jpg", extensions["image"])
        self.assertIn(".pdf", extensions["document"])

    def test_is_media_file(self):
        """Test media file detection."""
        # Valid media files
        self.assertTrue(is_media_file("test.mp4"))
        self.assertTrue(is_media_file("test.mp3"))
        self.assertTrue(is_media_file("test.jpg"))
        self.assertTrue(is_media_file("test.pdf"))

        # Invalid files
        self.assertFalse(is_media_file("test.txt"))
        self.assertFalse(is_media_file("test.exe"))

    def test_get_file_type(self):
        """Test file type detection."""
        self.assertEqual(get_file_type("test.mp4"), "video")
        self.assertEqual(get_file_type("test.mkv"), "video")
        self.assertEqual(get_file_type("test.mp3"), "audio")
        self.assertEqual(get_file_type("test.flac"), "audio")
        self.assertEqual(get_file_type("test.jpg"), "image")
        self.assertEqual(get_file_type("test.png"), "image")
        self.assertEqual(get_file_type("test.pdf"), "document")

        # Unknown extension
        self.assertIsNone(get_file_type("test.unknown"))

    def test_get_file_metadata(self):
        """Test getting file metadata."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            temp_path = f.name

        try:
            metadata = get_file_metadata(temp_path)
            self.assertIn("file_size", metadata)
            self.assertIn("date_modified", metadata)
            self.assertGreater(metadata["file_size"], 0)
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    unittest.main()


