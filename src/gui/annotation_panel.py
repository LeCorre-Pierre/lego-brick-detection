"""Annotation mode control panel."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)
from PyQt6.QtCore import pyqtSignal

from ..utils.logger import get_logger

logger = get_logger("annotation_panel")


class AnnotationPanel(QWidget):
    """Panel for controlling annotation capture mode.

    UI (mode OFF) — compact single row:
        [Annotation Mode ●]  [Classe active: —]  [0 captures]

    UI (mode ON) — expanded:
        [■ Annotation Mode]
        Classe active : 3001
        [Capturer  Space]  [Auto-bbox: ☑]
        Compteur : 12 captures — 3001
        [Changer session]  [Exporter data.yaml]
    """

    # Signals
    mode_changed = pyqtSignal(bool)     # True = ON, False = OFF
    capture_requested = pyqtSignal(str)  # part_number

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.logger = logger
        self._annotation_mode = False
        self._active_class: Optional[str] = None
        self._capture_count = 0
        self._session_path: Optional[Path] = None
        self._init_ui()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @property
    def annotation_mode(self) -> bool:
        return self._annotation_mode

    @property
    def active_class(self) -> Optional[str]:
        return self._active_class

    @property
    def auto_bbox_enabled(self) -> bool:
        return self._auto_bbox_check.isChecked()

    def set_active_class(self, part_number: str) -> None:
        """Called when a brick is selected in the brick list."""
        self._active_class = part_number
        self._update_class_label()

    def set_capture_count(self, part_number: str, count: int) -> None:
        """Update the displayed capture counter."""
        self._capture_count = count
        self._update_counter_label()

    def set_session_path(self, path: Path) -> None:
        """Display the current session path."""
        self._session_path = Path(path)
        self._session_label.setText(str(self._session_path))
        self._session_label.setToolTip(str(self._session_path))

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 3, 5, 3)
        layout.setSpacing(8)

        # Toggle button
        self._toggle_btn = QPushButton("Annotation Mode")
        self._toggle_btn.setCheckable(True)
        self._toggle_btn.setMinimumHeight(32)
        self._toggle_btn.clicked.connect(self._on_toggle)
        layout.addWidget(self._toggle_btn)

        # Active class label
        self._class_label = QLabel("Classe active: —")
        layout.addWidget(self._class_label)

        # Capture button (hidden until mode ON)
        self._capture_btn = QPushButton("Capturer  [Space]")
        self._capture_btn.setMinimumHeight(32)
        self._capture_btn.clicked.connect(self._on_capture)
        self._capture_btn.setVisible(False)
        layout.addWidget(self._capture_btn)

        # Auto-bbox checkbox
        self._auto_bbox_check = QCheckBox("Auto-bbox")
        self._auto_bbox_check.setChecked(True)
        self._auto_bbox_check.setVisible(False)
        layout.addWidget(self._auto_bbox_check)

        # Counter label
        self._counter_label = QLabel("0 captures")
        layout.addWidget(self._counter_label)

        # Session path label (hidden until mode ON)
        self._session_label = QLabel("")
        self._session_label.setVisible(False)
        layout.addWidget(self._session_label)

        layout.addStretch()

        self._update_button_style()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _on_toggle(self) -> None:
        self._annotation_mode = self._toggle_btn.isChecked()
        self._capture_btn.setVisible(self._annotation_mode)
        self._auto_bbox_check.setVisible(self._annotation_mode)
        self._session_label.setVisible(self._annotation_mode and self._session_path is not None)
        self._update_button_style()
        self._update_class_label()
        self.mode_changed.emit(self._annotation_mode)
        self.logger.info(f"Annotation mode: {'ON' if self._annotation_mode else 'OFF'}")

    def _on_capture(self) -> None:
        if not self._annotation_mode:
            return
        if not self._active_class:
            self.logger.warning("Capture requested but no active class set")
            return
        self.capture_requested.emit(self._active_class)

    def _update_button_style(self) -> None:
        if self._annotation_mode:
            self._toggle_btn.setText("■ Annotation Mode")
            self._toggle_btn.setStyleSheet(
                "QPushButton { background-color: #e74c3c; color: white;"
                " border-radius: 4px; font-weight: bold; }"
                "QPushButton:hover { background-color: #c0392b; }"
            )
        else:
            self._toggle_btn.setText("Annotation Mode ●")
            self._toggle_btn.setStyleSheet(
                "QPushButton { background-color: #95a5a6; color: white;"
                " border-radius: 4px; }"
                "QPushButton:hover { background-color: #7f8c8d; }"
            )

    def _update_class_label(self) -> None:
        cls = self._active_class or "—"
        self._class_label.setText(f"Classe active: {cls}")

    def _update_counter_label(self) -> None:
        cls = self._active_class or "?"
        self._counter_label.setText(f"{self._capture_count} captures — {cls}")

    # ------------------------------------------------------------------
    # Space shortcut support (called from MainWindow.keyPressEvent)
    # ------------------------------------------------------------------

    def trigger_capture_if_active(self) -> bool:
        """Trigger capture if annotation mode is on and a class is selected.

        Returns True if capture was triggered.
        """
        if self._annotation_mode and self._active_class:
            self._on_capture()
            return True
        return False
