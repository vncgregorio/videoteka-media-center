"""Media controller for managing media files and interactions."""

from pathlib import Path
from typing import List, Optional

from ..models.database import Database
from ..utils.thumbnail_generator import ThumbnailGenerator


class MediaController:
    """Controller for media file operations."""

    def __init__(self, database: Database, thumbnail_generator: Optional[ThumbnailGenerator] = None):
        """Initialize media controller.

        Args:
            database: Database instance
            thumbnail_generator: Optional thumbnail generator instance
        """
        self.database = database
        self.thumbnail_generator = thumbnail_generator or ThumbnailGenerator()

    def get_media_files(
        self,
        file_type: Optional[str] = None,
        search_query: Optional[str] = None,
        folder_path: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[dict]:
        """Get media files with filters.

        Args:
            file_type: Filter by type ('video', 'audio', 'image', 'document')
            search_query: Search in file names
            folder_path: Filter by folder
            limit: Maximum number of results (default: 100 for pagination)
            offset: Offset for pagination

        Returns:
            List of media file dictionaries
        """
        # Apply default pagination limit if not specified
        if limit is None:
            limit = 100

        media_files = self.database.get_media_files(
            file_type=file_type if file_type != "all" else None,
            folder_path=folder_path,
            search_query=search_query,
            limit=limit,
            offset=offset,
        )

        # Note: Thumbnail generation is now handled asynchronously in the UI
        # to avoid blocking the main thread with large datasets

        return media_files

    def get_media_count(self, file_type: Optional[str] = None) -> int:
        """Get count of media files.

        Args:
            file_type: Optional filter by type

        Returns:
            Total count
        """
        return self.database.get_media_count(file_type=file_type if file_type != "all" else None)

    def open_file(self, file_path: str) -> bool:
        """Open file with default application.

        Args:
            file_path: Path to file

        Returns:
            True if successful
        """
        if not Path(file_path).exists():
            return False

        try:
            from PySide6.QtGui import QDesktopServices
            from PySide6.QtCore import QUrl

            url = QUrl.fromLocalFile(file_path)
            return QDesktopServices.openUrl(url)
        except Exception:
            return False

    def get_folders(self) -> List[dict]:
        """Get list of folders.

        Returns:
            List of folder dictionaries
        """
        return self.database.get_folders()

    def get_categories(self) -> List[str]:
        """Get list of unique categories (subfolders).

        Returns:
            List of category names
        """
        from pathlib import Path
        
        # Normalize root folders to ensure consistent path comparison
        root_folders = [str(Path(f["folder_path"]).resolve()) for f in self.database.get_folders()]
        return self.database.get_categories(root_folders)

    def get_media_files_by_category(
        self,
        category: str,
        file_type: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[dict]:
        """Get media files filtered by category.

        Args:
            category: Category name (empty string for all)
            file_type: Optional filter by type
            search_query: Optional search query
            limit: Maximum number of results (default: 100 for pagination)
            offset: Offset for pagination

        Returns:
            List of media file dictionaries
        """
        from pathlib import Path
        
        # Normalize root folders to ensure consistent path comparison
        root_folders = [str(Path(f["folder_path"]).resolve()) for f in self.database.get_folders()]

        # Apply default pagination limit if not specified
        if limit is None:
            limit = 100

        if not category:
            # Return all files
            return self.get_media_files(
                file_type=file_type if file_type != "all" else None,
                search_query=search_query,
                limit=limit,
                offset=offset,
            )

        # Get files by category
        media_files = self.database.get_media_files_by_category(
            category, root_folders, file_type, search_query, limit, offset
        )

        # Note: Thumbnail generation is now handled asynchronously in the UI
        # to avoid blocking the main thread with large datasets

        return media_files


