"""
Settings dialog for Lego Brick Detection application.

Provides a user interface for adjusting detection parameters to optimize
performance in different lighting conditions and viewing angles.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox,
    QComboBox, QCheckBox, QGroupBox, QFormLayout, QPushButton, QTabWidget,
    QWidget, QSlider
)
from PyQt6.QtCore import Qt, pyqtSignal

from ..models.detection_params import DetectionParams
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SettingsDialog(QDialog):
    """
    Dialog for configuring detection parameters.

    Allows users to adjust computer vision settings through an intuitive
    graphical interface with real-time validation.
    """

    # Signal emitted when settings are applied
    settings_changed = pyqtSignal(DetectionParams)

    def __init__(self, current_params: DetectionParams = None, parent=None):
        super().__init__(parent)
        self.current_params = current_params or DetectionParams()

        self.setWindowTitle("Detection Settings")
        self.setModal(True)
        self.resize(500, 600)

        self._setup_ui()
        self._load_current_settings()

        logger.info("Settings dialog initialized")

    def _setup_ui(self):
        """Setup the user interface components."""
        layout = QVBoxLayout(self)

        # Create tab widget for organizing settings
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Basic settings tab
        self._create_basic_tab()

        # Advanced settings tab
        self._create_advanced_tab()

        # Performance settings tab
        self._create_performance_tab()

        # Buttons
        button_layout = QHBoxLayout()

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self._apply_settings)
        button_layout.addWidget(self.apply_button)

        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self._reset_to_defaults)
        button_layout.addWidget(self.reset_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def _create_basic_tab(self):
        """Create the basic settings tab."""
        basic_widget = QWidget()
        layout = QFormLayout(basic_widget)

        # Lighting mode
        self.lighting_combo = QComboBox()
        self.lighting_combo.addItems(["Auto", "Bright", "Dim"])
        layout.addRow("Lighting Mode:", self.lighting_combo)

        # Detection sensitivity
        self.confidence_slider = QSlider(Qt.Orientation.Horizontal)
        self.confidence_slider.setRange(0, 100)
        self.confidence_slider.setTickInterval(10)
        self.confidence_slider.setTickPosition(QSlider.TickPosition.TicksBelow)

        self.confidence_label = QLabel("70%")
        self.confidence_slider.valueChanged.connect(
            lambda v: self.confidence_label.setText(f"{v}%")
        )

        confidence_layout = QHBoxLayout()
        confidence_layout.addWidget(self.confidence_slider)
        confidence_layout.addWidget(self.confidence_label)
        layout.addRow("Detection Sensitivity:", confidence_layout)

        # Color threshold
        self.color_threshold_spin = QSpinBox()
        self.color_threshold_spin.setRange(0, 255)
        layout.addRow("Color Threshold:", self.color_threshold_spin)

        # Angle tolerance
        self.angle_tolerance_spin = QSpinBox()
        self.angle_tolerance_spin.setRange(0, 90)
        self.angle_tolerance_spin.setSuffix("°")
        layout.addRow("Angle Tolerance:", self.angle_tolerance_spin)

        self.tab_widget.addTab(basic_widget, "Basic")

    def _create_advanced_tab(self):
        """Create the advanced settings tab."""
        advanced_widget = QWidget()
        layout = QFormLayout(advanced_widget)

        # Size constraints
        self.min_size_spin = QSpinBox()
        self.min_size_spin.setRange(1, 1000)
        layout.addRow("Minimum Brick Size:", self.min_size_spin)

        self.max_size_spin = QSpinBox()
        self.max_size_spin.setRange(1, 2000)
        layout.addRow("Maximum Brick Size:", self.max_size_spin)

        # Brightness and contrast
        self.brightness_spin = QDoubleSpinBox()
        self.brightness_spin.setRange(0.1, 3.0)
        self.brightness_spin.setSingleStep(0.1)
        layout.addRow("Brightness Compensation:", self.brightness_spin)

        self.contrast_spin = QDoubleSpinBox()
        self.contrast_spin.setRange(0.1, 3.0)
        self.contrast_spin.setSingleStep(0.1)
        layout.addRow("Contrast Enhancement:", self.contrast_spin)

        # Advanced options
        self.perspective_check = QCheckBox("Enable perspective correction")
        layout.addRow(self.perspective_check)

        self.morphology_check = QCheckBox("Enable morphological filtering")
        layout.addRow(self.morphology_check)

        self.tab_widget.addTab(advanced_widget, "Advanced")

    def _create_performance_tab(self):
        """Create the performance settings tab."""
        performance_widget = QWidget()
        layout = QFormLayout(performance_widget)

        # Frame processing
        self.frame_skip_spin = QSpinBox()
        self.frame_skip_spin.setRange(0, 10)
        layout.addRow("Frame Skip (0 = process all):", self.frame_skip_spin)

        # ROI margin
        self.roi_margin_spin = QSpinBox()
        self.roi_margin_spin.setRange(0, 50)
        layout.addRow("ROI Margin (pixels):", self.roi_margin_spin)

        # Edge detection threshold
        self.edge_threshold_spin = QSpinBox()
        self.edge_threshold_spin.setRange(0, 255)
        layout.addRow("Edge Detection Threshold:", self.edge_threshold_spin)

        self.tab_widget.addTab(performance_widget, "Performance")

    def _load_current_settings(self):
        """Load current parameter values into the UI."""
        params = self.current_params

        # Basic tab
        lighting_map = {"auto": 0, "bright": 1, "dim": 2}
        self.lighting_combo.setCurrentIndex(lighting_map.get(params.lighting_mode, 0))

        self.confidence_slider.setValue(int(params.min_confidence * 100))
        self.color_threshold_spin.setValue(params.color_threshold)
        self.angle_tolerance_spin.setValue(params.angle_tolerance)

        # Advanced tab
        self.min_size_spin.setValue(params.min_brick_size)
        self.max_size_spin.setValue(params.max_brick_size)
        self.brightness_spin.setValue(params.brightness_compensation)
        self.contrast_spin.setValue(params.contrast_enhancement)
        self.perspective_check.setChecked(params.perspective_correction)
        self.morphology_check.setChecked(params.morphological_operations)

        # Performance tab
        self.frame_skip_spin.setValue(params.frame_skip)
        self.roi_margin_spin.setValue(params.roi_margin)
        self.edge_threshold_spin.setValue(params.edge_detection_threshold)

    def _get_settings_from_ui(self) -> DetectionParams:
        """Extract parameter values from the UI."""
        lighting_modes = ["auto", "bright", "dim"]

        return DetectionParams(
            min_confidence=self.confidence_slider.value() / 100.0,
            confidence_threshold=max(0.3, self.confidence_slider.value() / 100.0 - 0.1),
            lighting_mode=lighting_modes[self.lighting_combo.currentIndex()],
            brightness_compensation=self.brightness_spin.value(),
            contrast_enhancement=self.contrast_spin.value(),
            color_threshold=self.color_threshold_spin.value(),
            min_brick_size=self.min_size_spin.value(),
            max_brick_size=self.max_size_spin.value(),
            angle_tolerance=self.angle_tolerance_spin.value(),
            perspective_correction=self.perspective_check.isChecked(),
            frame_skip=self.frame_skip_spin.value(),
            roi_margin=self.roi_margin_spin.value(),
            morphological_operations=self.morphology_check.isChecked(),
            edge_detection_threshold=self.edge_threshold_spin.value()
        )

    def _apply_settings(self):
        """Apply the current settings and emit the signal."""
        try:
            new_params = self._get_settings_from_ui()
            self.current_params = new_params
            self.settings_changed.emit(new_params)
            logger.info("Detection settings applied successfully")
        except ValueError as e:
            logger.error(f"Invalid settings: {e}")
            # Could show error dialog here

    def _reset_to_defaults(self):
        """Reset all settings to default values."""
        self.current_params = DetectionParams()
        self._load_current_settings()
        logger.info("Settings reset to defaults")

    def get_current_params(self) -> DetectionParams:
        """Get the currently applied parameters."""
        return self.current_params