"""
Video source model for Lego Brick Detection application.
"""

from dataclasses import dataclass
from typing import Dict, Any, Tuple
from enum import Enum

class VideoSourceType(Enum):
    """Types of video sources supported."""
    WEBCAM = "webcam"
    KINECT = "kinect"

@dataclass
class VideoSource:
    """Represents a camera or video input device configuration."""
    type: VideoSourceType
    device_id: int
    resolution: Tuple[int, int] = (640, 480)
    frame_rate: int = 30
    calibration_data: Dict[str, Any] = None

    def __post_init__(self):
        """Validate video source configuration after initialization."""
        if self.device_id < 0:
            raise ValueError("Device ID must be non-negative")
        if self.resolution[0] <= 0 or self.resolution[1] <= 0:
            raise ValueError("Resolution dimensions must be positive")
        if not (1 <= self.frame_rate <= 60):
            raise ValueError("Frame rate must be between 1 and 60 FPS")
        if self.calibration_data is None:
            self.calibration_data = {}

    def get_opencv_device_id(self) -> int:
        """Get the device ID for OpenCV VideoCapture."""
        return self.device_id

    def get_display_name(self) -> str:
        """Get a human-readable name for the video source."""
        if self.type == VideoSourceType.WEBCAM:
            return f"Webcam {self.device_id}"
        elif self.type == VideoSourceType.KINECT:
            return f"Kinect {self.device_id}"
        return f"Unknown {self.device_id}"