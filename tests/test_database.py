"""Tests for database module."""

import os
import tempfile
import unittest
from pathlib import Path

from src.models.database import Database
from src.models.media_file import MediaFile, MediaType


class TestDatabase(unittest.TestCase):
    """Test cases for Database class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.database = Database(self.db_path)

    def tearDown(self):
        """Clean up after tests."""
        self.database.close()
        # Clean up temp files
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)

    def test_init_database(self):
        """Test database initialization."""
        # Database should be created
        self.assertTrue(os.path.exists(self.db_path))

        # Tables should exist
        conn = self.database._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='media_files'"
        )
        self.assertIsNotNone(cursor.fetchone())

    def test_add_media_file(self):
        """Test adding media file."""
        media_file = MediaFile(
            file_path="/test/video.mp4",
            file_name="video.mp4",
            file_type=MediaType.VIDEO,
            file_size=1000000,
        )

        file_id = self.database.add_media_file(media_file)
        self.assertIsNotNone(file_id)

        # Verify it was added
        result = self.database.get_media_file_by_path("/test/video.mp4")
        self.assertIsNotNone(result)
        self.assertEqual(result["file_name"], "video.mp4")

    def test_get_media_files(self):
        """Test getting media files."""
        # Add test files
        for i in range(5):
            media_file = MediaFile(
                file_path=f"/test/file{i}.mp4",
                file_name=f"file{i}.mp4",
                file_type=MediaType.VIDEO,
            )
            self.database.add_media_file(media_file)

        # Get all files
        files = self.database.get_media_files()
        self.assertEqual(len(files), 5)

        # Filter by type
        video_files = self.database.get_media_files(file_type="video")
        self.assertEqual(len(video_files), 5)

    def test_add_folder(self):
        """Test adding folder."""
        folder_id = self.database.add_folder("/test/folder")
        self.assertIsNotNone(folder_id)

        folders = self.database.get_folders()
        self.assertEqual(len(folders), 1)
        self.assertEqual(folders[0]["folder_path"], "/test/folder")

    def test_get_media_count(self):
        """Test getting media count."""
        # Initially empty
        count = self.database.get_media_count()
        self.assertEqual(count, 0)

        # Add files
        for i in range(3):
            media_file = MediaFile(
                file_path=f"/test/file{i}.mp4",
                file_name=f"file{i}.mp4",
                file_type=MediaType.VIDEO,
            )
            self.database.add_media_file(media_file)

        count = self.database.get_media_count()
        self.assertEqual(count, 3)


if __name__ == "__main__":
    unittest.main()


