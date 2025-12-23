"""
Video display widget for Lego Brick Detection application.
"""

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint, QEvent
from typing import Optional, List
import numpy as np
import cv2
import os
from datetime import datetime
from ..vision.video_utils import VideoCaptureManager, convert_frame_to_qimage, draw_bounding_box
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

        # UI components
        self.video_label = QLabel("No video feed")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
        self.video_label.setMouseTracking(True)  # Enable mouse tracking
        self.video_label.installEventFilter(self)  # Install event filter for mouse events

        # Status label overlay
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            QLabel {
                color: yellow;
                background-color: rgba(0, 0, 0, 0.7);
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
                border-radius: 3px;
            }
        """)
        self.status_label.setParent(self.video_label)
        self.status_label.move(10, 10)
        self.status_label.hide()  # Initially hidden

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

        # Emit signal for processing
        self.frame_processed.emit(frame)

        # Convert to QImage and display
        qimage = convert_frame_to_qimage(frame)
        if qimage is not None:
            pixmap = QPixmap.fromImage(qimage)
            self.video_label.setPixmap(pixmap)

    def get_current_frame(self) -> Optional[np.ndarray]:
        """Get the current video frame."""
        return self.current_frame.copy() if self.current_frame is not None else None

    def save_screenshot_jpg(self, save_dir: str = "screenshoot") -> Optional[str]:
        """Save the current frame as a JPG in the given directory.

        Returns the saved file path on success, or None if no frame.
        """
        try:
            frame = self.get_current_frame()
            if frame is None:
                self.logger.warning("No frame available to save")
                # brief status overlay feedback
                self.set_status_text("No frame to save", True)
                QTimer.singleShot(1500, lambda: self.set_status_text("", False))
                return None

            # Ensure directory exists
            os.makedirs(save_dir, exist_ok=True)

            # Timestamp up to seconds
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"preview_{ts}.jpg"
            path = os.path.join(save_dir, filename)

            # Write JPG using OpenCV (frame assumed BGR)
            success = cv2.imwrite(path, frame)
            if success:
                self.logger.info(f"Saved screenshot: {path}")
                self.set_status_text(f"Saved: {filename}", True)
                QTimer.singleShot(1500, lambda: self.set_status_text("", False))
                return path
            else:
                self.logger.error(f"Failed to write screenshot: {path}")
                self.set_status_text("Save failed", True)
                QTimer.singleShot(1500, lambda: self.set_status_text("", False))
                return None
        except Exception as e:
            self.logger.error(f"Error saving screenshot: {e}")
            self.set_status_text("Error saving", True)
            QTimer.singleShot(1500, lambda: self.set_status_text("", False))
            return None

    def set_status_text(self, text: str, visible: bool = True):
        """Set the status text overlay."""
        self.status_label.setText(text)
        if visible:
            self.status_label.show()
        else:
            self.status_label.hide()
        self.logger.debug(f"Status text set to: '{text}' (visible: {visible})")

    def eventFilter(self, obj, event):
        """Handle events for child widgets."""
        if obj == self.video_label and event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                # Mouse clicks disabled - no detection overlays
                pass
            return True  # Event handled
        return super().eventFilter(obj, event)

    def draw_detections(self, frame: np.ndarray, detections: List) -> np.ndarray:
        """Draw bounding boxes and labels on frame from detections.
        
        Args:
            frame: Input frame (BGR format)
            detections: List of Detection objects
            
        Returns:
            Frame with bounding boxes and labels drawn
        """
        if not detections:
            return frame
        
        output_frame = frame.copy()
        
        # Drawing parameters
        box_color = (0, 255, 0)  # Green (BGR)
        box_thickness = 2
        text_color = (255, 255, 255)  # White
        text_thickness = 1
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        
        for detection in detections:
            x1, y1, x2, y2 = [int(v) for v in detection.bbox]
            
            # Draw bounding box
            cv2.rectangle(output_frame, (x1, y1), (x2, y2), box_color, box_thickness)
            
            # Draw label with confidence
            label = f"{detection.class_name} ({detection.confidence:.2f})"
            label_size, _ = cv2.getTextSize(label, font, font_scale, text_thickness)
            label_y = max(y1 - 5, label_size[1] + 5)
            
            # Draw label background
            cv2.rectangle(output_frame, 
                        (x1, label_y - label_size[1] - 5),
                        (x1 + label_size[0] + 5, label_y),
                        box_color, -1)
            
            # Draw label text
            cv2.putText(output_frame, label, (x1 + 2, label_y - 5),
                       font, font_scale, text_color, text_thickness)
        
        return output_frame

    def closeEvent(self, event):
        """Handle widget close event."""
        self.stop_video()
        super().closeEvent(event)