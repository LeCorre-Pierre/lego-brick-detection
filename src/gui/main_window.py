"""
Main window for Lego Brick Detection application using PyQt6.
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMenuBar, QStatusBar, QFileDialog, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QAction, QPixmap

import numpy as np

from ..utils.logger import get_logger
from .set_info_panel import SetInfoPanel
from ..loaders.set_loader import SetLoader
from .camera_config_dialog import CameraConfigDialog
from ..models.video_source import VideoSource
from .video_display import VideoDisplayWidget
from ..vision.brick_detector import BrickDetector

logger = get_logger("main_window")

class MainWindow(QMainWindow):
    """Main application window for Lego Brick Detection."""

    def __init__(self):
        super().__init__()
        self.logger = logger
        self.current_set = None
        self.current_video_source = None
        self.brick_detector = BrickDetector()
        self.is_detecting = False

        self.init_ui()
        self.setup_menus()
        self.setup_status_bar()

        self.logger.info("Main window initialized")

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Lego Brick Detector")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)

        # Video display area
        self.video_display = VideoDisplayWidget()
        self.video_display.frame_processed.connect(self._on_frame_processed)
        self.video_display.brick_clicked.connect(self._on_brick_clicked)
        layout.addWidget(self.video_display)

        # Control buttons
        button_layout = QHBoxLayout()

        self.load_button = QPushButton("Load Set")
        self.load_button.clicked.connect(self.load_set)
        button_layout.addWidget(self.load_button)

        self.config_button = QPushButton("Configure Camera")
        self.config_button.clicked.connect(self.configure_camera)
        button_layout.addWidget(self.config_button)

        self.start_button = QPushButton("Start Detection")
        self.start_button.clicked.connect(self.start_detection)
        self.start_button.setEnabled(False)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Detection")
        self.stop_button.clicked.connect(self.stop_detection)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        layout.addLayout(button_layout)

        # Set info panel
        self.set_info_panel = SetInfoPanel()
        layout.addWidget(self.set_info_panel)

    def setup_menus(self):
        """Setup application menus."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')

        load_action = QAction('Load Set...', self)
        load_action.triggered.connect(self.load_set)
        file_menu.addAction(load_action)

        file_menu.addSeparator()

        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Camera menu
        camera_menu = menubar.addMenu('Camera')

        config_action = QAction('Configure...', self)
        config_action.triggered.connect(self.configure_camera)
        camera_menu.addAction(config_action)

        # Detection menu
        detection_menu = menubar.addMenu('Detection')

        start_action = QAction('Start', self)
        start_action.triggered.connect(self.start_detection)
        detection_menu.addAction(start_action)

        stop_action = QAction('Stop', self)
        stop_action.triggered.connect(self.stop_detection)
        detection_menu.addAction(stop_action)

    def setup_status_bar(self):
        """Setup status bar."""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

    def load_set(self):
        """Load a Lego set from file."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Load Lego Set", "", "CSV files (*.csv);;All files (*)"
        )

        if file_path:
            try:
                loader = SetLoader()
                lego_set = loader.load_from_csv(file_path)
                self.current_set = lego_set
                self.set_info_panel.load_set(lego_set)
                self.start_button.setEnabled(True)
                self.status_bar.showMessage(f"Loaded set: {lego_set.name}")
                self.logger.info(f"Set loaded: {lego_set.name} from {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load set: {e}")
                self.logger.error(f"Failed to load set: {e}")

    def configure_camera(self):
        """Configure camera settings."""
        dialog = CameraConfigDialog(self)
        dialog.camera_selected.connect(self._on_camera_selected)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_device = dialog.get_selected_device()
            if selected_device:
                self.current_video_source = selected_device
                self.status_bar.showMessage(f"Camera configured: {selected_device.get_display_name()}")
                self.logger.info(f"Camera configured: {selected_device.get_display_name()}")
        else:
            self.logger.info("Camera configuration cancelled")

    def _on_camera_selected(self, video_source: VideoSource):
        """Handle camera selection from dialog."""
        self.current_video_source = video_source
        self.logger.debug(f"Camera selected: {video_source.get_display_name()}")

    def start_detection(self):
        """Start brick detection."""
        if not self.current_set:
            QMessageBox.warning(self, "Warning", "Please load a set first")
            return

        if not self.current_video_source:
            QMessageBox.warning(self, "Warning", "Please configure a camera first")
            return

        # Set the Lego set for detection
        self.brick_detector.set_lego_set(self.current_set)

        # Start video display
        if self.video_display.start_video(
            self.current_video_source.device_id,
            self.current_video_source.resolution[0],  # width
            self.current_video_source.resolution[1],  # height
            self.current_video_source.frame_rate
        ):
            self.is_detecting = True
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.status_bar.showMessage("Detection running...")
            self.logger.info("Detection started")
        else:
            QMessageBox.critical(self, "Error", "Failed to start video capture")
            self.logger.error("Failed to start video capture for detection")

    def stop_detection(self):
        """Stop brick detection."""
        self.is_detecting = False
        self.video_display.stop_video()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_bar.showMessage("Detection stopped")
        self.logger.info("Detection stopped")

    def _on_frame_processed(self, frame: np.ndarray):
        """Handle processed video frame for detection."""
        if self.is_detecting and self.current_set:
            # Run detection on the frame
            detections = self.brick_detector.detect_bricks(frame)

            # Update video display with detection overlays
            self.video_display.overlay_detection_results(detections)

            # Update set progress based on stable detections
            stable_detections = self.brick_detector.get_stable_detections()
            self._update_set_progress(stable_detections)

    def _update_set_progress(self, detections):
        """Update the set progress based on detected bricks."""
        if not self.current_set or not detections:
            return

        # Mark bricks as found based on detections
        for detection in detections:
            self.current_set.mark_brick_found(detection.brick_id)

        # Update the set info panel
        self.set_info_panel.load_set(self.current_set)

    def _on_brick_clicked(self, brick_id: str, click_pos: QPoint):
        """Handle brick click from video display."""
        if self.current_set:
            self.set_info_panel.mark_brick_found_manually(brick_id)
            self.logger.info(f"Brick clicked and marked as found: {brick_id}")

    def closeEvent(self, event):
        """Handle application close event."""
        if self.is_detecting:
            self.stop_detection()
        self.logger.info("Application closing")
        event.accept()