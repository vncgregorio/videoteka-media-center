"""Media card widget for displaying individual media items."""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame,
)


class MediaCard(QFrame):
    """Card widget for displaying a media file."""

    clicked = Signal(str)  # Emits file_path when clicked
    focused = Signal(str)  # Emits file_path when focused

    def __init__(self, file_path: str, file_name: str, file_type: str, thumbnail_path: Optional[str] = None, parent=None):
        """Initialize media card.

        Args:
            file_path: Full path to the media file
            file_name: Name of the file
            file_type: Type of media ('video', 'audio', 'image', 'document')
            thumbnail_path: Path to thumbnail image
            parent: Parent widget
        """
        super().__init__(parent)
        self.file_path = file_path
        self.file_name = file_name
        self.file_type = file_type
        self.thumbnail_path = thumbnail_path

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._setup_ui()
        self._load_thumbnail()

    def _setup_ui(self) -> None:
        """Setup the card UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Thumbnail
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(300, 200)
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setStyleSheet(
            "background-color: #2a2a2a; border-radius: 5px;"
        )
        self.thumbnail_label.setScaledContents(False)
        layout.addWidget(self.thumbnail_label)

        # File name
        self.name_label = QLabel(self.file_name)
        self.name_label.setWordWrap(True)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        layout.addWidget(self.name_label)

        # Type indicator
        type_icon = self._get_type_icon()
        if type_icon:
            type_label = QLabel(type_icon)
            type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            type_label.setStyleSheet("color: #888888; font-size: 10px;")
            layout.addWidget(type_label)

        self.setStyleSheet(
            """
            MediaCard {
                background-color: #1a1a1a;
                border: 2px solid transparent;
                border-radius: 8px;
            }
            MediaCard:hover {
                border-color: #444444;
                background-color: #222222;
            }
            MediaCard:focus {
                border: 3px solid #0078d4;
                background-color: #2a2a2a;
            }
            """
        )

    def _get_type_icon(self) -> str:
        """Get icon/emoji for media type.

        Returns:
            Icon string
        """
        icons = {
            "video": "🎬",
            "audio": "🎵",
            "image": "🖼️",
            "document": "📄",
        }
        return icons.get(self.file_type, "📁")

    def _load_thumbnail(self) -> None:
        """Load thumbnail image."""
        if self.thumbnail_path and Path(self.thumbnail_path).exists():
            pixmap = QPixmap(self.thumbnail_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.thumbnail_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.thumbnail_label.setPixmap(scaled_pixmap)
                return

        # Default placeholder
        self.thumbnail_label.setText(self._get_type_icon())
        self.thumbnail_label.setStyleSheet(
            "background-color: #2a2a2a; border-radius: 5px; color: #666666; font-size: 48px;"
        )

    def mousePressEvent(self, event) -> None:
        """Handle mouse press event."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.file_path)
        super().mousePressEvent(event)

    def focusInEvent(self, event) -> None:
        """Handle focus in event."""
        self.focused.emit(self.file_path)
        super().focusInEvent(event)

    def set_thumbnail(self, thumbnail_path: str) -> None:
        """Update thumbnail.

        Args:
            thumbnail_path: Path to thumbnail image
        """
        self.thumbnail_path = thumbnail_path
        self._load_thumbnail()


