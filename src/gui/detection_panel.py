"""Detection control panel UI component."""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import pyqtSignal
from ..utils.logger import get_logger

logger = get_logger("detection_panel")


class DetectionPanel(QWidget):
    """Detection toggle panel with button and status display."""

    # Signals
    detection_toggled = pyqtSignal(bool)  # Emitted when toggle button clicked (True=enable, False=disable)
    state_changed = pyqtSignal(str)       # Emitted when state changes (state label)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logger
        self.is_detection_active = False
        self.is_enabled = False
        self.init_ui()
        self.logger.info("Detection panel initialized")

    def init_ui(self):
        """Initialize UI components."""
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Status label
        self.status_label = QLabel("Loading model...")
        self.status_label.setMinimumWidth(150)
        layout.addWidget(self.status_label)

        # Toggle button
        self.toggle_button = QPushButton("Start Detection")
        self.toggle_button.setCheckable(True)
        self.toggle_button.setEnabled(False)  # Disabled until model loads
        self.toggle_button.clicked.connect(self._on_toggle_clicked)
        self.toggle_button.setMinimumHeight(40)
        layout.addWidget(self.toggle_button)

        self.setLayout(layout)
        self._update_button_style()

    def _on_toggle_clicked(self):
        """Handle toggle button click."""
        if not self.is_enabled:
            self.logger.warning("Toggle clicked but detection not ready")
            return

        self.is_detection_active = self.toggle_button.isChecked()
        self.logger.info(f"Detection toggled: {'ON' if self.is_detection_active else 'OFF'}")
        self._update_button_style()
        self.detection_toggled.emit(self.is_detection_active)

    def _update_button_style(self):
        """Update button style based on state."""
        if not self.is_enabled:
            # Loading or error state
            self.toggle_button.setStyleSheet("""
                QPushButton {
                    background-color: #cccccc;
                    color: #666666;
                    border: 1px solid #999999;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """)
            self.toggle_button.setText("Start Detection")
        elif self.is_detection_active:
            # Active state (detection running)
            self.toggle_button.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: 1px solid #1e7e34;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            self.toggle_button.setText("Stop Detection")
        else:
            # Ready state (detection available, not running)
            self.toggle_button.setStyleSheet("""
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border: 1px solid #0056b3;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
            """)
            self.toggle_button.setText("Start Detection")

    def set_loading(self):
        """Set UI to loading state."""
        self.is_enabled = False
        self.is_detection_active = False
        self.toggle_button.setEnabled(False)
        self.toggle_button.setChecked(False)
        self.status_label.setText("Loading model...")
        self._update_button_style()
        self.state_changed.emit("Loading model...")
        self.logger.info("Detection panel state: LOADING")

    def set_ready(self):
        """Set UI to ready state (model loaded, detection available)."""
        self.is_enabled = True
        self.is_detection_active = False
        self.toggle_button.setEnabled(True)
        self.toggle_button.setChecked(False)
        self.status_label.setText("Ready")
        self._update_button_style()
        self.state_changed.emit("Ready")
        self.logger.info("Detection panel state: READY")

    def set_error(self, error_msg: str = "Model Error"):
        """Set UI to error state.
        
        Args:
            error_msg: Error message to display
        """
        self.is_enabled = False
        self.is_detection_active = False
        self.toggle_button.setEnabled(False)
        self.toggle_button.setChecked(False)
        self.status_label.setText(error_msg)
        self.toggle_button.setToolTip(error_msg)
        self._update_button_style()
        self.state_changed.emit(error_msg)
        self.logger.error(f"Detection panel state: ERROR - {error_msg}")

    def set_active(self):
        """Set UI to active state (detection running)."""
        self.is_detection_active = True
        self.toggle_button.setChecked(True)
        self.status_label.setText("Detecting...")
        self._update_button_style()
        self.state_changed.emit("Detecting...")
        self.logger.info("Detection panel state: ACTIVE")

    def set_inactive(self):
        """Set UI to inactive state (detection stopped)."""
        self.is_detection_active = False
        self.toggle_button.setChecked(False)
        self.status_label.setText("Ready")
        self._update_button_style()
        self.state_changed.emit("Ready")
        self.logger.info("Detection panel state: INACTIVE")
