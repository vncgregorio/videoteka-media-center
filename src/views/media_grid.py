"""Media grid widget for displaying media files in a grid layout."""

from typing import List, Optional, Dict, Tuple

from PySide6.QtCore import Qt, Signal, QSize, QTimer
from PySide6.QtGui import QKeyEvent, QCloseEvent
from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QScrollArea,
    QVBoxLayout,
    QLabel,
)

from .media_card import MediaCard
from ..utils.thumbnail_worker import ThumbnailWorker


class GridScrollArea(QScrollArea):
    """Custom scroll area that blocks arrow keys to prevent scrolling."""
    
    def __init__(self, parent=None):
        """Initialize scroll area."""
        super().__init__(parent)
        self.verticalScrollBar().valueChanged.connect(self._on_scroll)
        self._scroll_callback = None
    
    def set_scroll_callback(self, callback):
        """Set callback for scroll events."""
        self._scroll_callback = callback
    
    def _on_scroll(self, value):
        """Handle scroll events."""
        if self._scroll_callback:
            self._scroll_callback()
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Block arrow keys - let parent handle navigation."""
        key = event.key()
        # Block arrow keys - don't let scroll area process them
        if key in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right):
            event.ignore()  # Let parent MediaGrid handle it
            return
        # Allow other keys
        super().keyPressEvent(event)


class MediaGrid(QWidget):
    """Grid widget for displaying media cards."""

    item_clicked = Signal(str)  # Emits file_path when item is clicked
    item_focused = Signal(str)  # Emits file_path when item is focused

    def __init__(self, parent=None):
        """Initialize media grid.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.cards: List[MediaCard] = []
        self.focused_media_index = -1  # Tracks position in all_media_files, not cards
        self.grid_columns = 4  # Number of columns in the grid
        self.card_positions: Dict[int, Tuple[int, int]] = {}  # media_index -> (row, col)
        
        # Lazy loading support
        self.all_media_files: List[dict] = []  # All media file data
        self.thumbnail_generator = None
        self.thumbnail_workers: Dict[str, ThumbnailWorker] = {}  # file_path -> worker
        self.visible_range: Tuple[int, int] = (0, 0)  # (start_index, end_index)
        self.items_per_page = 50  # Number of items to render at once
        self.load_more_threshold = 20  # Load more when this many items from end
        self.card_to_index: Dict[MediaCard, int] = {}  # card -> media_index
        
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the grid UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area (custom to block arrow keys)
        self.scroll_area = GridScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("background-color: #121212; border: none;")
        self.scroll_area.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Grid container
        self.grid_widget = QWidget()
        self.grid_widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(15)
        self.grid_layout.setContentsMargins(20, 20, 20, 20)

        self.scroll_area.setWidget(self.grid_widget)
        layout.addWidget(self.scroll_area)
        
        # Connect scroll callback for lazy loading
        self.scroll_area.set_scroll_callback(self._on_scroll)

        # Empty state label (initially hidden)
        self.empty_label = QLabel("Nenhum arquivo multimídia encontrado.")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("color: #888888; font-size: 16px; padding: 50px;")
        self.empty_label.setVisible(False)
        layout.addWidget(self.empty_label)
        
        # Timer for debouncing scroll events
        self.scroll_timer = QTimer(self)
        self.scroll_timer.setSingleShot(True)
        self.scroll_timer.timeout.connect(self._update_visible_items)

    def clear(self) -> None:
        """Clear all cards from the grid."""
        # Cancel and cleanup all thumbnail workers
        for worker in list(self.thumbnail_workers.values()):
            worker.cleanup()  # Use cleanup method which properly terminates thread
            # Note: PySide6 automatically cleans up signals when objects are deleted
            worker.deleteLater()
        self.thumbnail_workers.clear()
        
        # Remove all cards
        for card in self.cards:
            # Clear thumbnails to free memory
            card.clear_thumbnail()
            card.deleteLater()
        self.cards.clear()
        self.card_positions.clear()
        self.card_to_index.clear()
        self.focused_media_index = -1
        self.all_media_files.clear()
        self.visible_range = (0, 0)

    def add_media_files(
        self,
        media_files: List[dict],
        thumbnail_generator=None,
    ) -> None:
        """Add media files to the grid with lazy loading.

        Args:
            media_files: List of dictionaries with media file data
            thumbnail_generator: Optional thumbnail generator instance
        """
        self.clear()

        if not media_files:
            self.empty_label.setVisible(True)
            return

        self.empty_label.setVisible(False)
        self.thumbnail_generator = thumbnail_generator
        
        # Store all media files data
        self.all_media_files = media_files
        
        # Initially load first page of items
        initial_end = min(len(media_files), self.items_per_page)
        self.visible_range = (0, initial_end)
        self._create_cards_for_range(0, initial_end)
        
        # Initialize focused_media_index but don't move focus
        # Focus will be set only when user explicitly navigates to grid (via G key)
        if self.all_media_files:
            self.focused_media_index = 0
            # Don't set focus automatically - preserve current focus (e.g., categories)
    
    def _update_visible_items(self) -> None:
        """Update which items are visible and create/remove cards accordingly."""
        if not self.all_media_files:
            return
        
        # Calculate visible range based on scroll position
        scrollbar = self.scroll_area.verticalScrollBar()
        viewport_height = self.scroll_area.viewport().height()
        scroll_value = scrollbar.value()
        
        # Estimate which items should be visible
        # Each card is approximately 250px tall (200px thumbnail + margins)
        card_height = 250
        cards_per_row = self.grid_columns
        rows_visible = max(3, (viewport_height // card_height) + 2)  # Show a bit extra
        items_visible = rows_visible * cards_per_row
        
        # Calculate start index (rough estimate)
        start_row = max(0, scroll_value // card_height - 1)
        start_index = max(0, start_row * cards_per_row)
        end_index = min(len(self.all_media_files), start_index + items_visible + self.load_more_threshold)
        
        # Expand range to include buffer
        start_index = max(0, start_index - self.load_more_threshold)
        
        # Update visible range
        old_start, old_end = self.visible_range
        self.visible_range = (start_index, end_index)
        
        # Remove cards that are no longer visible
        cards_to_remove = []
        for card in self.cards:
            # Get media index for this card
            media_index = self.card_to_index.get(card)
            
            if media_index is None or media_index < start_index or media_index >= end_index:
                cards_to_remove.append(card)
        
        # Remove cards
        for card in cards_to_remove:
            # Cancel thumbnail worker if exists
            card_file_path = card.file_path
            if card_file_path in self.thumbnail_workers:
                worker = self.thumbnail_workers.pop(card_file_path)
                worker.cleanup()  # Use cleanup method which properly terminates thread
                # Note: PySide6 automatically cleans up signals when objects are deleted
                worker.deleteLater()
            
            # Clear thumbnail to free memory
            card.clear_thumbnail()
            
            # Get media index before removing
            media_index = self.card_to_index.pop(card, None)
            
            # Remove from layout and list
            self.grid_layout.removeWidget(card)
            card.deleteLater()
            if card in self.cards:
                self.cards.remove(card)
            
            # Update card_positions
            if media_index is not None and media_index in self.card_positions:
                del self.card_positions[media_index]
        
        # Create cards for newly visible items
        self._create_cards_for_range(start_index, end_index)
    
    def _create_cards_for_range(self, start_index: int, end_index: int) -> None:
        """Create cards for items in the given range."""
        for index in range(start_index, min(end_index, len(self.all_media_files))):
            # Check if card already exists
            if any(card.file_path == self.all_media_files[index].get("file_path") for card in self.cards):
                continue
            
            media_data = self.all_media_files[index]
            file_path = media_data.get("file_path", "")
            file_name = media_data.get("file_name", "")
            file_type = media_data.get("file_type", "video")
            thumbnail_path = media_data.get("thumbnail_path")

            # Calculate grid position
            row = index // self.grid_columns
            col = index % self.grid_columns
            
            # Create card (thumbnail will be loaded asynchronously)
            card = MediaCard(file_path, file_name, file_type, thumbnail_path)
            card.clicked.connect(self.item_clicked.emit)
            card.focused.connect(self.item_focused.emit)

            self.grid_layout.addWidget(card, row, col)
            self.cards.append(card)
            self.card_positions[index] = (row, col)
            self.card_to_index[card] = index  # Track which media index this card represents
            
            # Start async thumbnail generation if needed
            if not thumbnail_path and self.thumbnail_generator:
                self._load_thumbnail_async(file_path, file_type, card)
    
    def _load_thumbnail_async(self, file_path: str, file_type: str, card: MediaCard) -> None:
        """Load thumbnail asynchronously for a card."""
        # Don't start duplicate workers
        if file_path in self.thumbnail_workers:
            return
        
        # Check cache first
        if self.thumbnail_generator:
            cache_path = self.thumbnail_generator.get_thumbnail_path(file_path)
            if cache_path:
                card.set_thumbnail(cache_path)
                return
        
        # Create worker thread
        worker = ThumbnailWorker(file_path, file_type, self.thumbnail_generator, self)
        worker.thumbnail_ready.connect(lambda fp, tp: self._on_thumbnail_ready(fp, tp, card))
        worker.thumbnail_failed.connect(lambda fp: self._on_thumbnail_failed(fp))
        self.thumbnail_workers[file_path] = worker
        worker.start()
    
    def _on_thumbnail_ready(self, file_path: str, thumbnail_path: str, card: MediaCard) -> None:
        """Handle thumbnail ready signal."""
        if file_path in self.thumbnail_workers:
            worker = self.thumbnail_workers.pop(file_path)
            # Thread should already be finished, but ensure cleanup
            if worker.isRunning():
                worker.wait(100)
            # Note: PySide6 automatically cleans up signals when objects are deleted
            worker.deleteLater()
        
        # Update card thumbnail
        if card and card.file_path == file_path:
            card.set_thumbnail(thumbnail_path)
    
    def _on_thumbnail_failed(self, file_path: str) -> None:
        """Handle thumbnail generation failure."""
        if file_path in self.thumbnail_workers:
            worker = self.thumbnail_workers.pop(file_path)
            # Thread should already be finished, but ensure cleanup
            if worker.isRunning():
                worker.wait(100)
            # Note: PySide6 automatically cleans up signals when objects are deleted
            worker.deleteLater()
    
    def _on_scroll(self) -> None:
        """Handle scroll event (debounced)."""
        self.scroll_timer.start(100)  # Debounce scroll events

    def _get_card_position(self, media_index: int) -> Optional[Tuple[int, int]]:
        """Get grid position (row, col) of media item at index.

        Args:
            media_index: Media file index in all_media_files

        Returns:
            Tuple of (row, col) or None
        """
        return self.card_positions.get(media_index)

    def _get_card_for_media_index(self, media_index: int) -> Optional[MediaCard]:
        """Get card for media index, ensuring it exists.

        Args:
            media_index: Media file index in all_media_files

        Returns:
            MediaCard instance or None if media_index is invalid
        """
        if media_index < 0 or media_index >= len(self.all_media_files):
            return None
        
        # Find existing card
        for card, idx in self.card_to_index.items():
            if idx == media_index:
                return card
        
        # Card doesn't exist - ensure it's in visible range and create it
        start, end = self.visible_range
        if media_index < start or media_index >= end:
            # Expand visible range to include this index
            buffer = self.load_more_threshold
            new_start = max(0, media_index - buffer)
            new_end = min(len(self.all_media_files), media_index + buffer + 1)
            self._create_cards_for_range(new_start, new_end)
            self.visible_range = (new_start, new_end)
        
        # Card should now exist
        for card, idx in self.card_to_index.items():
            if idx == media_index:
                return card
        
        return None

    def _focus_media_index(self, media_index: int) -> bool:
        """Focus media item at given index.

        Args:
            media_index: Media file index in all_media_files

        Returns:
            True if focus was set, False otherwise
        """
        card = self._get_card_for_media_index(media_index)
        if card:
            self.focused_media_index = media_index
            card.setFocus()
            card.update()
            self._ensure_card_visible_for_media_index(media_index)
            return True
        return False

    def _ensure_card_visible_for_media_index(self, media_index: int) -> None:
        """Ensure card for media index is visible in scroll area.

        Args:
            media_index: Media file index in all_media_files
        """
        card = self._get_card_for_media_index(media_index)
        if card:
            self.scroll_area.ensureWidgetVisible(card)

    def focus_right(self) -> bool:
        """Focus the next media item in the same row (next column).

        Returns:
            True if focus moved, False if already at end of row
        """
        if not self.all_media_files:
            return False
        
        # If no item has focus, start from first
        if self.focused_media_index < 0:
            return self._focus_media_index(0)

        # Calculate next media index
        current_row = self.focused_media_index // self.grid_columns
        current_col = self.focused_media_index % self.grid_columns
        next_col = current_col + 1
        
        if next_col < self.grid_columns:
            next_media_index = current_row * self.grid_columns + next_col
            if next_media_index < len(self.all_media_files):
                return self._focus_media_index(next_media_index)
        
        return False

    def focus_left(self) -> bool:
        """Focus the previous media item in the same row (previous column).

        Returns:
            True if focus moved, False if already at start of row
        """
        if not self.all_media_files:
            return False
        
        # If no item has focus, start from first
        if self.focused_media_index < 0:
            return self._focus_media_index(0)

        # Calculate previous media index
        current_row = self.focused_media_index // self.grid_columns
        current_col = self.focused_media_index % self.grid_columns
        prev_col = current_col - 1

        if prev_col >= 0:
            prev_media_index = current_row * self.grid_columns + prev_col
            if prev_media_index >= 0:
                return self._focus_media_index(prev_media_index)
        
        return False

    def focus_down(self) -> bool:
        """Focus the media item in the same column, next row.

        Returns:
            True if focus moved, False if already at last row
        """
        if not self.all_media_files:
            return False
        
        # If no item has focus, start from first
        if self.focused_media_index < 0:
            return self._focus_media_index(0)

        # Calculate next row media index
        current_row = self.focused_media_index // self.grid_columns
        current_col = self.focused_media_index % self.grid_columns
        next_row = current_row + 1
        next_media_index = next_row * self.grid_columns + current_col

        if next_media_index < len(self.all_media_files):
            return self._focus_media_index(next_media_index)
        
        return False

    def focus_up(self) -> bool:
        """Focus the media item in the same column, previous row.

        Returns:
            True if focus moved, False if already at first row
        """
        if not self.all_media_files:
            return False
        
        # If no item has focus, start from first
        if self.focused_media_index < 0:
            return self._focus_media_index(0)

        # Calculate previous row media index
        current_row = self.focused_media_index // self.grid_columns
        current_col = self.focused_media_index % self.grid_columns
        prev_row = current_row - 1

        if prev_row >= 0:
            prev_media_index = prev_row * self.grid_columns + current_col
            if prev_media_index >= 0:
                return self._focus_media_index(prev_media_index)
        
        return False

    def focus_next(self) -> bool:
        """Focus the next media item (linear navigation).

        Returns:
            True if focus moved, False if already at end
        """
        if not self.all_media_files or self.focused_media_index < 0:
            return False

        if self.focused_media_index < len(self.all_media_files) - 1:
            return self._focus_media_index(self.focused_media_index + 1)
        
        return False

    def focus_previous(self) -> bool:
        """Focus the previous media item (linear navigation).

        Returns:
            True if focus moved, False if already at start
        """
        if not self.all_media_files or self.focused_media_index < 0:
            return False

        if self.focused_media_index > 0:
            return self._focus_media_index(self.focused_media_index - 1)
        
        return False

    def focus_first(self) -> bool:
        """Focus the first media item.

        Returns:
            True if focus moved
        """
        if not self.all_media_files:
            return False

        return self._focus_media_index(0)

    def focus_last(self) -> bool:
        """Focus the last media item.

        Returns:
            True if focus moved
        """
        if not self.all_media_files:
            return False

        return self._focus_media_index(len(self.all_media_files) - 1)

    def get_focused_file_path(self) -> Optional[str]:
        """Get file path of currently focused media item.

        Returns:
            File path or None
        """
        if 0 <= self.focused_media_index < len(self.all_media_files):
            return self.all_media_files[self.focused_media_index].get("file_path")
        return None

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle key press events for grid navigation."""
        key = event.key()
        
        # Handle arrow keys - process them here to prevent scroll area from handling
        if key in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right):
            handled = False
            if key == Qt.Key.Key_Right:
                handled = self.focus_right()
            elif key == Qt.Key.Key_Left:
                handled = self.focus_left()
            elif key == Qt.Key.Key_Down:
                handled = self.focus_down()
            elif key == Qt.Key.Key_Up:
                handled = self.focus_up()
            
            if handled:
                event.accept()
                return
        
        # Default: let parent handle
        super().keyPressEvent(event)

    
    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle widget close event - cleanup all threads.
        
        Args:
            event: Close event
        """
        # Cleanup all workers before closing
        for worker in list(self.thumbnail_workers.values()):
            worker.cleanup()
            # Note: PySide6 automatically cleans up signals when objects are deleted
            worker.deleteLater()
        self.thumbnail_workers.clear()
        super().closeEvent(event)


