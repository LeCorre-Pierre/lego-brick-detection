"""
Main entry point for Lego Brick Detection application.
"""

import sys
import argparse
import time
from PyQt6.QtWidgets import QApplication
from .gui.main_window import MainWindow
from .utils.logger import get_logger

logger = get_logger("main")

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
        logger.info(".2f")

        app = QApplication(sys.argv)
        app_creation_time = time.time()
        logger.info(".2f")

        # Create and show main window with optional arguments
        window_creation_time = time.time()
        window = MainWindow(set_file=args.set_file, camera_index=args.camera)
        window_creation_end_time = time.time()
        logger.info(".2f")

        window.show()
        logger.info("Main window shown")

        # Force processing of events to ensure window is displayed
        app.processEvents()
        logger.info("Processed initial events")

        total_startup_time = time.time() - start_time
        logger.info(".2f")

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