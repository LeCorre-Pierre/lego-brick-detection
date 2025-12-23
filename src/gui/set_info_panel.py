"""
Set information display panel for Lego Brick Detection application.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QGroupBox, QProgressBar, QCheckBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from typing import Optional
from ..models.lego_set import LegoSet
from ..utils.logger import get_logger
from ..utils.progress_tracker import ProgressTracker

logger = get_logger("set_info_panel")

class SetInfoPanel(QWidget):
    """Panel displaying information about the loaded Lego set."""

    # Signals
    brick_selected = pyqtSignal(str)  # Emitted when a brick is selected (brick_id)
    detect_scope_changed = pyqtSignal(bool)  # True: detect only set classes; False: detect all classes

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logger
        self.current_set = None
        self.progress_tracker = ProgressTracker()

        self._setup_ui()
        self.logger.info("Set info panel initialized")

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout()

        # Set information group
        set_group = QGroupBox("Lego Set Information")
        set_layout = QVBoxLayout()

        self.set_name_label = QLabel("No set loaded")
        self.set_name_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        set_layout.addWidget(self.set_name_label)

        self.set_stats_label = QLabel("")
        set_layout.addWidget(self.set_stats_label)

        set_group.setLayout(set_layout)
        layout.addWidget(set_group)

        # Progress group
        progress_group = QGroupBox("Collection Progress")
        progress_layout = QVBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%v/%m bricks found (%p%)")
        progress_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("0/0 bricks found")
        progress_layout.addWidget(self.progress_label)

        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        # Detection scope group
        scope_group = QGroupBox("Detection Scope")
        scope_layout = QVBoxLayout()

        self.set_only_checkbox = QCheckBox("Detect only bricks from this set")
        self.set_only_checkbox.setChecked(True)
        self.set_only_checkbox.toggled.connect(self._on_set_only_toggled)
        scope_layout.addWidget(self.set_only_checkbox)

        scope_group.setLayout(scope_layout)
        layout.addWidget(scope_group)

        self.setLayout(layout)

    def load_set(self, lego_set: LegoSet):
        """Load and display information for a Lego set."""
        self.current_set = lego_set
        self.progress_tracker.start_tracking(lego_set)
        self.logger.info(f"Loading set: {lego_set.name}")

        # Update set information
        self.set_name_label.setText(lego_set.name)
        total_bricks = len(lego_set.bricks)
        total_quantity = sum(brick.quantity for brick in lego_set.bricks)
        self.set_stats_label.setText(f"{total_bricks} brick types, {total_quantity} total pieces")

        # Update progress
        self._update_progress()

    def clear_set(self):
        """Clear the current set display."""
        self.current_set = None
        self.set_name_label.setText("No set loaded")
        self.set_stats_label.setText("")
        self.progress_bar.setValue(0)
        self.progress_label.setText("0/0 bricks found")
        self.logger.info("Set cleared")

    def _on_set_only_toggled(self, checked: bool):
        """Emit detection scope change when checkbox toggles."""
        try:
            self.detect_scope_changed.emit(checked)
            scope = "set-only" if checked else "all-classes"
            self.logger.info(f"Detection scope changed -> {scope}")
        except Exception as e:
            self.logger.error(f"Failed to emit detection scope change: {e}")

    def set_detection_scope(self, set_only: bool):
        """Programmatically set detection scope checkbox state."""
        self.set_only_checkbox.setChecked(set_only)

    def update_brick_status(self, brick_id: str, found: bool):
        """Update the status of a specific brick."""
        if self.current_set is None:
            return

        # Find the brick in the set
        brick = next((b for b in self.current_set.bricks if b.id == brick_id), None)
        if brick is None:
            self.logger.warning(f"Brick {brick_id} not found in current set")
            return

        if found:
            brick.mark_found()
        else:
            brick.unmark_found()

        self._update_progress()

    def _update_progress(self):
        """Update the progress bar and label."""
        if self.current_set is None:
            return

        total_quantity = sum(brick.quantity for brick in self.current_set.bricks)
        found_quantity = sum(brick.found_quantity for brick in self.current_set.bricks)

        if total_quantity > 0:
            percentage = int((found_quantity / total_quantity) * 100)
            self.progress_bar.setValue(percentage)
            self.progress_bar.setMaximum(total_quantity)
            self.progress_bar.setFormat(f"{found_quantity}/{total_quantity} bricks found ({percentage}%)")

        self.progress_label.setText(f"{found_quantity}/{total_quantity} bricks found")

    def refresh_progress(self):
        """Refresh progress display without restarting tracking or logging."""
        self._update_progress()

    def mark_brick_found_manually(self, brick_id: str):
        """Mark a brick as found manually (e.g., by clicking)."""
        if not self.current_set:
            return

        if self.current_set.mark_brick_found_by_click(brick_id):
            self.progress_tracker.record_brick_found(brick_id)
            self._update_progress()
            self.logger.info(f"Manually marked brick as found: {brick_id}")
        else:
            self.logger.warning(f"Could not mark brick as found: {brick_id}")
        self.logger.debug(f"Brick selected: {brick_id}")