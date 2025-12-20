"""
Detection result model for Lego Brick Detection application.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Tuple
from .brick import Brick

@dataclass
class DetectionResult:
    """Represents a detected brick instance in the video stream."""
    brick_id: str
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    confidence: float
    center_point: Tuple[int, int] = None
    color: str = ""
    timestamp: datetime = None

    def __post_init__(self):
        """Validate detection result after initialization."""
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("Confidence must be between 0.0 and 1.0")
        if len(self.bbox) != 4:
            raise ValueError("Bounding box must be a tuple of 4 integers")
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.center_point is None:
            x, y, w, h = self.bbox
            self.center_point = (x + w // 2, y + h // 2)

    def contains_point(self, point: Tuple[int, int]) -> bool:
        """Check if a point is inside the bounding box."""
        px, py = point
        x, y, w, h = self.bbox
        return x <= px <= x + w and y <= py <= y + h