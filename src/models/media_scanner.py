"""Media scanner for recursively scanning folders for media files."""

import os
from pathlib import Path
from threading import Thread
from typing import Callable, List, Optional

from ..models.database import Database
from ..models.media_file import MediaFile
from ..utils.file_utils import (
    get_file_duration,
    get_file_metadata,
    get_file_type,
    get_image_dimensions,
    get_video_dimensions,
    is_media_file,
)


class MediaScanner(Thread):
    """Thread-based media scanner for recursive folder scanning."""

    def __init__(
        self,
        folder_paths: List[str],
        database: Database,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        completed_callback: Optional[Callable[[int], None]] = None,
    ):
        """Initialize media scanner.

        Args:
            folder_paths: List of folder paths to scan
            database: Database instance to store results
            progress_callback: Callback function(current, total, current_file)
            completed_callback: Callback function(total_files) when done
        """
        super().__init__(daemon=True)
        self.folder_paths = [Path(p).resolve() for p in folder_paths]
        self.database = database
        self.progress_callback = progress_callback
        self.completed_callback = completed_callback
        self._stop_requested = False

    def stop(self) -> None:
        """Request scanner to stop."""
        self._stop_requested = True

    def _scan_folder(self, folder_path: Path) -> List[Path]:
        """Recursively scan a folder for media files.

        Args:
            folder_path: Path to folder to scan

        Returns:
            List of media file paths found
        """
        media_files = []

        if not folder_path.exists() or not folder_path.is_dir():
            return media_files

        try:
            for root, dirs, files in os.walk(folder_path):
                if self._stop_requested:
                    break

                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith(".")]

                for file in files:
                    if self._stop_requested:
                        break

                    file_path = Path(root) / file
                    if is_media_file(str(file_path)):
                        media_files.append(file_path)

        except PermissionError:
            # Skip folders without permission
            pass
        except Exception:
            # Continue on other errors
            pass

        return media_files

    def _process_media_file(self, file_path: Path) -> Optional[MediaFile]:
        """Process a single media file and extract metadata.

        Args:
            file_path: Path to media file

        Returns:
            MediaFile instance or None if processing failed
        """
        try:
            file_type_str = get_file_type(str(file_path))
            if not file_type_str:
                return None

            # Get basic metadata
            metadata = get_file_metadata(str(file_path))
            file_size = metadata.get("file_size")

            # Get type-specific metadata
            duration = None
            width = None
            height = None

            if file_type_str == "video":
                duration = get_file_duration(str(file_path))
                dimensions = get_video_dimensions(str(file_path))
                if dimensions:
                    width, height = dimensions
            elif file_type_str == "audio":
                duration = get_file_duration(str(file_path))
            elif file_type_str == "image":
                dimensions = get_image_dimensions(str(file_path))
                if dimensions:
                    width, height = dimensions

            # Map string type to MediaType enum
            from ..models.media_file import MediaType

            type_map = {
                "video": MediaType.VIDEO,
                "audio": MediaType.AUDIO,
                "image": MediaType.IMAGE,
                "document": MediaType.DOCUMENT,
            }
            file_type = type_map.get(file_type_str, MediaType.VIDEO)

            return MediaFile(
                file_path=str(file_path),
                file_name=file_path.name,
                file_type=file_type,
                file_size=file_size,
                duration=duration,
                width=width,
                height=height,
                folder_path=str(file_path.parent),
            )

        except Exception:
            return None

    def run(self) -> None:
        """Run the scanner in a separate thread."""
        all_media_files = []

        # First pass: collect all media files
        for folder_path in self.folder_paths:
            if self._stop_requested:
                break

            # Add folder to database
            self.database.add_folder(str(folder_path))

            # Scan folder
            media_files = self._scan_folder(folder_path)
            all_media_files.extend(media_files)

        total_files = len(all_media_files)
        processed = 0

        # Second pass: process and save to database
        for file_path in all_media_files:
            if self._stop_requested:
                break

            # Update progress
            if self.progress_callback:
                self.progress_callback(
                    processed, total_files, str(file_path)
                )

            # Process file
            media_file = self._process_media_file(file_path)
            if media_file:
                try:
                    self.database.add_media_file(media_file)
                    processed += 1
                except Exception:
                    # Skip files that can't be added (e.g., duplicates)
                    pass

        # Final progress update
        if self.progress_callback:
            self.progress_callback(processed, total_files, "")

        # Completion callback
        if self.completed_callback:
            self.completed_callback(processed)


