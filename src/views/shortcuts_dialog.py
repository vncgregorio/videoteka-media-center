"""Dialog showing keyboard shortcuts."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QScrollArea,
    QWidget,
    QGridLayout,
)


class ShortcutsDialog(QDialog):
    """Dialog displaying all keyboard shortcuts."""

    def __init__(self, parent=None):
        """Initialize shortcuts dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Keyboard Shortcuts")
        self.setMinimumSize(700, 600)
        self.setModal(True)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Keyboard Shortcuts")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff; margin: 10px;")
        layout.addWidget(title)

        # Scroll area for shortcuts
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: #1a1a1a; border: none;")

        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(20, 20, 20, 20)

        # Define shortcuts by category
        shortcuts = {
            "Grid Navigation": [
                ("← →", "Navigate between columns"),
                ("↑ ↓", "Navigate between rows"),
                ("Home", "Go to first item"),
                ("End", "Go to last item"),
            ],
            "Actions": [
                ("Enter", "Open selected file"),
                ("Esc", "Close dialogs / Return to grid"),
            ],
            "Panel Navigation": [
                ("C", "Focus categories panel"),
                ("G", "Focus files grid"),
            ],
            "Categories": [
                ("↑ ↓", "Navigate between categories"),
                ("Enter", "Select category"),
            ],
        }

        row = 0
        for category, items in shortcuts.items():
            # Category header
            cat_label = QLabel(category)
            cat_label.setStyleSheet(
                "font-size: 14px; font-weight: bold; color: #0078d4; margin-top: 10px;"
            )
            scroll_layout.addWidget(cat_label, row, 0, 1, 2)
            row += 1

            # Shortcuts in this category
            for shortcut, description in items:
                shortcut_label = QLabel(f"<b>{shortcut}</b>")
                shortcut_label.setStyleSheet("color: #ffffff; padding: 5px;")
                shortcut_label.setMinimumWidth(150)

                desc_label = QLabel(description)
                desc_label.setStyleSheet("color: #cccccc; padding: 5px;")

                scroll_layout.addWidget(shortcut_label, row, 0)
                scroll_layout.addWidget(desc_label, row, 1)
                row += 1

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Don't show again checkbox
        self.dont_show_checkbox = QCheckBox("Don't show again")
        self.dont_show_checkbox.setStyleSheet("color: #ffffff;")
        layout.addWidget(self.dont_show_checkbox)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

        # Set dialog style
        self.setStyleSheet(
            """
            QDialog {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            QPushButton {
                background-color: #2a2a2a;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 8px 16px;
                color: #ffffff;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
            }
            QCheckBox {
                color: #ffffff;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            """
        )

    def should_show_again(self) -> bool:
        """Check if dialog should be shown again.

        Returns:
            True if should show again, False otherwise
        """
        return not self.dont_show_checkbox.isChecked()

