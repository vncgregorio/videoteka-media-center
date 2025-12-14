"""Tests for thumbnail_generator module."""

import unittest
import tempfile
import os
from pathlib import Path
from PIL import Image

from src.utils.thumbnail_generator import ThumbnailGenerator


class TestThumbnailGenerator(unittest.TestCase):
    """Test cases for ThumbnailGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = os.path.join(self.temp_dir, "thumbnails")
        self.generator = ThumbnailGenerator(cache_dir=self.cache_dir)

    def tearDown(self):
        """Clean up after tests."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_get_cache_path(self):
        """Test cache path generation."""
        cache_path = self.generator._get_cache_path("/test/file.mp4")
        self.assertIsNotNone(cache_path)
        self.assertTrue(str(cache_path).endswith(".jpg"))

    def test_generate_image_thumbnail(self):
        """Test generating thumbnail from image."""
        # Create a test image
        test_image_path = os.path.join(self.temp_dir, "test.jpg")
        img = Image.new("RGB", (800, 600), color="red")
        img.save(test_image_path)

        thumbnail = self.generator._generate_image_thumbnail(test_image_path)
        self.assertIsNotNone(thumbnail)
        self.assertIsInstance(thumbnail, Image.Image)

    def test_generate_audio_thumbnail(self):
        """Test generating default audio thumbnail."""
        test_audio_path = "/test/audio.mp3"
        thumbnail = self.generator._generate_audio_thumbnail(test_audio_path)
        self.assertIsNotNone(thumbnail)
        self.assertIsInstance(thumbnail, Image.Image)


if __name__ == "__main__":
    unittest.main()


