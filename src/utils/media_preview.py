"""Media preview utilities for audio, images, and PDFs."""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import QUrl, QTimer, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QDialog
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput


class AudioPreviewWidget(QWidget):
    """Widget for previewing audio files."""

    def __init__(self, file_path: str, parent=None):
        """Initialize audio preview.

        Args:
            file_path: Path to audio file
            parent: Parent widget
        """
        super().__init__(parent)
        self.file_path = file_path
        self.player: Optional[QMediaPlayer] = None
        self.audio_output: Optional[QAudioOutput] = None
        self.preview_timer: Optional[QTimer] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup preview UI."""
        layout = QVBoxLayout(self)

        label = QLabel("Preview de Áudio")
        label.setStyleSheet("color: #ffffff; font-size: 14px;")
        layout.addWidget(label)

        self.play_button = QPushButton("▶ Reproduzir Preview (30s)")
        self.play_button.clicked.connect(self._play_preview)
        layout.addWidget(self.play_button)

        self.stop_button = QPushButton("⏹ Parar")
        self.stop_button.clicked.connect(self._stop_preview)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)

    def _play_preview(self) -> None:
        """Play 30-second preview of audio."""
        if not Path(self.file_path).exists():
            return

        try:
            self.player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            self.player.setAudioOutput(self.audio_output)

            url = QUrl.fromLocalFile(self.file_path)
            self.player.setSource(url)

            # Set volume
            self.audio_output.setVolume(0.7)

            # Start playback
            self.player.play()

            # Stop after 30 seconds
            self.preview_timer = QTimer()
            self.preview_timer.setSingleShot(True)
            self.preview_timer.timeout.connect(self._stop_preview)
            self.preview_timer.start(30000)  # 30 seconds

            self.play_button.setEnabled(False)
            self.stop_button.setEnabled(True)

        except Exception:
            pass

    def _stop_preview(self) -> None:
        """Stop audio preview."""
        if self.player:
            self.player.stop()
            self.player = None
        if self.audio_output:
            self.audio_output = None
        if self.preview_timer:
            self.preview_timer.stop()
            self.preview_timer = None

        self.play_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def cleanup(self) -> None:
        """Cleanup resources."""
        self._stop_preview()


class ImagePreviewDialog(QDialog):
    """Dialog for previewing images."""

    def __init__(self, file_path: str, parent=None):
        """Initialize image preview.

        Args:
            file_path: Path to image file
            parent: Parent widget
        """
        super().__init__(parent)
        self.file_path = file_path
        self.setWindowTitle(Path(file_path).name)
        self.setMinimumSize(800, 600)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup preview UI."""
        layout = QVBoxLayout(self)

        # Image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: #000000;")
        layout.addWidget(self.image_label)

        # Load image
        self._load_image()

        # Close button
        close_button = QPushButton("Fechar")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

    def _load_image(self) -> None:
        """Load and display image."""
        if not Path(self.file_path).exists():
            return

        try:
            pixmap = QPixmap(self.file_path)
            if not pixmap.isNull():
                # Scale to fit window while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    self.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.image_label.setPixmap(scaled_pixmap)
        except Exception:
            pass

    def resizeEvent(self, event) -> None:
        """Handle resize event."""
        super().resizeEvent(event)
        self._load_image()


class PDFPreviewDialog(QDialog):
    """Dialog for previewing PDF files (first page)."""

    def __init__(self, file_path: str, parent=None):
        """Initialize PDF preview.

        Args:
            file_path: Path to PDF file
            parent: Parent widget
        """
        super().__init__(parent)
        self.file_path = file_path
        self.setWindowTitle(Path(file_path).name)
        self.setMinimumSize(800, 600)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup preview UI."""
        layout = QVBoxLayout(self)

        # PDF page label
        self.page_label = QLabel()
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_label.setStyleSheet("background-color: #ffffff;")
        layout.addWidget(self.page_label)

        # Load first page
        self._load_first_page()

        # Close button
        close_button = QPushButton("Fechar")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

    def _load_first_page(self) -> None:
        """Load and display first page of PDF."""
        if not Path(self.file_path).exists():
            return

        try:
            import fitz  # PyMuPDF
            from io import BytesIO

            doc = fitz.open(self.file_path)
            if len(doc) == 0:
                doc.close()
                return

            # Get first page
            page = doc[0]
            # Render page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_data = pix.tobytes("ppm")

            # Convert to QPixmap
            from PIL import Image

            img = Image.open(BytesIO(img_data))
            img_bytes = BytesIO()
            img.save(img_bytes, format="PNG")
            img_bytes.seek(0)

            pixmap = QPixmap()
            pixmap.loadFromData(img_bytes.read())
            doc.close()

            if not pixmap.isNull():
                # Scale to fit window
                scaled_pixmap = pixmap.scaled(
                    self.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.page_label.setPixmap(scaled_pixmap)

        except Exception:
            pass

    def resizeEvent(self, event) -> None:
        """Handle resize event."""
        super().resizeEvent(event)
        self._load_first_page()


def show_media_preview(file_path: str, file_type: str, parent=None) -> None:
    """Show preview for a media file.

    Args:
        file_path: Path to media file
        file_type: Type of media
        parent: Parent widget
    """
    if file_type == "audio":
        dialog = QDialog(parent)
        dialog.setWindowTitle("Preview de Áudio")
        layout = QVBoxLayout(dialog)
        preview = AudioPreviewWidget(file_path, dialog)
        layout.addWidget(preview)
        dialog.exec()
        preview.cleanup()
    elif file_type == "image":
        dialog = ImagePreviewDialog(file_path, parent)
        dialog.exec()
    elif file_type == "document":
        dialog = PDFPreviewDialog(file_path, parent)
        dialog.exec()

