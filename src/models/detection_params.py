"""
Detection parameters configuration for Lego Brick Detection.

This module defines the configurable parameters for computer vision detection
algorithms, allowing users to adjust settings for different lighting conditions
and viewing angles.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DetectionParams:
    """
    Configuration parameters for brick detection algorithms.

    These parameters control the sensitivity and behavior of the computer vision
    pipeline, allowing adaptation to different environments.
    """

    # Detection sensitivity
    min_confidence: float = 0.7  # Minimum confidence score (0.0-1.0)
    confidence_threshold: float = 0.6  # Threshold for accepting detections

    # Lighting adaptation
    lighting_mode: str = "auto"  # "bright", "dim", "auto"
    brightness_compensation: float = 1.0  # Brightness adjustment factor
    contrast_enhancement: float = 1.0  # Contrast enhancement factor

    # Color matching
    color_threshold: int = 30  # HSV color distance threshold (0-255)
    color_saturation_boost: float = 1.0  # Saturation adjustment for color matching

    # Shape analysis
    min_brick_size: int = 20  # Minimum pixel area for detection
    max_brick_size: int = 200  # Maximum pixel area for detection
    aspect_ratio_tolerance: float = 0.3  # Tolerance for brick aspect ratios

    # Angle and rotation
    angle_tolerance: int = 15  # Maximum rotation angle tolerance (degrees)
    perspective_correction: bool = True  # Enable perspective correction

    # Performance settings
    frame_skip: int = 0  # Skip frames for performance (0 = process all)
    roi_margin: int = 10  # Margin around detected regions (pixels)

    # Advanced settings
    morphological_operations: bool = True  # Enable morphological filtering
    edge_detection_threshold: int = 50  # Canny edge detection threshold

    def __post_init__(self):
        """Validate parameter ranges after initialization."""
        self._validate_parameters()

    def _validate_parameters(self):
        """Validate that all parameters are within acceptable ranges."""
        if not 0.0 <= self.min_confidence <= 1.0:
            raise ValueError(f"min_confidence must be between 0.0 and 1.0, got {self.min_confidence}")

        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError(f"confidence_threshold must be between 0.0 and 1.0, got {self.confidence_threshold}")

        if self.lighting_mode not in ["bright", "dim", "auto"]:
            raise ValueError(f"lighting_mode must be 'bright', 'dim', or 'auto', got '{self.lighting_mode}'")

        if not 0 <= self.color_threshold <= 255:
            raise ValueError(f"color_threshold must be between 0 and 255, got {self.color_threshold}")

        if self.min_brick_size < 1:
            raise ValueError(f"min_brick_size must be positive, got {self.min_brick_size}")

        if self.max_brick_size <= self.min_brick_size:
            raise ValueError(f"max_brick_size must be greater than min_brick_size, got {self.max_brick_size}")

        if not 0 <= self.angle_tolerance <= 90:
            raise ValueError(f"angle_tolerance must be between 0 and 90 degrees, got {self.angle_tolerance}")

    def get_bright_mode_params(self) -> 'DetectionParams':
        """Return optimized parameters for bright lighting conditions."""
        return DetectionParams(
            min_confidence=self.min_confidence,
            confidence_threshold=max(0.5, self.confidence_threshold - 0.1),
            lighting_mode="bright",
            brightness_compensation=0.8,
            contrast_enhancement=1.2,
            color_threshold=self.color_threshold,
            min_brick_size=self.min_brick_size,
            max_brick_size=self.max_brick_size,
            angle_tolerance=self.angle_tolerance
        )

    def get_dim_mode_params(self) -> 'DetectionParams':
        """Return optimized parameters for dim lighting conditions."""
        return DetectionParams(
            min_confidence=max(0.5, self.min_confidence - 0.1),
            confidence_threshold=max(0.4, self.confidence_threshold - 0.2),
            lighting_mode="dim",
            brightness_compensation=1.5,
            contrast_enhancement=0.8,
            color_threshold=min(50, self.color_threshold + 10),
            min_brick_size=self.min_brick_size,
            max_brick_size=self.max_brick_size,
            angle_tolerance=self.angle_tolerance
        )

    def to_dict(self) -> dict:
        """Convert parameters to dictionary for serialization."""
        return {
            'min_confidence': self.min_confidence,
            'confidence_threshold': self.confidence_threshold,
            'lighting_mode': self.lighting_mode,
            'brightness_compensation': self.brightness_compensation,
            'contrast_enhancement': self.contrast_enhancement,
            'color_threshold': self.color_threshold,
            'color_saturation_boost': self.color_saturation_boost,
            'min_brick_size': self.min_brick_size,
            'max_brick_size': self.max_brick_size,
            'aspect_ratio_tolerance': self.aspect_ratio_tolerance,
            'angle_tolerance': self.angle_tolerance,
            'perspective_correction': self.perspective_correction,
            'frame_skip': self.frame_skip,
            'roi_margin': self.roi_margin,
            'morphological_operations': self.morphological_operations,
            'edge_detection_threshold': self.edge_detection_threshold
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'DetectionParams':
        """Create parameters from dictionary (for deserialization)."""
        return cls(**data)