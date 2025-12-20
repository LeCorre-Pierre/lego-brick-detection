"""
Video display widget for Lego Brick Detection application.
"""

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint, QEvent
from typing import Optional, List
import numpy as np
from ..vision.video_utils import VideoCaptureManager, convert_frame_to_qimage, draw_bounding_box
from ..models.detection_result import DetectionResult
from ..vision.color_matcher import ColorMatcher
from ..utils.logger import get_logger

logger = get_logger("video_display")

class VideoDisplayWidget(QWidget):
    """Widget for displaying video feed with detection overlays."""

    # Signals
    frame_processed = pyqtSignal(np.ndarray)  # Emitted when a frame is processed
    brick_clicked = pyqtSignal(str, QPoint)  # Emitted when a brick is clicked (brick_id, click_position)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logger

        # Video components
        self.video_manager = VideoCaptureManager()
        self.current_frame = None
        self.is_playing = False
        self.detection_results = []  # Current detection results
        self.show_overlays = True  # Whether to show detection overlays

        # UI components
        self.video_label = QLabel("No video feed")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
        self.video_label.setMouseTracking(True)  # Enable mouse tracking
        self.video_label.installEventFilter(self)  # Install event filter for mouse events

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        self.setLayout(layout)

        # Timer for frame updates
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frame)

        self.logger.info("Video display widget initialized")

    def start_video(self, device_id: int, width: int = 640, height: int = 480, fps: int = 30) -> bool:
        """Start video capture and display."""
        if self.video_manager.open(device_id, width, height, fps):
            self.is_playing = True
            self.timer.start(int(1000 / fps))  # Convert fps to milliseconds
            self.logger.info(f"Started video display at {fps} fps")
            return True
        else:
            self.logger.error(f"Failed to start video on device {device_id}")
            return False

    def stop_video(self):
        """Stop video capture and display."""
        self.is_playing = False
        self.timer.stop()
        self.video_manager.close()
        self.video_label.setPixmap(QPixmap())  # Clear display
        self.video_label.setText("Video stopped")
        self.logger.info("Video display stopped")

    def _update_frame(self):
        """Update the displayed frame."""
        if not self.is_playing:
            return

        # Read frame
        frame = self.video_manager.read_frame()
        if frame is None:
            self.logger.warning("No frame received")
            return

        # Store current frame
        self.current_frame = frame.copy()

        # Apply detection overlays if enabled
        display_frame = frame.copy()
        if self.show_overlays and self.detection_results:
            display_frame = self._apply_overlays(display_frame, self.detection_results)

        # Emit signal for processing
        self.frame_processed.emit(frame)

        # Convert to QImage and display
        qimage = convert_frame_to_qimage(display_frame)
        if qimage is not None:
            pixmap = QPixmap.fromImage(qimage)
            self.video_label.setPixmap(pixmap)

    def get_current_frame(self) -> Optional[np.ndarray]:
        """Get the current video frame."""
        return self.current_frame.copy() if self.current_frame is not None else None

    def overlay_detection_results(self, results: List[DetectionResult]):
        """Overlay detection results on the current frame."""
        self.detection_results = results

    def _apply_overlays(self, frame: np.ndarray, results: List[DetectionResult]) -> np.ndarray:
        """Apply detection overlays to a frame."""
        try:
            result_frame = frame.copy()

            for detection in results:
                # Create label with brick ID and confidence
                label = f"{detection.brick_id} ({detection.confidence:.2f})"

                # Choose color based on confidence
                if detection.confidence > 0.8:
                    color = (0, 255, 0)  # Green for high confidence
                elif detection.confidence > 0.6:
                    color = (0, 255, 255)  # Yellow for medium confidence
                else:
                    color = (0, 0, 255)  # Red for low confidence

                # Draw bounding box with label
                result_frame = draw_bounding_box(result_frame, detection.bbox, label, color)

            return result_frame

        except Exception as e:
            self.logger.error(f"Error applying overlays: {e}")
            return frame

    def set_overlay_visibility(self, visible: bool):
        """Enable or disable detection overlays."""
        self.show_overlays = visible
        self.logger.info(f"Detection overlays {'enabled' if visible else 'disabled'}")

    def eventFilter(self, obj, event):
        """Handle events for child widgets."""
        if obj == self.video_label and event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                self._handle_mouse_click(event.pos())
            return True  # Event handled
        return super().eventFilter(obj, event)

    def _handle_mouse_click(self, pos: QPoint):
        """Handle mouse click on video display."""
        if not self.detection_results:
            return

        # Convert screen coordinates to frame coordinates
        label_size = self.video_label.size()
        pixmap_size = self.video_label.pixmap()
        if pixmap_size is None:
            return

        # Calculate scaling factors
        scale_x = pixmap_size.width() / label_size.width()
        scale_y = pixmap_size.height() / label_size.height()

        # Adjust for label alignment and scaling
        frame_x = int(pos.x() * scale_x)
        frame_y = int(pos.y() * scale_y)

        click_point = (frame_x, frame_y)

        # Find which detection was clicked
        for detection in self.detection_results:
            if detection.contains_point(click_point):
                self.brick_clicked.emit(detection.brick_id, pos)
                self.logger.debug(f"Brick clicked: {detection.brick_id} at {click_point}")
                break

    def closeEvent(self, event):
        """Handle widget close event."""
        self.stop_video()
        super().closeEvent(event)