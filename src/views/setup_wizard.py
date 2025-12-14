"""Setup wizard for initial folder configuration."""

from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QProgressBar,
    QMessageBox,
    QFileDialog,
)

from ..models.database import Database
from ..models.media_scanner import MediaScanner


class ScanWorker(QThread):
    """Worker thread for scanning folders."""

    progress = Signal(int, int, str)  # current, total, current_file
    completed = Signal(int)  # total_files
    error = Signal(str)  # error_message

    def __init__(
        self,
        folder_paths: List[str],
        database: Database,
    ):
        """Initialize scan worker.

        Args:
            folder_paths: List of folder paths to scan
            database: Database instance
        """
        super().__init__()
        self.folder_paths = folder_paths
        self.database = database
        self.scanner: Optional[MediaScanner] = None

    def run(self) -> None:
        """Run the scanner."""
        try:
            self.scanner = MediaScanner(
                self.folder_paths,
                self.database,
                progress_callback=self._on_progress,
                completed_callback=self._on_completed,
            )
            self.scanner.start()
            self.scanner.join()
        except Exception as e:
            self.error.emit(str(e))

    def _on_progress(self, current: int, total: int, current_file: str) -> None:
        """Handle progress update.

        Args:
            current: Current file number
            total: Total files
            current_file: Current file path
        """
        self.progress.emit(current, total, current_file)

    def _on_completed(self, total_files: int) -> None:
        """Handle completion.

        Args:
            total_files: Total files processed
        """
        self.completed.emit(total_files)

    def stop_scan(self) -> None:
        """Stop the scanner."""
        if self.scanner:
            self.scanner.stop()


class SetupWizard(QDialog):
    """Setup wizard dialog for folder selection and initial scan."""

    def __init__(self, database: Database, parent=None):
        """Initialize setup wizard.

        Args:
            database: Database instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.database = database
        self.folder_paths: List[str] = []
        self.scan_worker: Optional[ScanWorker] = None

        self.setWindowTitle("Videoteka - Initial Setup")
        self.setMinimumSize(600, 500)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the UI."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Welcome to Videoteka Media Center")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            "Select the folders that contain your multimedia files.\n"
            "The application will scan these folders and organize your files."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Folder list
        list_label = QLabel("Selected folders:")
        layout.addWidget(list_label)

        self.folder_list = QListWidget()
        layout.addWidget(self.folder_list)

        # Buttons for folder management
        folder_buttons = QHBoxLayout()
        self.add_button = QPushButton("Add Folder")
        self.add_button.clicked.connect(self._add_folder)
        folder_buttons.addWidget(self.add_button)

        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self._remove_folder)
        folder_buttons.addWidget(self.remove_button)

        layout.addLayout(folder_buttons)

        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.progress_label = QLabel()
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.confirm_button = QPushButton("Confirm and Scan")
        self.confirm_button.clicked.connect(self._confirm_and_scan)
        button_layout.addWidget(self.confirm_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def _add_folder(self) -> None:
        """Add a folder to the list."""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Folder with Multimedia Files"
        )
        if folder:
            folder_path = str(Path(folder).resolve())
            if folder_path not in self.folder_paths:
                self.folder_paths.append(folder_path)
                self.folder_list.addItem(folder_path)

    def _remove_folder(self) -> None:
        """Remove selected folder from list."""
        current_item = self.folder_list.currentItem()
        if current_item:
            folder_path = current_item.text()
            self.folder_paths.remove(folder_path)
            self.folder_list.takeItem(self.folder_list.row(current_item))

    def _confirm_and_scan(self) -> None:
        """Confirm folder selection and start scanning."""
        if not self.folder_paths:
            QMessageBox.warning(
                self, "Warning", "Please select at least one folder."
            )
            return

        # Disable buttons during scan
        self.add_button.setEnabled(False)
        self.remove_button.setEnabled(False)
        self.confirm_button.setEnabled(False)
        self.cancel_button.setEnabled(False)

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(0)  # Indeterminate
        self.progress_label.setVisible(True)
        self.progress_label.setText("Starting scan...")

        # Start scan worker
        self.scan_worker = ScanWorker(self.folder_paths, self.database)
        self.scan_worker.progress.connect(self._on_scan_progress)
        self.scan_worker.completed.connect(self._on_scan_completed)
        self.scan_worker.error.connect(self._on_scan_error)
        self.scan_worker.start()

    def _on_scan_progress(self, current: int, total: int, current_file: str) -> None:
        """Handle scan progress update.

        Args:
            current: Current file number
            total: Total files
            current_file: Current file being processed
        """
        if total > 0:
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(current)
            self.progress_label.setText(
                f"Processando: {current}/{total}\n{Path(current_file).name if current_file else ''}"
            )

    def _on_scan_completed(self, total_files: int) -> None:
        """Handle scan completion.

        Args:
            total_files: Total files processed
        """
        self.progress_bar.setValue(self.progress_bar.maximum())
        self.progress_label.setText(f"Scan completed! {total_files} files found.")
        QMessageBox.information(
            self,
            "Completed",
            f"Scan completed successfully!\n{total_files} multimedia files were found and added to the library.",
        )
        self.accept()

    def _on_scan_error(self, error_message: str) -> None:
        """Handle scan error.

        Args:
            error_message: Error message
        """
        QMessageBox.critical(self, "Error", f"Error during scan:\n{error_message}")
        self._reset_ui()

    def _reset_ui(self) -> None:
        """Reset UI to initial state."""
        self.add_button.setEnabled(True)
        self.remove_button.setEnabled(True)
        self.confirm_button.setEnabled(True)
        self.cancel_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)

    def closeEvent(self, event) -> None:
        """Handle close event."""
        if self.scan_worker and self.scan_worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Confirm",
                "Scanning is in progress. Do you really want to cancel?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self.scan_worker.stop_scan()
                self.scan_worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


