"""
Main entry point for Lego Brick Detection application.
"""

import sys
import argparse
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt
from .gui.main_window import MainWindow
from .utils.logger import get_logger

logger = get_logger("main")

def create_application_icon():
    """Create a simple application icon for the Lego Brick Detector."""
    # Create a 64x64 pixel icon
    pixmap = QPixmap(64, 64)
    pixmap.fill(QColor(240, 240, 240))  # Light gray background

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Draw a red Lego brick shape
    brick_color = QColor(200, 50, 50)  # Red brick
    painter.setBrush(brick_color)
    painter.setPen(Qt.PenStyle.NoPen)

    # Main brick body
    painter.drawRect(8, 20, 48, 24)

    # Brick studs (dots on top)
    stud_color = QColor(220, 70, 70)  # Lighter red for studs
    painter.setBrush(stud_color)
    painter.drawEllipse(12, 12, 8, 8)  # Stud 1
    painter.drawEllipse(28, 12, 8, 8)  # Stud 2
    painter.drawEllipse(44, 12, 8, 8)  # Stud 3

    painter.end()

    return QIcon(pixmap)

def main():
    """Main application entry point."""
    try:
        start_time = time.time()
        logger.info("Starting Lego Brick Detection application")

        # Parse command line arguments
        parser = argparse.ArgumentParser(description='Lego Brick Detection Application')
        parser.add_argument('--set-file', '-s', type=str,
                           help='Path to Lego set CSV file to load automatically')
        parser.add_argument('--camera', '-c', type=int,
                           help='Camera device index to use (if not specified, camera will not be auto-configured)')

        args = parser.parse_args()
        arg_parse_time = time.time()
        logger.info(f"Arg parse took {arg_parse_time - start_time:.2f}s")

        app = QApplication(sys.argv)
        app_creation_time = time.time()
        logger.info(f"QApplication creation took {app_creation_time - arg_parse_time:.2f}s")

        # Set application icon and branding
        app_icon = create_application_icon()
        app.setWindowIcon(app_icon)
        app.setApplicationName("Lego Brick Detector")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("Lego Detection Tools")
        logger.info("Application icon and branding set")

        # Create and show main window with optional arguments
        window_creation_time = time.time()
        window = MainWindow(set_file=args.set_file, camera_index=args.camera)
        window_creation_end_time = time.time()
        logger.info(f"MainWindow creation took {window_creation_end_time - window_creation_time:.2f}s")

        window.show()
        logger.info("Main window shown")

        # Force processing of events to ensure window is displayed
        app.processEvents()
        logger.info("Processed initial events")

        total_startup_time = time.time() - start_time
        logger.info(f"Total startup took {total_startup_time:.2f}s")

        # Ensure the application doesn't quit immediately
        logger.info("Application GUI initialized, entering event loop")

        # Run application
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Application error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()