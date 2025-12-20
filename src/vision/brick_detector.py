"""
Core brick detection engine for Lego Brick Detection application.
"""

import cv2
import numpy as np
from typing import List, Optional, Dict
from ..models.detection_result import DetectionResult
from ..models.lego_set import LegoSet
from ..models.brick import Brick
from ..vision.contour_analyzer import ContourAnalyzer
from ..vision.color_matcher import ColorMatcher
from ..utils.logger import get_logger

logger = get_logger("brick_detector")

class BrickDetector:
    """Core engine for detecting Lego bricks in video frames."""

    def __init__(self):
        self.logger = logger
        self.contour_analyzer = ContourAnalyzer()
        self.color_matcher = ColorMatcher()
        self.current_set = None
        self.detection_history = []  # Keep track of recent detections

        self.logger.info("Brick detector initialized")

    def set_lego_set(self, lego_set: LegoSet):
        """Set the current Lego set for detection."""
        self.current_set = lego_set
        self.color_matcher.set_brick_colors(lego_set)
        self.logger.info(f"Set Lego set for detection: {lego_set.name}")

    def detect_bricks(self, frame: np.ndarray) -> List[DetectionResult]:
        """Detect bricks in the given frame."""
        if self.current_set is None:
            self.logger.warning("No Lego set configured for detection")
            return []

        try:
            # Step 1: Find potential brick contours
            contours = self.contour_analyzer.find_brick_contours(frame)

            if not contours:
                return []

            # Step 2: Analyze each contour, but skip bricks that are already fully found
            detections = []
            for contour in contours:
                detection = self._analyze_contour(frame, contour)
                if detection:
                    # Check if this brick type is already fully found
                    brick = next((b for b in self.current_set.bricks if b.part_number == detection.brick_id), None)
                    if brick and not brick.is_fully_found():
                        detections.append(detection)

            # Step 3: Filter and rank detections
            filtered_detections = self._filter_detections(detections)

            # Step 4: Update detection history
            self._update_history(filtered_detections)

            self.logger.debug(f"Detected {len(filtered_detections)} bricks in frame")
            return filtered_detections

        except Exception as e:
            self.logger.error(f"Error in brick detection: {e}")
            return []

    def _analyze_contour(self, frame: np.ndarray, contour) -> Optional[DetectionResult]:
        """Analyze a single contour to determine if it's a brick."""
        try:
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)

            # Skip if too small or too large
            area = cv2.contourArea(contour)
            if area < 500 or area > 50000:  # Configurable thresholds
                return None

            # Get aspect ratio (bricks are usually rectangular)
            aspect_ratio = float(w) / h if h > 0 else 0
            if not (0.5 <= aspect_ratio <= 3.0):  # Allow some variation
                return None

            # Extract region of interest
            roi = frame[y:y+h, x:x+w]
            if roi.size == 0:
                return None

            # Match color to known brick colors
            color_match = self.color_matcher.match_brick_color(roi)
            if not color_match or color_match.confidence < 0.3:  # Minimum confidence
                return None

            # Calculate center point
            center_x = x + w // 2
            center_y = y + h // 2

            # Create detection result
            detection = DetectionResult(
                brick_id=color_match.brick_id,
                bbox=(x, y, w, h),
                confidence=color_match.confidence,
                center_point=(center_x, center_y),
                color=color_match.color_name
            )

            return detection

        except Exception as e:
            self.logger.debug(f"Error analyzing contour: {e}")
            return None

    def _filter_detections(self, detections: List[DetectionResult]) -> List[DetectionResult]:
        """Filter and rank detections to avoid duplicates and low-confidence results."""
        if not detections:
            return []

        # Sort by confidence (highest first)
        detections.sort(key=lambda d: d.confidence, reverse=True)

        # Filter out overlapping detections (Non-Maximum Suppression)
        filtered = []
        for detection in detections:
            # Check if this detection overlaps significantly with existing ones
            overlap = False
            for existing in filtered:
                if self._bboxes_overlap(detection.bbox, existing.bbox, threshold=0.3):
                    overlap = True
                    break

            if not overlap:
                filtered.append(detection)

        return filtered[:10]  # Limit to top 10 detections per frame

    def _bboxes_overlap(self, bbox1, bbox2, threshold: float = 0.3) -> bool:
        """Check if two bounding boxes overlap significantly."""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2

        # Calculate intersection
        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)

        if x_right < x_left or y_bottom < y_top:
            return False  # No intersection

        intersection_area = (x_right - x_left) * (y_bottom - y_top)

        # Calculate union
        area1 = w1 * h1
        area2 = w2 * h2
        union_area = area1 + area2 - intersection_area

        # Calculate IoU (Intersection over Union)
        iou = intersection_area / union_area if union_area > 0 else 0

        return iou > threshold

    def _update_history(self, detections: List[DetectionResult]):
        """Update detection history for temporal filtering."""
        # Keep only recent detections (last 10 frames)
        self.detection_history.append(detections)
        if len(self.detection_history) > 10:
            self.detection_history.pop(0)

    def get_stable_detections(self) -> List[DetectionResult]:
        """Get detections that are stable across multiple frames."""
        if len(self.detection_history) < 3:
            return []

        # Count how many times each brick appears in recent frames
        brick_counts = {}
        for frame_detections in self.detection_history[-3:]:  # Last 3 frames
            for detection in frame_detections:
                key = detection.brick_id
                if key not in brick_counts:
                    brick_counts[key] = []
                brick_counts[key].append(detection)

        # Return bricks that appear in at least 2 of the last 3 frames
        stable_detections = []
        for brick_id, detections in brick_counts.items():
            if len(detections) >= 2:
                # Use the most recent detection
                stable_detections.append(detections[-1])

        return stable_detections