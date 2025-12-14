"""Main window for the media center application."""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QKeySequence, QShortcut, QKeyEvent
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QMenuBar,
    QMenu,
)

from .media_grid import MediaGrid
from .category_panel import CategoryPanel


class MainWindow(QMainWindow):
    """Main application window with streaming-style interface."""

    def __init__(self, parent=None):
        """Initialize main window.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Videoteka Media Center")
        self.setMinimumSize(1200, 800)
        self.controller = None  # Will be set by AppController

        self._setup_ui()
        self._setup_shortcuts()

    def _setup_ui(self) -> None:
        """Setup the main UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top bar
        self._setup_top_bar()

        # Category panel (left sidebar)
        self.category_panel = CategoryPanel()
        main_layout.addWidget(self.category_panel)

        # Main content area - Media grid
        self.media_grid = MediaGrid()
        main_layout.addWidget(self.media_grid)

        # Menu bar
        self._setup_menu_bar()

    def _setup_top_bar(self) -> None:
        """Setup top bar with title and settings."""
        # This will be integrated into the main layout
        pass

    def _setup_menu_bar(self) -> None:
        """Setup menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        manage_library_action = file_menu.addAction("Manage Library")
        manage_library_action.triggered.connect(self._manage_library)

        # Help menu
        help_menu = menubar.addMenu("Help")
        shortcuts_action = help_menu.addAction("Keyboard Shortcuts")
        shortcuts_action.triggered.connect(self._show_shortcuts)
        help_menu.addSeparator()
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self._show_about)

    def _setup_shortcuts(self) -> None:
        """Setup keyboard shortcuts."""
        # Note: Arrow keys are handled via keyPressEvent() to respect focus
        # Enter to open
        self.shortcut_enter = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        self.shortcut_enter.activated.connect(self._open_selected)

        # Home/End
        self.shortcut_home = QShortcut(QKeySequence(Qt.Key.Key_Home), self)
        self.shortcut_home.activated.connect(self._navigate_home)

        self.shortcut_end = QShortcut(QKeySequence(Qt.Key.Key_End), self)
        self.shortcut_end.activated.connect(self._navigate_end)

        # Escape
        self.shortcut_escape = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        self.shortcut_escape.activated.connect(self._handle_escape)

        # Focus categories
        self.shortcut_focus_categories = QShortcut(QKeySequence(Qt.Key.Key_C), self)
        self.shortcut_focus_categories.setContext(Qt.ShortcutContext.WindowShortcut)
        self.shortcut_focus_categories.activated.connect(self._focus_categories)

        # Focus grid/media list
        self.shortcut_focus_grid = QShortcut(QKeySequence(Qt.Key.Key_G), self)
        self.shortcut_focus_grid.setContext(Qt.ShortcutContext.WindowShortcut)
        self.shortcut_focus_grid.activated.connect(self._focus_grid)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle key press events with focus-aware navigation."""
        key = event.key()
        
        # C, G - Always work, regardless of focus
        if key == Qt.Key.Key_C:
            self._focus_categories()
            event.accept()
            return
        elif key == Qt.Key.Key_G:
            self._focus_grid()
            event.accept()
            return
        
        # Arrow keys - process based on current focus
        if key in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right):
            # Do categories have focus?
            if self.category_panel.category_list.hasFocus():
                if key == Qt.Key.Key_Down:
                    self.category_panel.focus_next()
                elif key == Qt.Key.Key_Up:
                    self.category_panel.focus_previous()
                event.accept()
                return
            
            # Grid has focus (or none has) - navigate grid
            else:
                # If MediaGrid or a card has focus, let MediaGrid handle it
                if (self.media_grid.hasFocus() or 
                    any(card.hasFocus() for card in self.media_grid.cards)):
                    # Let MediaGrid process the event
                    super().keyPressEvent(event)
                    return
                
                # Otherwise, navigate grid directly
                if self.media_grid.cards:
                    # Ensure a card has focus before navigating
                    if self.media_grid.focused_card_index < 0:
                        self.media_grid.focus_first()
                        event.accept()
                        return
                    
                    # Navigate grid
                    handled = False
                    if key == Qt.Key.Key_Right:
                        handled = self.media_grid.focus_right()
                    elif key == Qt.Key.Key_Left:
                        handled = self.media_grid.focus_left()
                    elif key == Qt.Key.Key_Down:
                        handled = self.media_grid.focus_down()
                    elif key == Qt.Key.Key_Up:
                        handled = self.media_grid.focus_up()
                    
                    if handled:
                        event.accept()
                        return
        
        # Enter key - handle based on focus
        elif key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            if self.category_panel.category_list.hasFocus():
                # Activate current category - shortcut is already disabled
                self.category_panel.activate_current_category()
                event.accept()
                return
            else:
                # Grid or other - let shortcut handle
                super().keyPressEvent(event)
                return
        
        # Default: process normally
        super().keyPressEvent(event)

    def _navigate_home(self) -> None:
        """Navigate to first item."""
        self.media_grid.focus_first()

    def _navigate_end(self) -> None:
        """Navigate to last item."""
        self.media_grid.focus_last()

    def _open_selected(self) -> None:
        """Open the currently selected file."""
        # Don't open if categories have focus - let them handle Enter
        if self.category_panel.category_list.hasFocus():
            return
        
        file_path = self.media_grid.get_focused_file_path()
        if file_path:
            self._open_file(file_path)

    def _handle_escape(self) -> None:
        """Handle escape key."""
        # If categories have focus, return focus to grid
        if self.category_panel.category_list.hasFocus():
            if self.media_grid.cards:
                self.media_grid.focus_first()

    def _focus_categories(self) -> None:
        """Focus the categories panel."""
        # Disable Enter shortcut when focusing categories
        self.shortcut_enter.setEnabled(False)
        self.category_panel.focus_first_item()

    def _focus_grid(self) -> None:
        """Focus the media grid."""
        # Enable Enter shortcut when focusing grid
        self.shortcut_enter.setEnabled(True)
        if self.media_grid.cards:
            # Focus the MediaGrid widget first, then focus first card
            self.media_grid.setFocus()
            self.media_grid.focus_first()

    def _open_file(self, file_path: str) -> None:
        """Open file with default application.

        Args:
            file_path: Path to file to open
        """
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl

        url = QUrl.fromLocalFile(file_path)
        QDesktopServices.openUrl(url)

    def _manage_library(self) -> None:
        """Open library management dialog (reset and rescan)."""
        from PySide6.QtWidgets import QMessageBox

        if not self.controller:
            QMessageBox.warning(
                self,
                "Error",
                "Controller not available. Cannot manage library.",
            )
            return

        # Confirm action
        reply = QMessageBox.question(
            self,
            "Manage Library",
            "This action will clear the entire current library and rescan the selected folders.\n\n"
            "Do you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # Reset library
            if self.controller.reset_library():
                QMessageBox.information(
                    self,
                    "Completed",
                    "Library updated successfully!",
                )
            else:
                QMessageBox.warning(
                    self,
                    "Warning",
                    "Library update was cancelled or not completed.",
                )

    def _show_shortcuts(self) -> None:
        """Show shortcuts dialog."""
        from .shortcuts_dialog import ShortcutsDialog

        dialog = ShortcutsDialog(self)
        dialog.exec()

    def _show_about(self) -> None:
        """Show about dialog."""
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.about(
            self,
            "About Videoteka",
            "Videoteka Media Center v0.1.0\n\n"
            "A desktop media center for Linux\n"
            "with streaming-style interface.",
        )

    def set_media_files(self, media_files: list, thumbnail_generator=None) -> None:
        """Set media files to display.

        Args:
            media_files: List of media file dictionaries
            thumbnail_generator: Optional thumbnail generator instance
        """
        # This will be called by the controller
        self.media_grid.add_media_files(media_files, thumbnail_generator)

