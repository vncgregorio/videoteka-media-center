"""Main entry point for Videoteka Media Center."""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

from .controllers.app_controller import AppController


def main() -> int:
    """Main application entry point.

    Returns:
        Exit code
    """
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Videoteka Media Center")
    app.setOrganizationName("Videoteka")
    app.setApplicationVersion("0.1.0")

    # Enable high DPI scaling
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    # Load stylesheet if available
    stylesheet_path = Path(__file__).parent / "resources" / "styles" / "main.qss"
    if not stylesheet_path.exists():
        # Try alternative path (when running as module)
        stylesheet_path = Path(__file__).parent.parent / "src" / "resources" / "styles" / "main.qss"
    if stylesheet_path.exists():
        try:
            with open(stylesheet_path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
        except Exception:
            pass  # Continue without stylesheet if there's an error

    try:
        # Initialize controller
        controller = AppController()

        if not controller.initialize():
            QMessageBox.critical(
                None,
                "Error",
                "Could not initialize the database.\n"
                "Check the data directory permissions.",
            )
            return 1

        # Check if setup is needed
        if not controller.is_setup_complete():
            # Show setup wizard
            if not controller.show_setup_wizard():
                # User cancelled setup
                return 0

        # Show main window
        controller.show_main_window()

        # Run application
        exit_code = app.exec()

        # Cleanup
        controller.cleanup()

        return exit_code

    except Exception as e:
        QMessageBox.critical(
            None,
            "Fatal Error",
            f"A fatal error occurred:\n{str(e)}\n\nThe application will exit.",
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())

