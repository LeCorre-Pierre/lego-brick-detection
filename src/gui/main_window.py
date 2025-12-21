"""
Main window for Lego Brick Detection application using PyQt6.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QMessageBox, QDialog, QLabel, QListWidget, QListWidgetItem, QGroupBox
)
from PyQt6.QtCore import QPoint, QThread, pyqtSignal, Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QColor
import time

import numpy as np

from ..utils.logger import get_logger
from .set_info_panel import SetInfoPanel
from ..loaders.set_loader import SetLoader, SetCSVLoader
from .camera_config_dialog import CameraConfigDialog
from ..models.video_source import VideoSource
from .video_display import VideoDisplayWidget
from ..vision.brick_detector import BrickDetector
from ..vision.camera_scanner import VideoSourceConfigurator
from .settings_dialog import SettingsDialog
from ..utils.config_manager import ConfigManager
from ..models.detection_params import DetectionParams

logger = get_logger("main_window")


class ModelLoader(QThread):
    """Worker thread for loading the brick detection model asynchronously."""
    
    finished = pyqtSignal(object)  # Signal emitted when model is loaded
    error = pyqtSignal(str)        # Signal emitted on loading error
    progress = pyqtSignal(str)     # Signal emitted for progress updates
    
    def __init__(self):
        super().__init__()
        self.brick_detector = None
        
    def run(self):
        """Load the model in the background thread."""
        try:
            self.progress.emit("Loading AI models...")
            
            # Simulate model loading time (in real implementation, this would load ML models)
            import time
            time.sleep(2)  # Simulate 2 seconds of model loading
            
            # Create the brick detector
            self.brick_detector = BrickDetector()
            self.progress.emit("AI models loaded successfully")
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
        
        # Defer configuration loading to background for rapid startup
        self.config_manager = None
        self.detection_params = DetectionParams()  # Use defaults initially
        self.config_loaded = False

        # Store auto-load parameters for deferred execution
        self.pending_set_file = set_file
        self.pending_camera_index = camera_index

        self.init_ui()
        ui_init_time = time.time()
        self.logger.info(".2f")

        self.setup_menus()
        menu_setup_time = time.time()
        self.logger.info(".2f")

        self.setup_status_bar()
        status_bar_time = time.time()
        self.logger.info(".2f")

        # Start background initialization after UI is responsive
        QTimer.singleShot(0, self._deferred_initialization)

        total_init_time = time.time() - init_start_time
        self.logger.info(".2f")

    def _deferred_initialization(self):
        """Perform initialization tasks after UI is responsive."""
        self.logger.info("Starting deferred initialization")
        
        # Initialize progress tracking
        self.init_progress = {
            'set_loaded': False,
            'camera_configured': False,
            'model_loaded': False
        }
        
        # Load configuration first (fast)
        self._load_configuration_async()
        
        # Start parallel initialization threads
        self._start_parallel_initialization()
        
    def _start_parallel_initialization(self):
        """Start all initialization threads in parallel."""
        # 1. Lego set loading thread
        if self.pending_set_file:
            self.set_loader = SetCSVLoader(self.pending_set_file)
            self.set_loader.finished.connect(self._on_set_loaded)
            self.set_loader.error.connect(self._on_set_error)
            self.set_loader.progress.connect(self._on_init_progress)
            self.set_loader.start()
        
        # 2. Video source configuration thread
        if self.pending_camera_index is not None:
            self.video_configurator = VideoSourceConfigurator(self.pending_camera_index)
            self.video_configurator.finished.connect(self._on_camera_configured)
            self.video_configurator.error.connect(self._on_camera_error)
            self.video_configurator.progress.connect(self._on_init_progress)
            self.video_configurator.start()
        
        # 3. Model loading thread
        self.model_loader = ModelLoader()
        self.model_loader.finished.connect(self._on_model_loaded)
        self.model_loader.error.connect(self._on_model_error)
        self.model_loader.progress.connect(self._on_init_progress)
        self.model_loader.start()
        
    def _on_init_progress(self, message: str):
        """Handle progress updates from initialization threads."""
        self.logger.info(f"Init progress: {message}")
        self.status_bar.showMessage(message)
        
    def _on_set_loaded(self, lego_set):
        """Handle successful set loading."""
        self.current_set = lego_set
        self.set_info_panel.load_set(lego_set)
        self._update_brick_list()
        self.init_progress['set_loaded'] = True
        self.logger.info(f"Set loaded: {lego_set.name}")
        self._check_auto_start_detection()
        
    def _on_set_error(self, error_msg: str):
        """Handle set loading error."""
        self.logger.error(f"Set loading failed: {error_msg}")
        self.status_bar.showMessage(f"Failed to load set: {error_msg}")
        
    def _on_camera_configured(self, video_source):
        """Handle successful camera configuration."""
        self.current_video_source = video_source
        self.init_progress['camera_configured'] = True
        self.logger.info(f"Camera configured: {video_source.get_display_name()}")
        self._check_auto_start_detection()
        
    def _on_camera_error(self, error_msg: str):
        """Handle camera configuration error."""
        self.logger.error(f"Camera configuration failed: {error_msg}")
        self.status_bar.showMessage(f"Failed to configure camera: {error_msg}")
        
    def _check_auto_start_detection(self):
        """Check if we can auto-start detection after initialization with error recovery."""
        try:
            if self.init_progress['set_loaded'] and self.init_progress['camera_configured'] and self.init_progress['model_loaded']:
                self.logger.info("All initialization complete, auto-starting detection")
                self.start_detection()
        except Exception as e:
            self.logger.error(f"Failed to auto-start detection: {e}")
            # Don't show error dialog for auto-start, just log

    def _load_configuration_async(self):
        """Load configuration asynchronously (actually just deferred to avoid blocking UI)."""
        def load_config():
            try:
                self.config_manager = ConfigManager()
                loaded_params = self.config_manager.load_detection_params()
                if loaded_params:
                    self.detection_params = loaded_params
                    self.config_loaded = True
                    self.logger.info("Configuration loaded successfully")
                    
                    # Apply loaded parameters to detector if it exists
                    if self.brick_detector:
                        self.brick_detector.set_detection_params(self.detection_params)
                        self.logger.info("Applied loaded configuration to detector")
                else:
                    self.config_loaded = True
                    self.logger.info("Using default configuration")
            except Exception as e:
                self.logger.error(f"Failed to load configuration: {e}")
                self.config_loaded = True  # Mark as loaded even on error
        
        # Defer configuration loading to avoid blocking UI
        QTimer.singleShot(10, load_config)

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Lego Brick Detector v1.0 - Find Your Missing Pieces")
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
        self.start_button.setToolTip("Start real-time brick detection using loaded set and camera (F5)")
        self.start_button.clicked.connect(self.start_detection)
        self.start_button.setEnabled(False)  # Initially disabled until model loads
        control_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Detection")
        self.stop_button.setToolTip("Stop detection and video stream (F6)")
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
        """Update the brick list display with checkboxes and error recovery."""
        try:
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
        except Exception as e:
            self.logger.error(f"Failed to update brick list: {e}")
            # Don't show error dialog for UI updates, just log

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

    def _on_model_loaded(self, brick_detector):
        """Called when the model has finished loading."""
        self.brick_detector = brick_detector
        self.model_loading = False
        self.init_progress['model_loaded'] = True

        # Apply current detection parameters to the detector
        if self.brick_detector:
            self.brick_detector.set_detection_params(self.detection_params)

        # Update status text to show detection is active
        self.video_display.update_model_loading_status(is_loading=False)

        # Enable detection features
        self.start_button.setEnabled(True)

        self.logger.info("Model loaded successfully, detection features enabled")

        # Check if we can auto-start detection now
        self._check_auto_start_detection()

    def _on_model_error(self, error_msg):
        """Called when model loading fails."""
        self.model_loading = False
        self.logger.error(f"Model loading failed: {error_msg}")
        self.status_bar.showMessage(f"Model loading failed: {error_msg}")
        self.video_display.set_status_text(f"Model Load Error: {error_msg}", visible=True)

    def setup_menus(self):
        """Setup application menus."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')

        load_action = QAction('Load Set...', self)
        load_action.setShortcut('Ctrl+O')
        load_action.setToolTip("Load a Lego set from CSV file to define bricks to detect")
        load_action.triggered.connect(self.load_set)
        file_menu.addAction(load_action)

        file_menu.addSeparator()

        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setToolTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Camera menu
        camera_menu = menubar.addMenu('Camera')

        config_action = QAction('Configure...', self)
        config_action.setShortcut('Ctrl+C')
        config_action.setToolTip("Configure camera device and test video stream")
        config_action.triggered.connect(self.configure_camera)
        camera_menu.addAction(config_action)

        # Detection menu
        detection_menu = menubar.addMenu('Detection')

        start_action = QAction('Start', self)
        start_action.setShortcut('F5')
        start_action.setToolTip("Start real-time brick detection")
        start_action.triggered.connect(self.start_detection)
        detection_menu.addAction(start_action)

        stop_action = QAction('Stop', self)
        stop_action.setShortcut('F6')
        stop_action.setToolTip("Stop detection and video stream")
        stop_action.triggered.connect(self.stop_detection)
        detection_menu.addAction(stop_action)

        # Settings menu
        settings_menu = menubar.addMenu('Settings')

        detection_settings_action = QAction('Detection Settings...', self)
        detection_settings_action.setShortcut('Ctrl+,')
        detection_settings_action.setToolTip("Adjust detection parameters for lighting and angles")
        detection_settings_action.triggered.connect(self.show_detection_settings)
        settings_menu.addAction(detection_settings_action)

        # Help menu
        help_menu = menubar.addMenu('Help')

        about_action = QAction('About', self)
        about_action.setToolTip("Show information about Lego Brick Detector")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        help_action = QAction('Help', self)
        help_action.setShortcut('F1')
        help_action.setToolTip("Show help documentation")
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

    def setup_status_bar(self):
        """Setup status bar."""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

    def load_set(self):
        """Load a Lego set from file with error recovery."""
        try:
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(
                self, "Load Lego Set", "", "CSV files (*.csv);;All files (*)"
            )

            if not file_path:
                return  # User cancelled

            # Validate file exists and is readable
            import os
            if not os.path.exists(file_path):
                QMessageBox.critical(self, "File Error", f"File does not exist:\n{file_path}")
                return

            if not os.access(file_path, os.R_OK):
                QMessageBox.critical(self, "Permission Error", f"Cannot read file:\n{file_path}")
                return

            # Check file size (reasonable limit)
            file_size = os.path.getsize(file_path)
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                QMessageBox.warning(self, "Large File", "This file is quite large. Loading may take some time.")
            elif file_size == 0:
                QMessageBox.critical(self, "Empty File", "The selected file is empty.")
                return

            # Load the set
            loader = SetLoader()
            lego_set = loader.load_from_csv(file_path)

            # Validate the loaded set
            if not lego_set.bricks:
                QMessageBox.warning(self, "Empty Set", "The loaded set contains no bricks.")
                return

            self.current_set = lego_set
            self.set_info_panel.load_set(lego_set)
            self._update_brick_list()
            self.start_button.setEnabled(True)
            self.status_bar.showMessage(f"Loaded set: {lego_set.name}")
            self.logger.info(f"Set loaded: {lego_set.name} from {file_path}")

            # Check if we can auto-start detection
            self._check_auto_start_detection()

        except PermissionError as e:
            QMessageBox.critical(self, "Permission Error", f"Cannot access the file:\n{e}")
            self.logger.error(f"Permission error loading set: {e}")
        except UnicodeDecodeError as e:
            QMessageBox.critical(self, "Encoding Error", f"The file contains invalid characters:\n{e}\n\nTry saving the file with UTF-8 encoding.")
            self.logger.error(f"Encoding error loading set: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load set:\n{e}")
            self.logger.error(f"Failed to load set: {e}")

    def configure_camera(self):
        """Configure camera settings with error recovery."""
        try:
            dialog = CameraConfigDialog(self)
            dialog.camera_selected.connect(self._on_camera_selected)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                selected_device = dialog.get_selected_device()
                if selected_device:
                    self.current_video_source = selected_device
                    self.status_bar.showMessage(f"Camera configured: {selected_device.get_display_name()}")
                    self.logger.info(f"Camera configured: {selected_device.get_display_name()}")
                    # Check if we can auto-start detection
                    self._check_auto_start_detection()
            else:
                self.logger.info("Camera configuration cancelled")

        except Exception as e:
            QMessageBox.critical(self, "Configuration Error", f"Failed to configure camera:\n{e}")
            self.logger.error(f"Failed to configure camera: {e}")

    def _on_camera_selected(self, video_source: VideoSource):
        """Handle camera selection from dialog."""
        self.current_video_source = video_source
        self.logger.debug(f"Camera selected: {video_source.get_display_name()}")

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
        """Start brick detection with error recovery."""
        try:
            if self.model_loading:
                QMessageBox.information(self, "Please Wait", "Model is still loading. Detection will start automatically when ready.")
                return

            if not self.current_set:
                QMessageBox.warning(self, "Set Required", "Please load a Lego set first.\n\nUse File → Load Set... to select a CSV file.")
                return

            if not self.current_video_source:
                result = QMessageBox.question(self, "Camera Required",
                    "No camera configured. Would you like to configure one now?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if result == QMessageBox.StandardButton.Yes:
                    self.configure_camera()
                return

            # Set the Lego set for detection
            try:
                self.brick_detector.set_lego_set(self.current_set)
            except Exception as e:
                QMessageBox.critical(self, "Detection Setup Error", f"Failed to configure detection for set: {e}")
                self.logger.error(f"Failed to set Lego set for detection: {e}")
                return

            # Start video display if not already running
            if not self.video_display.is_playing:
                try:
                    if not self.video_display.start_video(
                        self.current_video_source.device_id,
                        self.current_video_source.resolution[0],  # width
                        self.current_video_source.resolution[1],  # height
                        self.current_video_source.frame_rate
                    ):
                        QMessageBox.critical(self, "Video Error", "Failed to start video capture.\n\nPlease check your camera connection and try again.")
                        self.logger.error("Failed to start video capture for detection")
                        return
                except Exception as e:
                    QMessageBox.critical(self, "Video Error", f"Failed to initialize video: {e}")
                    self.logger.error(f"Video initialization error: {e}")
                    return

            # Enable detection
            self.is_detecting = True
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.status_bar.showMessage("Detection running...")
            self.video_display.update_detection_status(is_detecting=True)
            self.logger.info("Detection started successfully")

        except Exception as e:
            QMessageBox.critical(self, "Unexpected Error", f"An unexpected error occurred: {e}")
            self.logger.error(f"Unexpected error in start_detection: {e}")
            # Reset UI state
            self.is_detecting = False
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def stop_detection(self):
        """Stop brick detection with error recovery."""
        try:
            self.is_detecting = False
            # Note: Video continues running, only detection is stopped
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.status_bar.showMessage("Detection stopped (preview active)")
            self.video_display.update_detection_status(is_detecting=False)
            self.logger.info("Detection stopped")
        except Exception as e:
            QMessageBox.critical(self, "Stop Error", f"Failed to stop detection:\n{e}")
            self.logger.error(f"Failed to stop detection: {e}")

    def _on_frame_processed(self, frame: np.ndarray):
        """Handle processed video frame for detection with error recovery."""
        if self.is_detecting and self.current_set:
            try:
                # Run detection on the frame
                detections = self.brick_detector.detect_bricks(frame)

                # Update video display with detection overlays
                self.video_display.overlay_detection_results(detections)

                # Update set progress based on stable detections
                stable_detections = self.brick_detector.get_stable_detections()
                self._update_set_progress(stable_detections)

            except Exception as e:
                self.logger.error(f"Error during frame processing: {e}")
                # Don't show error dialog for every frame, just log and continue
                # If this happens repeatedly, the user will notice detection isn't working

    def _update_set_progress(self, detections):
        """Update the set progress based on detected bricks with error recovery."""
        try:
            if not self.current_set or not detections:
                return

            # Note: Automatic marking removed - detection is now manual only
            # The detections are still used for visual overlays but don't automatically mark bricks as found

            # Update the set info panel (progress will only show manually marked bricks)
            self.set_info_panel.load_set(self.current_set)
            self._update_brick_list()
        except Exception as e:
            self.logger.error(f"Failed to update set progress: {e}")
            # Don't show error dialog for progress updates, just log

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

    def show_about(self):
        """Show about dialog."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.about(self, "About Lego Brick Detector",
            "Lego Brick Detector v1.0\n\n"
            "Find your missing Lego bricks quickly using computer vision.\n\n"
            "Load a Lego set, configure your camera, and start detection.\n"
            "Click on detected bricks to mark them as found.\n\n"
            "Built with PyQt6 and OpenCV.")

    def show_help(self):
        """Show help dialog."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Help - Lego Brick Detector",
            "Getting Started:\n\n"
            "1. Load Set (Ctrl+O): Choose a Lego set CSV file from Rebrickable\n"
            "2. Configure Camera (Ctrl+C): Select webcam or Kinect\n"
            "3. Start Detection (F5): Begin real-time brick detection\n"
            "4. Click Bricks: Mark found bricks by clicking on them\n"
            "5. Stop Detection (F6): End the detection session\n\n"
            "Tips:\n"
            "- Ensure good lighting for best detection\n"
            "- Adjust settings if detection is poor\n"
            "- Use keyboard shortcuts for faster operation\n\n"
            "For more help, visit the project documentation.")

    def closeEvent(self, event):
        """Handle application close event."""
        if self.is_detecting:
            self.stop_detection()
        self.logger.info("Application closing")
        event.accept()