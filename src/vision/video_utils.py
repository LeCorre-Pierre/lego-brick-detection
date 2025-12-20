"""
Video processing utilities for Lego Brick Detection application.
"""

import cv2
import numpy as np
from typing import Optional, Tuple
from ..utils.logger import get_logger

logger = get_logger("video_utils")

class VideoCaptureManager:
    """Manages video capture from various sources."""

    def __init__(self):
        self.capture = None
        self.is_opened = False
        self.logger = logger

    def open(self, device_id: int, width: int = 640, height: int = 480, fps: int = 30) -> bool:
        """Open video capture device."""
        try:
            self.capture = cv2.VideoCapture(device_id)
            if not self.capture.isOpened():
                self.logger.error(f"Failed to open video device {device_id}")
                return False

            # Set properties
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.capture.set(cv2.CAP_PROP_FPS, fps)

            self.is_opened = True
            self.logger.info(f"Opened video device {device_id} at {width}x{height}@{fps}fps")
            return True

        except Exception as e:
            self.logger.error(f"Error opening video device {device_id}: {e}")
            return False

    def read_frame(self) -> Optional[np.ndarray]:
        """Read a frame from the video stream."""
        if not self.is_opened or self.capture is None:
            return None

        try:
            ret, frame = self.capture.read()
            if ret:
                return frame
            else:
                self.logger.warning("Failed to read frame from video stream")
                return None
        except Exception as e:
            self.logger.error(f"Error reading frame: {e}")
            return None

    def close(self):
        """Close video capture device."""
        if self.capture is not None:
            self.capture.release()
            self.capture = None
        self.is_opened = False
        self.logger.info("Video capture closed")

    def isOpened(self) -> bool:
        """Check if video capture is opened."""
        return self.is_opened and self.capture is not None and self.capture.isOpened()

def convert_frame_to_qimage(frame: np.ndarray) -> 'QImage':
    """Convert OpenCV frame to PyQt QImage."""
    try:
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Get dimensions
        height, width, channel = rgb_frame.shape
        bytes_per_line = 3 * width

        # Import here to avoid circular imports
        from PyQt6.QtGui import QImage
        from PyQt6.QtCore import Qt

        # Create QImage
        qimage = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        return qimage

    except Exception as e:
        logger.error(f"Error converting frame to QImage: {e}")
        return None

def resize_frame(frame: np.ndarray, width: int, height: int) -> np.ndarray:
    """Resize frame to specified dimensions."""
    try:
        return cv2.resize(frame, (width, height))
    except Exception as e:
        logger.error(f"Error resizing frame: {e}")
        return frame

def draw_bounding_box(frame: np.ndarray, bbox: Tuple[int, int, int, int],
                     label: str = "", color: Tuple[int, int, int] = (0, 255, 0)) -> np.ndarray:
    """Draw bounding box on frame."""
    try:
        x, y, w, h = bbox
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

        if label:
            # Draw label background
            cv2.rectangle(frame, (x, y - 25), (x + len(label) * 12, y), color, -1)
            # Draw label text
            cv2.putText(frame, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        return frame
    except Exception as e:
        logger.error(f"Error drawing bounding box: {e}")
        return frame