"""Asynchronous thumbnail generation worker thread."""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import QThread, Signal

from .thumbnail_generator import ThumbnailGenerator


class ThumbnailWorker(QThread):
    """Worker thread for generating thumbnails asynchronously."""

    thumbnail_ready = Signal(str, str)  # Emits (file_path, thumbnail_path) when ready
    thumbnail_failed = Signal(str)  # Emits file_path when generation fails

    def __init__(self, file_path: str, file_type: str, thumbnail_generator: ThumbnailGenerator, parent=None):
        """Initialize thumbnail worker.

        Args:
            file_path: Path to media file
            file_type: Type of media ('video', 'audio', 'image', 'document')
            thumbnail_generator: ThumbnailGenerator instance
            parent: Parent QObject
        """
        super().__init__(parent)
        self.file_path = file_path
        self.file_type = file_type
        self.thumbnail_generator = thumbnail_generator
        self._cancelled = False

    def cancel(self) -> None:
        """Cancel thumbnail generation."""
        self._cancelled = True
        if self.isRunning():
            self.quit()  # Request thread to exit

    def cleanup(self) -> None:
        """Cleanup worker thread.
        
        This should be called before destroying the worker to ensure
        the thread is properly terminated.
        """
        self.cancel()
        if self.isRunning():
            # Wait up to 1 second for thread to finish
            if not self.wait(1000):
                # If thread is still running, force terminate
                self.terminate()
                self.wait(500)  # Wait a bit more after termination

    def run(self) -> None:
        """Generate thumbnail in background thread."""
        if self._cancelled:
            return

        try:
            # Check if thumbnail already exists in cache
            cache_path = self.thumbnail_generator.get_thumbnail_path(self.file_path)
            if cache_path:
                if not self._cancelled:
                    self.thumbnail_ready.emit(self.file_path, cache_path)
                return

            # Generate thumbnail
            thumbnail_path = self.thumbnail_generator.generate_thumbnail(
                self.file_path, self.file_type
            )

            if not self._cancelled:
                if thumbnail_path:
                    self.thumbnail_ready.emit(self.file_path, thumbnail_path)
                else:
                    self.thumbnail_failed.emit(self.file_path)
        except Exception:
            if not self._cancelled:
                self.thumbnail_failed.emit(self.file_path)
