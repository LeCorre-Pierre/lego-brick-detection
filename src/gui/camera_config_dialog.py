"""
Camera configuration dialog for Lego Brick Detection application.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QSpinBox, QGroupBox, QDialogButtonBox, QListWidget, QListWidgetItem,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import List, Optional
from ..models.video_source import VideoSource
from ..vision.camera_scanner import CameraScanner
from ..vision.video_utils import VideoCaptureManager
from ..utils.logger import get_logger

logger = get_logger("camera_config_dialog")

class CameraConfigDialog(QDialog):
    """Dialog for configuring camera settings."""

    # Signals
    camera_selected = pyqtSignal(VideoSource)  # Emitted when a camera is selected and tested

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logger
        self.scanner = CameraScanner()
        self.available_devices = []
        self.selected_device = None

        self._setup_ui()
        self._scan_devices()
        self.logger.info("Camera config dialog initialized")

    def _setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Configure Camera")
        self.setModal(True)
        self.resize(500, 400)

        layout = QVBoxLayout()

        # Device selection group
        device_group = QGroupBox("Camera Device")
        device_layout = QVBoxLayout()

        self.device_list = QListWidget()
        self.device_list.itemSelectionChanged.connect(self._on_device_selected)
        device_layout.addWidget(self.device_list)

        device_group.setLayout(device_layout)
        layout.addWidget(device_group)

        # Device info group
        info_group = QGroupBox("Device Information")
        info_layout = QVBoxLayout()

        self.info_label = QLabel("Select a camera device to view information")
        info_layout.addWidget(self.info_label)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Test controls
        test_layout = QHBoxLayout()

        self.test_button = QPushButton("Test Camera")
        self.test_button.clicked.connect(self._test_camera)
        self.test_button.setEnabled(False)
        test_layout.addWidget(self.test_button)

        self.preview_button = QPushButton("Preview")
        self.preview_button.clicked.connect(self._preview_camera)
        self.preview_button.setEnabled(False)
        test_layout.addWidget(self.preview_button)

        layout.addLayout(test_layout)

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._accept_selection)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def _scan_devices(self):
        """Scan for available camera devices."""
        self.device_list.clear()
        self.available_devices = self.scanner.scan_devices()

        if not self.available_devices:
            self.device_list.addItem("No camera devices found")
            self.logger.warning("No camera devices found")
            return

        for device in self.available_devices:
            item = QListWidgetItem(device.get_display_name())
            item.setData(Qt.ItemDataRole.UserRole, device)
            self.device_list.addItem(item)

        self.logger.info(f"Found {len(self.available_devices)} camera devices")

    def _on_device_selected(self):
        """Handle device selection."""
        current_item = self.device_list.currentItem()
        if current_item and current_item.data(Qt.ItemDataRole.UserRole):
            device = current_item.data(Qt.ItemDataRole.UserRole)
            self.selected_device = device
            self.test_button.setEnabled(True)
            self.preview_button.setEnabled(True)

            # Update info display
            info_text = f"""
Device ID: {device.device_id}
Resolution: {device.width}x{device.height}
FPS: {device.fps}
Type: {device.source_type.value}
"""
            self.info_label.setText(info_text.strip())
        else:
            self.selected_device = None
            self.test_button.setEnabled(False)
            self.preview_button.setEnabled(False)
            self.info_label.setText("Select a camera device to view information")

    def _test_camera(self):
        """Test the selected camera device."""
        if not self.selected_device:
            return

        try:
            manager = VideoCaptureManager()
            if manager.open(self.selected_device.device_id,
                          self.selected_device.width,
                          self.selected_device.height,
                          self.selected_device.fps):

                # Try to read a frame
                frame = manager.read_frame()
                manager.close()

                if frame is not None:
                    QMessageBox.information(self, "Test Successful",
                                          f"Camera {self.selected_device.get_display_name()} is working correctly!")
                    self.logger.info(f"Camera test successful: {self.selected_device.get_display_name()}")
                else:
                    QMessageBox.warning(self, "Test Failed",
                                      "Camera opened but failed to read frames. Check camera connection.")
                    self.logger.warning(f"Camera test failed - no frames: {self.selected_device.get_display_name()}")
            else:
                QMessageBox.warning(self, "Test Failed",
                                  f"Failed to open camera {self.selected_device.get_display_name()}")
                self.logger.error(f"Camera test failed - cannot open: {self.selected_device.get_display_name()}")

        except Exception as e:
            QMessageBox.critical(self, "Test Error", f"Error testing camera: {e}")
            self.logger.error(f"Camera test error: {e}")

    def _preview_camera(self):
        """Show a preview of the selected camera."""
        # TODO: Implement camera preview dialog
        QMessageBox.information(self, "Preview", "Camera preview not yet implemented")
        self.logger.info("Camera preview requested")

    def _accept_selection(self):
        """Accept the current selection."""
        if self.selected_device:
            self.camera_selected.emit(self.selected_device)
            self.logger.info(f"Camera selected: {self.selected_device.get_display_name()}")
            self.accept()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a camera device first")
            self.logger.warning("No camera selected")

    def get_selected_device(self) -> Optional[VideoSource]:
        """Get the selected camera device."""
        return self.selected_device