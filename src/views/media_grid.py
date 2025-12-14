"""Media grid widget for displaying media files in a grid layout."""

from typing import List, Optional, Dict, Tuple

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QScrollArea,
    QVBoxLayout,
    QLabel,
)

from .media_card import MediaCard


class GridScrollArea(QScrollArea):
    """Custom scroll area that blocks arrow keys to prevent scrolling."""
    
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
        self.focused_card_index = -1
        self.grid_columns = 4  # Number of columns in the grid
        self.card_positions: Dict[int, Tuple[int, int]] = {}  # index -> (row, col)
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

        # Empty state label (initially hidden)
        self.empty_label = QLabel("Nenhum arquivo multimídia encontrado.")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("color: #888888; font-size: 16px; padding: 50px;")
        self.empty_label.setVisible(False)
        layout.addWidget(self.empty_label)

    def clear(self) -> None:
        """Clear all cards from the grid."""
        for card in self.cards:
            card.deleteLater()
        self.cards.clear()
        self.card_positions.clear()
        self.focused_card_index = -1

    def add_media_files(
        self,
        media_files: List[dict],
        thumbnail_generator=None,
    ) -> None:
        """Add media files to the grid.

        Args:
            media_files: List of dictionaries with media file data
            thumbnail_generator: Optional thumbnail generator instance
        """
        self.clear()

        if not media_files:
            self.empty_label.setVisible(True)
            return

        self.empty_label.setVisible(False)

        row = 0
        col = 0

        for index, media_data in enumerate(media_files):
            file_path = media_data.get("file_path", "")
            file_name = media_data.get("file_name", "")
            file_type = media_data.get("file_type", "video")
            thumbnail_path = media_data.get("thumbnail_path")

            # Generate thumbnail if not available and generator provided
            if not thumbnail_path and thumbnail_generator:
                thumbnail_path = thumbnail_generator.generate_thumbnail(
                    file_path, file_type
                )
                if thumbnail_path:
                    # Update database with thumbnail path
                    # This would typically be done by the controller
                    pass

            card = MediaCard(file_path, file_name, file_type, thumbnail_path)
            card.clicked.connect(self.item_clicked.emit)
            card.focused.connect(self.item_focused.emit)

            self.grid_layout.addWidget(card, row, col)
            self.cards.append(card)
            self.card_positions[index] = (row, col)

            col += 1
            if col >= self.grid_columns:
                col = 0
                row += 1

        # Initialize focused_card_index but don't move focus
        # Focus will be set only when user explicitly navigates to grid (via G key)
        if self.cards:
            self.focused_card_index = 0
            # Don't set focus automatically - preserve current focus (e.g., categories)

    def _get_card_position(self, index: int) -> Optional[Tuple[int, int]]:
        """Get grid position (row, col) of card at index.

        Args:
            index: Card index

        Returns:
            Tuple of (row, col) or None
        """
        return self.card_positions.get(index)

    def _find_card_at_position(self, row: int, col: int) -> int:
        """Find card index at given grid position.

        Args:
            row: Row number
            col: Column number

        Returns:
            Card index or -1 if not found
        """
        for index, (r, c) in self.card_positions.items():
            if r == row and c == col:
                return index
        return -1

    def focus_right(self) -> bool:
        """Focus the next card in the same row (next column).

        Returns:
            True if focus moved, False if already at end of row
        """
        if not self.cards:
            return False
        
        # If no card has focus, start from first
        if self.focused_card_index < 0:
            self.focused_card_index = 0

        pos = self._get_card_position(self.focused_card_index)
        if pos is None:
            return False

        current_row, current_col = pos
        next_col = current_col + 1

        # Check if there's a card in the next column of the same row
        target_index = self._find_card_at_position(current_row, next_col)
        if target_index >= 0:
            self.focused_card_index = target_index
            self.cards[target_index].setFocus()
            self.cards[target_index].update()  # Force visual update
            self._ensure_card_visible(target_index)
            return True
        return False

    def focus_left(self) -> bool:
        """Focus the previous card in the same row (previous column).

        Returns:
            True if focus moved, False if already at start of row
        """
        if not self.cards:
            return False
        
        # If no card has focus, start from first
        if self.focused_card_index < 0:
            self.focused_card_index = 0

        pos = self._get_card_position(self.focused_card_index)
        if pos is None:
            return False

        current_row, current_col = pos
        prev_col = current_col - 1

        if prev_col >= 0:
            target_index = self._find_card_at_position(current_row, prev_col)
            if target_index >= 0:
                self.focused_card_index = target_index
                self.cards[target_index].setFocus()
                self.cards[target_index].update()  # Force visual update
                self._ensure_card_visible(target_index)
                return True
        return False

    def focus_down(self) -> bool:
        """Focus the card in the same column, next row.

        Returns:
            True if focus moved, False if already at last row
        """
        if not self.cards:
            return False
        
        # If no card has focus, start from first
        if self.focused_card_index < 0:
            self.focused_card_index = 0

        pos = self._get_card_position(self.focused_card_index)
        if pos is None:
            return False

        current_row, current_col = pos
        next_row = current_row + 1

        # Find card in same column, next row
        target_index = self._find_card_at_position(next_row, current_col)
        if target_index >= 0:
            self.focused_card_index = target_index
            self.cards[target_index].setFocus()
            self.cards[target_index].update()  # Force visual update
            self._ensure_card_visible(target_index)
            return True
        return False

    def focus_up(self) -> bool:
        """Focus the card in the same column, previous row.

        Returns:
            True if focus moved, False if already at first row
        """
        if not self.cards:
            return False
        
        # If no card has focus, start from first
        if self.focused_card_index < 0:
            self.focused_card_index = 0

        pos = self._get_card_position(self.focused_card_index)
        if pos is None:
            return False

        current_row, current_col = pos
        prev_row = current_row - 1

        if prev_row >= 0:
            target_index = self._find_card_at_position(prev_row, current_col)
            if target_index >= 0:
                self.focused_card_index = target_index
                self.cards[target_index].setFocus()
                self.cards[target_index].update()  # Force visual update
                self._ensure_card_visible(target_index)
                return True
        return False

    def focus_next(self) -> bool:
        """Focus the next card (linear navigation).

        Returns:
            True if focus moved, False if already at end
        """
        if not self.cards or self.focused_card_index < 0:
            return False

        if self.focused_card_index < len(self.cards) - 1:
            self.focused_card_index += 1
            self.cards[self.focused_card_index].setFocus()
            self.cards[self.focused_card_index].update()  # Force visual update
            self._ensure_card_visible(self.focused_card_index)
            return True
        return False

    def focus_previous(self) -> bool:
        """Focus the previous card (linear navigation).

        Returns:
            True if focus moved, False if already at start
        """
        if not self.cards or self.focused_card_index < 0:
            return False

        if self.focused_card_index > 0:
            self.focused_card_index -= 1
            self.cards[self.focused_card_index].setFocus()
            self.cards[self.focused_card_index].update()  # Force visual update
            self._ensure_card_visible(self.focused_card_index)
            return True
        return False

    def focus_first(self) -> bool:
        """Focus the first card.

        Returns:
            True if focus moved
        """
        if not self.cards:
            return False

        self.focused_card_index = 0
        self.cards[0].setFocus()
        self.cards[0].update()  # Force visual update
        self._ensure_card_visible(0)
        return True

    def focus_last(self) -> bool:
        """Focus the last card.

        Returns:
            True if focus moved
        """
        if not self.cards:
            return False

        self.focused_card_index = len(self.cards) - 1
        self.cards[self.focused_card_index].setFocus()
        self.cards[self.focused_card_index].update()  # Force visual update
        self._ensure_card_visible(self.focused_card_index)
        return True

    def get_focused_file_path(self) -> Optional[str]:
        """Get file path of currently focused card.

        Returns:
            File path or None
        """
        if 0 <= self.focused_card_index < len(self.cards):
            return self.cards[self.focused_card_index].file_path
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

    def _ensure_card_visible(self, index: int) -> None:
        """Ensure card at index is visible in scroll area.

        Args:
            index: Index of card to make visible
        """
        if 0 <= index < len(self.cards):
            card = self.cards[index]
            # Scroll to make card visible
            self.scroll_area.ensureWidgetVisible(card)


