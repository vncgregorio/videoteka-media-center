"""Application controller for managing application state and coordination."""

from pathlib import Path
from typing import Optional

from ..models.database import Database
from ..controllers.media_controller import MediaController
from ..utils.thumbnail_generator import ThumbnailGenerator
from ..views.setup_wizard import SetupWizard
from ..views.main_window import MainWindow
from ..views.shortcuts_dialog import ShortcutsDialog


class AppController:
    """Main application controller."""

    def __init__(self, db_path: str = "data/videoteka.db"):
        """Initialize application controller.

        Args:
            db_path: Path to database file
        """
        self.db_path = Path(db_path)
        self.database: Optional[Database] = None
        self.media_controller: Optional[MediaController] = None
        self.thumbnail_generator: Optional[ThumbnailGenerator] = None
        self.main_window: Optional[MainWindow] = None

    def initialize(self) -> bool:
        """Initialize database and controllers.

        Returns:
            True if initialization successful
        """
        try:
            self.database = Database(str(self.db_path))
            self.thumbnail_generator = ThumbnailGenerator()
            self.media_controller = MediaController(
                self.database, self.thumbnail_generator
            )
            return True
        except Exception:
            return False

    def is_setup_complete(self) -> bool:
        """Check if initial setup is complete.

        Returns:
            True if setup is complete
        """
        if not self.database:
            return False

        # Check if database exists and has folders
        folders = self.database.get_folders()
        return len(folders) > 0

    def show_setup_wizard(self) -> bool:
        """Show setup wizard and return True if setup completed.

        Returns:
            True if setup was completed successfully
        """
        if not self.database:
            return False

        wizard = SetupWizard(self.database)
        result = wizard.exec()

        return result == wizard.DialogCode.Accepted

    def show_main_window(self) -> None:
        """Show and initialize main window."""
        if not self.media_controller:
            return

        self.main_window = MainWindow()
        
        # Store controller reference in main window
        self.main_window.controller = self

        # Connect category panel
        self.main_window.category_panel.category_selected.connect(
            self._on_category_changed
        )

        # Connect media grid
        self.main_window.media_grid.item_clicked.connect(self._on_media_clicked)

        # Load categories
        categories = self.media_controller.get_categories()
        self.main_window.category_panel.set_categories(categories)

        # Load initial media
        self._load_media()

        self.main_window.show()

        # Show shortcuts dialog on first run (after window is shown)
        self._show_shortcuts_if_needed()

    def _normalize_category(self, category: Optional[str]) -> str:
        """Normalize category value, ensuring it's not None.
        
        Args:
            category: Category value (may be None)
            
        Returns:
            Normalized category string (empty string if None)
        """
        return category if category is not None else ""

    def _on_category_changed(self, category: str) -> None:
        """Handle category change.
        
        Args:
            category: Selected category name
        """
        # Load media for selected category
        # IMPORTANT: Don't move focus - keep focus on categories
        self._load_media(category=self._normalize_category(category))

    def _load_media(self, category: Optional[str] = None, limit: Optional[int] = None, offset: Optional[int] = None) -> None:
        """Load media files and display in grid.
        
        Args:
            category: Optional category to filter by
            limit: Maximum number of results (default: 100 for pagination)
            offset: Offset for pagination
        """
        if not self.media_controller or not self.main_window:
            return

        # Use provided category or get from panel
        if category is None:
            category = self.main_window.category_panel.get_selected_category()
        
        # Normalize category
        category = self._normalize_category(category)

        # Apply default pagination limit if not specified
        if limit is None:
            limit = 100
        if offset is None:
            offset = 0

        # Get media files for category with pagination
        if category:
            media_files = self.media_controller.get_media_files_by_category(
                category, limit=limit, offset=offset
            )
        else:
            media_files = self.media_controller.get_media_files(
                limit=limit, offset=offset
            )

        # Update grid WITHOUT moving focus
        self.main_window.set_media_files(media_files, self.thumbnail_generator)

    def _on_media_clicked(self, file_path: str) -> None:
        """Handle media file click.

        Args:
            file_path: Path to clicked file
        """
        if not self.media_controller:
            return

        # Get file info
        media_file = self.database.get_media_file_by_path(file_path)
        if not media_file:
            return

        file_type = media_file.get("file_type")

        # For videos, just open with default app
        # For others, could show preview first
        if file_type == "video":
            self.media_controller.open_file(file_path)
        else:
            # Could show preview dialog here
            self.media_controller.open_file(file_path)

    def _show_shortcuts_if_needed(self) -> None:
        """Show shortcuts dialog if needed (first run)."""
        if not self.database:
            return

        # Check preference
        show_shortcuts = self.database.get_preference("show_shortcuts_on_startup", "true")
        if show_shortcuts.lower() == "true":
            dialog = ShortcutsDialog(self.main_window)
            dialog.exec()
            # Save preference
            self.database.set_preference("show_shortcuts_on_startup", str(dialog.should_show_again()).lower())

    def show_shortcuts(self) -> None:
        """Show shortcuts dialog."""
        if self.main_window:
            dialog = ShortcutsDialog(self.main_window)
            dialog.exec()

    def reset_library(self) -> bool:
        """Reset library by clearing database and rescanning.

        Returns:
            True if reset was completed successfully
        """
        if not self.database:
            return False

        # Clear all data
        self.database.clear_all_data()

        # Show setup wizard
        if self.show_setup_wizard():
            # After scanning, reload categories and media
            categories = self.media_controller.get_categories()
            if self.main_window:
                self.main_window.category_panel.set_categories(categories)
                self._load_media()
            return True

        return False

    def cleanup(self) -> None:
        """Cleanup resources."""
        if self.database:
            self.database.close()

