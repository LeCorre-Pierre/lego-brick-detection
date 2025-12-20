"""
Contour detection and shape analysis for Lego Brick Detection application.
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict
from ..utils.logger import get_logger

logger = get_logger("contour_analyzer")

class ContourAnalyzer:
    """Analyzes image contours to find potential Lego brick shapes."""

    def __init__(self):
        self.logger = logger
        # Configure detection parameters
        self.min_area = 300
        self.max_area = 100000
        self.approx_epsilon = 0.02  # For polygon approximation

    def find_brick_contours(self, frame: np.ndarray) -> List[np.ndarray]:
        """Find contours that could be Lego bricks."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)

            # Edge detection
            edges = cv2.Canny(blurred, 50, 150)

            # Morphological operations to clean up edges
            kernel = np.ones((3, 3), np.uint8)
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

            # Find contours
            contours, hierarchy = cv2.findContours(
                edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            if not contours:
                return []

            # Filter contours based on brick-like properties
            brick_contours = []
            for contour in contours:
                if self._is_brick_like(contour):
                    brick_contours.append(contour)

            self.logger.debug(f"Found {len(brick_contours)} potential brick contours")
            return brick_contours

        except Exception as e:
            self.logger.error(f"Error in contour detection: {e}")
            return []

    def _is_brick_like(self, contour: np.ndarray) -> bool:
        """Check if a contour has brick-like properties."""
        try:
            # Basic area check
            area = cv2.contourArea(contour)
            if area < self.min_area or area > self.max_area:
                return False

            # Perimeter check
            perimeter = cv2.arcLength(contour, True)
            if perimeter < 50:  # Too small perimeter
                return False

            # Approximate the contour to a polygon
            approx = cv2.approxPolyDP(contour, self.approx_epsilon * perimeter, True)
            num_vertices = len(approx)

            # Lego bricks typically have 4-8 vertices (rectangular with possible studs)
            if not (4 <= num_vertices <= 12):
                return False

            # Check aspect ratio
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h if h > 0 else 0

            # Bricks are usually rectangular (not too elongated)
            if not (0.3 <= aspect_ratio <= 5.0):
                return False

            # Check solidity (ratio of contour area to bounding box area)
            bounding_area = w * h
            solidity = area / bounding_area if bounding_area > 0 else 0

            # Bricks should fill their bounding box reasonably well
            if solidity < 0.5:
                return False

            # Check convexity
            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull)
            convexity = area / hull_area if hull_area > 0 else 0

            # Bricks are mostly convex
            if convexity < 0.8:
                return False

            return True

        except Exception as e:
            self.logger.debug(f"Error checking contour properties: {e}")
            return False

    def get_contour_properties(self, contour: np.ndarray) -> Dict:
        """Get detailed properties of a contour."""
        try:
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            x, y, w, h = cv2.boundingRect(contour)

            # Moments for center of mass
            moments = cv2.moments(contour)
            if moments["m00"] != 0:
                cx = int(moments["m10"] / moments["m00"])
                cy = int(moments["m01"] / moments["m00"])
            else:
                cx, cy = x + w//2, y + h//2

            # Approximate shape
            approx = cv2.approxPolyDP(contour, self.approx_epsilon * perimeter, True)

            return {
                'area': area,
                'perimeter': perimeter,
                'bbox': (x, y, w, h),
                'center': (cx, cy),
                'aspect_ratio': w/h if h > 0 else 0,
                'vertices': len(approx),
                'solidity': area / (w * h) if w * h > 0 else 0
            }

        except Exception as e:
            self.logger.error(f"Error getting contour properties: {e}")
            return {}

    def draw_contours(self, frame: np.ndarray, contours: List[np.ndarray]) -> np.ndarray:
        """Draw contours on a frame for debugging."""
        try:
            result = frame.copy()
            cv2.drawContours(result, contours, -1, (0, 255, 0), 2)

            # Draw bounding boxes
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(result, (x, y), (x + w, y + h), (255, 0, 0), 1)

            return result

        except Exception as e:
            self.logger.error(f"Error drawing contours: {e}")
            return frame