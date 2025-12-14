"""Category panel for navigating media by folder categories."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
)


class CategoryPanel(QWidget):
    """Panel for displaying and selecting categories (folders)."""

    category_selected = Signal(str)  # Emits category name when selected

    def __init__(self, parent=None):
        """Initialize category panel.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.categories: list = []
        self.selected_category: str = ""
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the category panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title
        title = QLabel("Categories")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        layout.addWidget(title)

        # Category list
        self.category_list = QListWidget()
        self.category_list.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.category_list.setStyleSheet(
            """
            QListWidget {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 4px;
                color: #ffffff;
                outline: none;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #2a2a2a;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            QListWidget::item:hover {
                background-color: #2a2a2a;
            }
            QListWidget::item:focus {
                background-color: #333333;
            }
            """
        )
        self.category_list.itemClicked.connect(self._on_category_clicked)
        self.category_list.itemActivated.connect(self._on_category_activated)
        layout.addWidget(self.category_list)

        # Set panel background
        self.setStyleSheet("background-color: #1a1a1a;")
        self.setMaximumWidth(250)
        self.setMinimumWidth(200)

    def set_categories(self, categories: list) -> None:
        """Set list of categories to display.

        Args:
            categories: List of category names
        """
        self.categories = categories
        self.category_list.clear()

        # Add "All" option at the beginning
        all_item = QListWidgetItem("📁 All")
        all_item.setData(Qt.ItemDataRole.UserRole, "")
        self.category_list.addItem(all_item)

        # Add categories
        for category in categories:
            # Display category with icon
            display_text = f"📂 {category}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, category)
            # Set tooltip with full category path for long paths
            item.setToolTip(category)
            self.category_list.addItem(item)

        # Select "Todos" by default
        if self.category_list.count() > 0:
            self.category_list.setCurrentRow(0)
            self.selected_category = ""

    def _on_category_clicked(self, item: QListWidgetItem) -> None:
        """Handle category item click.

        Args:
            item: Clicked list item
        """
        category = item.data(Qt.ItemDataRole.UserRole)
        self.selected_category = category
        self.category_selected.emit(category)

    def _on_category_activated(self, item: QListWidgetItem) -> None:
        """Handle category item activation (Enter key).

        Args:
            item: Activated list item
        """
        self._on_category_clicked(item)

    def get_selected_category(self) -> str:
        """Get currently selected category.

        Returns:
            Selected category name or empty string for "Todos"
        """
        return self.selected_category

    def activate_current_category(self) -> None:
        """Activate the currently selected category item.
        
        This method can be called externally to ensure the category_selected
        signal is emitted for the current item.
        """
        current_item = self.category_list.currentItem()
        if current_item:
            self._on_category_activated(current_item)

    def focus_first_item(self) -> None:
        """Focus the first category item."""
        if self.category_list.count() > 0:
            self.category_list.setCurrentRow(0)
            self.category_list.setFocus()

    def focus_next(self) -> bool:
        """Focus next category item.

        Returns:
            True if focus moved
        """
        current = self.category_list.currentRow()
        if current < self.category_list.count() - 1:
            self.category_list.setCurrentRow(current + 1)
            # Ensure the list widget has focus
            if not self.category_list.hasFocus():
                self.category_list.setFocus()
            # Update selected category
            item = self.category_list.currentItem()
            if item:
                self._on_category_clicked(item)
            return True
        return False

    def focus_previous(self) -> bool:
        """Focus previous category item.

        Returns:
            True if focus moved
        """
        current = self.category_list.currentRow()
        if current > 0:
            self.category_list.setCurrentRow(current - 1)
            # Ensure the list widget has focus
            if not self.category_list.hasFocus():
                self.category_list.setFocus()
            # Update selected category
            item = self.category_list.currentItem()
            if item:
                self._on_category_clicked(item)
            return True
        return False

