"""
Main entry point for Lego Brick Detection application.
"""

import sys
from PyQt6.QtWidgets import QApplication
from .gui.main_window import MainWindow
from .utils.logger import get_logger

logger = get_logger("main")

def main():
    """Main application entry point."""
    logger.info("Starting Lego Brick Detection application")

    app = QApplication(sys.argv)

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()