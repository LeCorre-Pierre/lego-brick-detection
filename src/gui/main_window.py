"""
Main window for Lego Brick Detection application using PyQt6.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QMessageBox, QDialog, QLabel, QListWidget, QListWidgetItem, QGroupBox
)
from PyQt6.QtCore import QPoint, QThread, pyqtSignal, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QColor
import time

import numpy as np

from ..utils.logger import get_logger
from .set_info_panel import SetInfoPanel
from ..loaders.set_loader import SetLoader
from .camera_config_dialog import CameraConfigDialog
from ..models.video_source import VideoSource
from .video_display import VideoDisplayWidget
from ..vision.brick_detector import BrickDetector
from .settings_dialog import SettingsDialog
from ..utils.config_manager import ConfigManager
from ..models.detection_params import DetectionParams

logger = get_logger("main_window")


class ModelLoader(QThread):
    """Worker thread for loading the brick detection model asynchronously."""
    
    finished = pyqtSignal(object)  # Signal emitted when model is loaded
    error = pyqtSignal(str)        # Signal emitted on loading error
    
    def __init__(self):
        super().__init__()
        self.brick_detector = None
        
    def run(self):
        """Load the model in the background thread."""
        try:
            # Simulate model loading time (in real implementation, this would load ML models)
            import time
            time.sleep(2)  # Simulate 2 seconds of model loading
            
            # Create the brick detector
            self.brick_detector = BrickDetector()
            self.finished.emit(self.brick_detector)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window for Lego Brick Detection."""

    def __init__(self, set_file=None, camera_index=0):
        init_start_time = time.time()
        super().__init__()
        self.logger = logger
        self.current_set = None
        self.current_video_source = None
        self.brick_detector = None  # Will be loaded asynchronously
        self.is_detecting = False
        self.model_loading = True

        # Configuration management
        self.config_manager = ConfigManager()
        self.detection_params = self.config_manager.load_detection_params() or DetectionParams()

        self.init_ui()
        ui_init_time = time.time()
        self.logger.info(".2f")

        self.setup_menus()
        menu_setup_time = time.time()
        self.logger.info(".2f")

        self.setup_status_bar()
        status_bar_time = time.time()
        self.logger.info(".2f")

        # Start asynchronous model loading
        self._start_model_loading()

        # Auto-load set and camera if provided
        if set_file:
            self._auto_load_set(set_file)
        if camera_index is not None:
            self._auto_configure_camera(camera_index)

        # Auto-start detection if both set and camera are available
        self._check_and_start_detection()

        total_init_time = time.time() - init_start_time
        self.logger.info(".2f")

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Lego Brick Detector")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout
        main_layout = QVBoxLayout(central_widget)

        # Set info panel at top
        self.set_info_panel = SetInfoPanel()
        main_layout.addWidget(self.set_info_panel)

        # Create horizontal layout for video and brick list
        content_layout = QHBoxLayout()

        # Video display in the center
        self.video_display = VideoDisplayWidget()
        self.video_display.brick_clicked.connect(self._on_brick_clicked)
        self.video_display.frame_processed.connect(self._on_frame_processed)
        content_layout.addWidget(self.video_display)

        # Brick list on the right (extracted from set_info_panel)
        self.brick_list_panel = self._create_brick_list_panel()
        content_layout.addWidget(self.brick_list_panel)

        main_layout.addLayout(content_layout)

        # Control buttons at bottom
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)

        # Start/Stop buttons
        self.start_button = QPushButton("Start Detection")
        self.start_button.clicked.connect(self.start_detection)
        self.start_button.setEnabled(False)  # Initially disabled until model loads
        control_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Detection")
        self.stop_button.clicked.connect(self.stop_detection)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)

        control_layout.addStretch()

        main_layout.addWidget(control_panel)

        self.logger.info("UI initialized")

    def _create_brick_list_panel(self):
        """Create a separate panel for the brick list."""
        from PyQt6.QtWidgets import QGroupBox, QVBoxLayout

        # Brick list group
        brick_group = QGroupBox("Bricks in Set")
        brick_layout = QVBoxLayout()

        self.brick_list = QListWidget()
        self.brick_list.itemChanged.connect(self._on_brick_list_changed)
        brick_layout.addWidget(self.brick_list)

        brick_group.setLayout(brick_layout)
        brick_group.setFixedWidth(300)  # Fixed width for the brick list panel

        return brick_group

    def _on_brick_list_changed(self, item):
        """Handle brick checkbox state change from the brick list."""
        if self.current_set:
            brick_id = item.data(Qt.ItemDataRole.UserRole)
            if brick_id:
                brick = self.current_set.get_brick_by_part_number(brick_id)
                if brick:
                    checked = item.checkState() == Qt.CheckState.Checked
                    
                    if checked and not brick.is_fully_found():
                        # Mark as found if checkbox is checked and brick is not fully found
                        if self.current_set.mark_brick_found(brick_id, brick.quantity - brick.found_quantity):
                            self.logger.info(f"Marked brick {brick_id} as fully found via checkbox")
                        else:
                            self.logger.warning(f"Could not mark brick {brick_id} as found")
                    elif not checked and brick.is_fully_found():
                        # Unmark as found if checkbox is unchecked and brick is fully found
                        if self.current_set.unmark_brick_found(brick_id, brick.found_quantity):
                            self.logger.info(f"Unmarked brick {brick_id} as found via checkbox")
                        else:
                            self.logger.warning(f"Could not unmark brick {brick_id}")

                    # Update UI
                    self.set_info_panel.load_set(self.current_set)
                    # Don't call _update_brick_list here to avoid recursion, just update the current item
                    self._update_brick_list_item(item, brick)
                else:
                    self.logger.warning(f"Brick {brick_id} not found in current set")

    def _update_brick_list(self):
        """Update the brick list display with checkboxes."""
        self.brick_list.clear()

        if not self.current_set:
            return

        for brick in self.current_set.bricks:
            # Create display text
            text = f"{brick.name} ({brick.id}) - {brick.found_quantity}/{brick.quantity}"

            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, brick.id)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            
            # Set checked state based on whether brick is fully found
            if brick.is_fully_found():
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)

            # Color coding
            if brick.is_fully_found():
                item.setBackground(QColor(144, 238, 144))  # light green
            elif brick.found_quantity > 0:
                item.setBackground(QColor(255, 255, 224))  # light yellow
            else:
                item.setBackground(QColor(255, 255, 255))  # white

            self.brick_list.addItem(item)

    def _update_brick_list_item(self, item, brick):
        """Update a single brick list item."""
        # Update display text
        text = f"{brick.name} ({brick.id}) - {brick.found_quantity}/{brick.quantity}"
        item.setText(text)
        
        # Update check state
        if brick.is_fully_found():
            item.setCheckState(Qt.CheckState.Checked)
        else:
            item.setCheckState(Qt.CheckState.Unchecked)
        
        # Update color coding
        if brick.is_fully_found():
            item.setBackground(QColor(144, 238, 144))  # light green
        elif brick.found_quantity > 0:
            item.setBackground(QColor(255, 255, 224))  # light yellow
        else:
            item.setBackground(QColor(255, 255, 255))  # white

    def _start_model_loading(self):
        """Start asynchronous model loading."""
        # Set initial status text
        self.video_display.update_model_loading_status(is_loading=True)
        
        self.model_loader = ModelLoader()
        self.model_loader.finished.connect(self._on_model_loaded)
        self.model_loader.error.connect(self._on_model_error)
        self.model_loader.start()
        self.logger.info("Started asynchronous model loading")

    def _on_model_loaded(self, brick_detector):
        """Called when the model has finished loading."""
        self.brick_detector = brick_detector
        self.model_loading = False

        # Apply current detection parameters to the detector
        if self.brick_detector:
            self.brick_detector.set_detection_params(self.detection_params)

        # Update status text to show detection is active
        self.video_display.update_model_loading_status(is_loading=False)

        # Enable detection features
        self.start_button.setEnabled(True)

        self.logger.info("Model loaded successfully, detection features enabled")

        # Check if we can auto-start detection now
        self._check_and_start_detection()

    def _on_model_error(self, error_msg):
        """Called when model loading fails."""
        self.model_loading = False
        
        # Update status text to show error
        self.video_display.set_status_text(f"Model Load Error: {error_msg}", visible=True)
        
        QMessageBox.critical(self, "Model Loading Error", f"Failed to load AI model: {error_msg}")
        self.logger.error(f"Model loading failed: {error_msg}")

    def _check_and_start_detection(self):
        """Check if both set and camera are available and auto-start detection."""
        if self.current_set and self.current_video_source and not self.is_detecting and not self.model_loading:
            self.logger.info("Both set and camera available, auto-starting detection")
            self.start_detection()
        elif self.model_loading:
            self.logger.info("Model still loading, detection will start automatically when ready")
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

        # Settings menu
        settings_menu = menubar.addMenu('Settings')

        detection_settings_action = QAction('Detection Settings...', self)
        detection_settings_action.triggered.connect(self.show_detection_settings)
        settings_menu.addAction(detection_settings_action)

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
                self._update_brick_list()
                self.start_button.setEnabled(True)
                self.status_bar.showMessage(f"Loaded set: {lego_set.name}")
                self.logger.info(f"Set loaded: {lego_set.name} from {file_path}")
                # Check if we can auto-start detection
                self._check_and_start_detection()
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
                # Check if we can auto-start detection
                self._check_and_start_detection()
        else:
            self.logger.info("Camera configuration cancelled")

    def _on_camera_selected(self, video_source: VideoSource):
        """Handle camera selection from dialog."""
        self.current_video_source = video_source
        self.logger.debug(f"Camera selected: {video_source.get_display_name()}")

    def _auto_load_set(self, file_path: str):
        """Automatically load a Lego set from the specified file path."""
        try:
            loader = SetLoader()
            lego_set = loader.load_from_csv(file_path)
            self.current_set = lego_set
            self.set_info_panel.load_set(lego_set)
            self.start_button.setEnabled(True)
            self.status_bar.showMessage(f"Auto-loaded set: {lego_set.name}")
            self.logger.info(f"Set auto-loaded: {lego_set.name} from {file_path}")
            # Check if we can auto-start detection
            self._check_and_start_detection()
        except Exception as e:
            # Log error instead of showing dialog during initialization
            self.logger.error(f"Failed to auto-load set: {e}")
            self.status_bar.showMessage(f"Failed to load set: {e}")

    def _auto_configure_camera(self, camera_index: int):
        """Automatically configure camera with the specified index."""
        try:
            from ..models.video_source import VideoSource, VideoSourceType
            from ..vision.camera_scanner import CameraScanner

            scanner = CameraScanner()
            devices = scanner.scan_devices()

            if camera_index < len(devices):
                selected_device = devices[camera_index]
                self.current_video_source = selected_device
                self.status_bar.showMessage(f"Auto-configured camera: {selected_device.get_display_name()}")
                self.logger.info(f"Camera auto-configured: {selected_device.get_display_name()}")
                # Check if we can auto-start detection
                self._check_and_start_detection()
            else:
                self.logger.warning(f"Camera index {camera_index} not available. Found {len(devices)} devices.")
                # Use first available camera as fallback
                if devices:
                    self.current_video_source = devices[0]
                    self.status_bar.showMessage(f"Auto-configured camera (fallback): {devices[0].get_display_name()}")
                    self.logger.info(f"Camera auto-configured (fallback): {devices[0].get_display_name()}")
            # Check if we can auto-start detection
            self._check_and_start_detection()
        except Exception as e:
            self.logger.error(f"Failed to auto-configure camera: {e}")
            self.status_bar.showMessage(f"Failed to configure camera: {e}")

    def _check_and_start_detection(self):
        """Check if both set and camera are available and auto-start detection."""
        if self.current_set and self.current_video_source and not self.is_detecting:
            if not self.model_loading:
                if self.video_display.is_playing:
                    # Video is already playing, just enable detection
                    self.logger.info("Enabling detection on existing video stream")
                    self._enable_detection_only()
                else:
                    # Start full detection (video + detection)
                    self.logger.info("Both set and camera available, auto-starting detection")
                    self.start_detection()
            else:
                # Start video preview immediately, detection will start when model loads
                self.logger.info("Camera configured, starting video preview (detection will start when model loads)")
                self._start_video_preview_only()

    def _enable_detection_only(self):
        """Enable detection on an already running video stream."""
        if self.video_display.is_playing and self.current_video_source and self.current_set and not self.model_loading:
            # Set the Lego set for detection
            self.brick_detector.set_lego_set(self.current_set)
            
            # Enable detection
            self.is_detecting = True
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.status_bar.showMessage("Detection running...")
            self.video_display.update_detection_status(is_detecting=True)
            self.logger.info("Detection enabled on existing video stream")

    def _start_video_preview_only(self):
        """Start video preview without enabling detection."""
        if not self.video_display.is_playing and self.current_video_source:
            if self.video_display.start_video(
                self.current_video_source.device_id,
                self.current_video_source.resolution[0],  # width
                self.current_video_source.resolution[1],  # height
                self.current_video_source.frame_rate
            ):
                self.video_display.update_detection_status(is_detecting=False)
                self.status_bar.showMessage("Preview active (waiting for model to load)")
                self.logger.info("Video preview started (detection disabled until model loads)")
            else:
                self.logger.error("Failed to start video preview")

    def start_detection(self):
        """Start brick detection."""
        if self.model_loading:
            self.logger.info("Model still loading, cannot start detection yet")
            return
            
        if not self.current_set:
            QMessageBox.warning(self, "Warning", "Please load a set first")
            return

        if not self.current_video_source:
            QMessageBox.warning(self, "Warning", "Please configure a camera first")
            return

        # Set the Lego set for detection
        self.brick_detector.set_lego_set(self.current_set)

        # Start video display if not already running
        if not self.video_display.is_playing:
            if not self.video_display.start_video(
                self.current_video_source.device_id,
                self.current_video_source.resolution[0],  # width
                self.current_video_source.resolution[1],  # height
                self.current_video_source.frame_rate
            ):
                QMessageBox.critical(self, "Error", "Failed to start video capture")
                self.logger.error("Failed to start video capture for detection")
                return

        # Enable detection
        self.is_detecting = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_bar.showMessage("Detection running...")
        self.video_display.update_detection_status(is_detecting=True)
        self.logger.info("Detection started")

    def stop_detection(self):
        """Stop brick detection."""
        self.is_detecting = False
        # Note: Video continues running, only detection is stopped
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_bar.showMessage("Detection stopped (preview active)")
        self.video_display.update_detection_status(is_detecting=False)
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

        # Note: Automatic marking removed - detection is now manual only
        # The detections are still used for visual overlays but don't automatically mark bricks as found

        # Update the set info panel (progress will only show manually marked bricks)
        self.set_info_panel.load_set(self.current_set)
        self._update_brick_list()

    def _on_brick_clicked(self, brick_id: str, click_pos: QPoint):
        """Handle brick click from video display - toggle detection status."""
        if self.current_set:
            brick = self.current_set.get_brick_by_part_number(brick_id)
            if brick:
                if brick.is_fully_found():
                    # Unmark one instance as found
                    if self.current_set.unmark_brick_found(brick_id, 1):
                        self.logger.info(f"Unmarked brick {brick_id} as found (clicked in video)")
                    else:
                        self.logger.warning(f"Could not unmark brick {brick_id}")
                else:
                    # Mark one instance as found
                    if self.current_set.mark_brick_found(brick_id, 1):
                        self.logger.info(f"Marked brick {brick_id} as found (clicked in video)")
                    else:
                        self.logger.warning(f"Could not mark brick {brick_id} as found")

                # Update UI
                self.set_info_panel.load_set(self.current_set)
                self._update_brick_list()
            else:
                self.logger.warning(f"Brick {brick_id} not found in current set")

    def show_detection_settings(self):
        """Show the detection settings dialog."""
        if not hasattr(self, 'settings_dialog'):
            self.settings_dialog = SettingsDialog(self.detection_params, self)
            self.settings_dialog.settings_changed.connect(self._on_settings_changed)
        else:
            # Update with current parameters
            self.settings_dialog.current_params = self.detection_params
            self.settings_dialog._load_current_settings()

        self.settings_dialog.exec()

    def _on_settings_changed(self, new_params: DetectionParams):
        """Handle settings changes from the dialog."""
        self.detection_params = new_params

        # Apply to brick detector if loaded
        if self.brick_detector:
            self.brick_detector.set_detection_params(new_params)

        # Save to persistent storage
        self.config_manager.save_detection_params(new_params)

        self.logger.info("Detection settings updated and saved")

    def closeEvent(self, event):
        """Handle application close event."""
        if self.is_detecting:
            self.stop_detection()
        self.logger.info("Application closing")
        event.accept()