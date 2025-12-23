"""
Main window for Lego Brick Inventory application using PyQt6.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QMessageBox, QDialog, QLabel, QListWidget, QListWidgetItem, QGroupBox
)
from PyQt6.QtCore import QPoint, QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QAction, QColor
import time
import os
import numpy as np

from ..utils.logger import get_logger
from .set_info_panel import SetInfoPanel
from ..loaders.set_loader import SetLoader, SetCSVLoader
from .camera_config_dialog import CameraConfigDialog
from ..models.video_source import VideoSource
from .video_display import VideoDisplayWidget
from ..vision.camera_scanner import VideoSourceConfigurator
from .detection_panel import DetectionPanel
from ..vision.detection_engine import YOLOv8Engine
from ..vision.model_loader import ModelLoaderThread
from ..vision.detection_state import DetectionState

logger = get_logger("main_window")


class MainWindow(QMainWindow):
    """Main application window for Lego Brick Inventory."""

    def __init__(self, set_file=None, camera_index=0):
        init_start_time = time.time()
        super().__init__()
        self.logger = logger
        self.current_set = None
        self.current_video_source = None

        # Store auto-load parameters for deferred execution
        self.pending_set_file = set_file
        self.pending_camera_index = camera_index

        self.init_ui()
        ui_init_time = time.time()
        self.logger.info(f"UI init took {ui_init_time - init_start_time:.2f}s")

        self.setup_menus()
        menu_setup_time = time.time()
        self.logger.info(f"Menu setup took {menu_setup_time - ui_init_time:.2f}s")

        self.setup_status_bar()
        status_bar_time = time.time()
        self.logger.info(f"Status bar setup took {status_bar_time - menu_setup_time:.2f}s")

        # Start background initialization after UI is responsive
        QTimer.singleShot(0, self._deferred_initialization)

        total_init_time = time.time() - init_start_time
        self.logger.info(f"MainWindow init took {total_init_time:.2f}s")

    def _deferred_initialization(self):
        """Perform initialization tasks after UI is responsive."""
        self.logger.info("Starting deferred initialization")
        
        # Initialize progress tracking
        self.init_progress = {
            'set_loaded': False,
            'camera_configured': False
        }
        
        # Start parallel initialization threads
        self._start_parallel_initialization()
        
    def _start_parallel_initialization(self):
        """Start all initialization threads in parallel."""
        # 0. Model loading thread (detection engine)
        self._start_model_loading()
        
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
    
    def _start_model_loading(self):
        """Start YOLOv8 model loading in background thread."""
        try:
            model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../models")
            # Look for .pt file in models directory
            pt_files = [f for f in os.listdir(model_path) if f.endswith('.pt')]
            
            if pt_files:
                model_file = os.path.join(model_path, pt_files[0])
                self.logger.info(f"Found model: {model_file}")
                
                # Initialize detection engine
                self.detection_engine = YOLOv8Engine()
                self.detection_panel.set_loading()
                
                # Start model loading in background
                self.model_loader = ModelLoaderThread(self.detection_engine, model_file)
                self.model_loader.progress.connect(self._on_model_load_progress)
                self.model_loader.finished.connect(self._on_model_loaded)
                self.model_loader.error.connect(self._on_model_load_error)
                self.model_loader.start()
            else:
                self.logger.warning("No YOLOv8 model (.pt) file found in models/ directory")
                self.detection_engine = None
                self.detection_panel.set_error("No model file found")
                
        except Exception as e:
            self.logger.error(f"Error starting model loading: {e}")
            self.detection_engine = None
            self.detection_panel.set_error(str(e))
    
    def _on_model_load_progress(self, message: str):
        """Handle model loading progress update."""
        self.logger.info(f"Model load progress: {message}")
        self.status_bar.showMessage(message)
    
    def _on_model_loaded(self, success: bool):
        """Handle model loading completion."""
        if success and self.detection_engine:
            self.logger.info("Model loaded successfully")
            self.detection_panel.set_ready()
            self.status_bar.showMessage("Detection ready")
        else:
            self.logger.error("Model loading failed")
            self.detection_panel.set_error("Model load failed")
    
    def _on_model_load_error(self, error_msg: str):
        """Handle model loading error."""
        self.logger.error(f"Model load error: {error_msg}")
        self.detection_panel.set_error(error_msg)
        QMessageBox.warning(self, "Model Load Error", f"Failed to load detection model:\n{error_msg}")
        
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
        self._check_auto_start_video()
        
    def _on_set_error(self, error_msg: str):
        """Handle set loading error."""
        self.logger.error(f"Set loading failed: {error_msg}")
        self.status_bar.showMessage(f"Failed to load set: {error_msg}")
        
    def _on_camera_configured(self, video_source):
        """Handle successful camera configuration."""
        self.current_video_source = video_source
        self.init_progress['camera_configured'] = True
        self.logger.info(f"Camera configured: {video_source.get_display_name()}")
        # Start video preview immediately when camera is configured
        self.start_video()
        
    def _on_camera_error(self, error_msg: str):
        """Handle camera configuration error."""
        self.logger.error(f"Camera configuration failed: {error_msg}")
        self.status_bar.showMessage(f"Failed to configure camera: {error_msg}")
        
    def _check_auto_start_video(self):
        """Check if we can auto-start video after initialization with error recovery."""
        # Only auto-start video if both set and camera are loaded (for legacy/manual triggers)
        try:
            if self.init_progress['set_loaded'] and self.init_progress['camera_configured']:
                self.logger.info("All initialization complete, auto-starting video")
                # Only start video if not already running
                if not self.video_display.is_playing:
                    self.start_video()
        except Exception as e:
            self.logger.error(f"Failed to auto-start video: {e}")
            # Don't show error dialog for auto-start, just log

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Lego Brick Inventory v1.0 - Track Your Collection")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout
        main_layout = QVBoxLayout(central_widget)

        # Set info panel at top
        self.set_info_panel = SetInfoPanel()
        main_layout.addWidget(self.set_info_panel)

        # Detection panel (below set info)
        self.detection_panel = DetectionPanel()
        main_layout.addWidget(self.detection_panel)

        # Create horizontal layout for video and brick list
        content_layout = QHBoxLayout()

        # Video display in the center
        self.video_display = VideoDisplayWidget()
        self.video_display.brick_clicked.connect(self._on_brick_clicked)
        content_layout.addWidget(self.video_display)

        # Brick list on the right (extracted from set_info_panel)
        self.brick_list_panel = self._create_brick_list_panel()
        content_layout.addWidget(self.brick_list_panel)

        main_layout.addLayout(content_layout)

        # Control buttons at bottom
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)

        # Start/Stop buttons
        self.start_button = QPushButton("Start Video")
        self.start_button.setToolTip("Start video preview (F5)")
        self.start_button.clicked.connect(self.start_video)
        self.start_button.setEnabled(False)  # Disabled until camera is configured
        control_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Video")
        self.stop_button.setToolTip("Stop video stream (F6)")
        self.stop_button.clicked.connect(self.stop_video)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)

        # Save preview button
        self.save_button = QPushButton("Save Preview (JPG)")
        self.save_button.setToolTip("Save current preview frame as JPG in 'screenshoot' directory")
        self.save_button.clicked.connect(self.save_preview)
        self.save_button.setEnabled(False)
        control_layout.addWidget(self.save_button)

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
            if self.current_video_source:
                self.start_button.setEnabled(True)
            self.status_bar.showMessage(f"Loaded set: {lego_set.name}")
            self.logger.info(f"Set loaded: {lego_set.name} from {file_path}")

            # Check if we can auto-start video
            self._check_auto_start_video()

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
                    if self.current_set:
                        self.start_button.setEnabled(True)
                    self.status_bar.showMessage(f"Camera configured: {selected_device.get_display_name()}")
                    self.logger.info(f"Camera configured: {selected_device.get_display_name()}")
                    # Check if we can auto-start video
                    self._check_auto_start_video()
            else:
                self.logger.info("Camera configuration cancelled")

        except Exception as e:
            QMessageBox.critical(self, "Configuration Error", f"Failed to configure camera:\n{e}")
            self.logger.error(f"Failed to configure camera: {e}")

    def _on_camera_selected(self, video_source: VideoSource):
        """Handle camera selection from dialog."""
        self.current_video_source = video_source
        self.logger.debug(f"Camera selected: {video_source.get_display_name()}")

    def start_video(self):
        """Start video preview."""
        try:
            if not self.current_set:
                QMessageBox.warning(self, "Set Required", "Please load a Lego set first.")
                return

            if not self.current_video_source:
                result = QMessageBox.question(self, "Camera Required",
                    "No camera configured. Would you like to configure one now?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if result == QMessageBox.StandardButton.Yes:
                    self.configure_camera()
                return

            # Start video display
            if not self.video_display.is_playing:
                if not self.video_display.start_video(
                    self.current_video_source.device_id,
                    self.current_video_source.resolution[0],
                    self.current_video_source.resolution[1],
                    self.current_video_source.frame_rate
                ):
                    QMessageBox.critical(self, "Video Error", "Failed to start video capture.")
                    return

            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.save_button.setEnabled(True)
            self.status_bar.showMessage("Video running")
            self.logger.info("Video started")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
            self.logger.error(f"Error in start_video: {e}")

    def stop_video(self):
        """Stop video preview."""
        try:
            self.video_display.stop_video()
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.save_button.setEnabled(False)
            self.status_bar.showMessage("Video stopped")
            self.logger.info("Video stopped")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to stop video: {e}")
            self.logger.error(f"Failed to stop video: {e}")

    def save_preview(self):
        """Save the current preview frame as a JPG into 'screenshoot/'."""
        try:
            # Use project-local directory 'screenshoot'
            import os
            save_dir = os.path.join(os.getcwd(), "screenshoot")
            path = self.video_display.save_screenshot_jpg(save_dir)
            if path:
                self.status_bar.showMessage(f"Saved preview: {path}")
            else:
                self.status_bar.showMessage("No frame to save or save failed")
        except Exception as e:
            self.logger.error(f"Error while saving preview: {e}")
            QMessageBox.critical(self, "Save Error", f"Failed to save preview: {e}")

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

    def show_about(self):
        """Show about dialog."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.about(self, "About Lego Brick Inventory",
            "Lego Brick Inventory v1.0\n\n"
            "Track your Lego brick collection.\n\n"
            "Load a Lego set and check off bricks as you find them.\n\n"
            "Built with PyQt6 and OpenCV.")

    def show_help(self):
        """Show help dialog."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Help - Lego Brick Inventory",
            "Getting Started:\n\n"
            "1. Load Set (Ctrl+O): Choose a Lego set CSV file\n"
            "2. Configure Camera (Ctrl+C): Select your webcam\n"
            "3. Start Video (F5): Begin video preview\n"
            "4. Check Boxes: Mark bricks as found\n"
            "5. Stop Video (F6): End the video session\n\n"
            "For more help, visit the project documentation.")

    def closeEvent(self, event):
        """Handle application close event."""
        self.video_display.stop_video()
        self.logger.info("Application closing")
        event.accept()