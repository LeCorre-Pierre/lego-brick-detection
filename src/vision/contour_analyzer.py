"""
Contour detection and shape analysis for Lego Brick Detection application.
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict
from ..models.detection_params import DetectionParams
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
        self.edge_threshold = 50

    def set_params(self, params: DetectionParams):
        """Update contour analysis parameters."""
        self.min_area = params.min_brick_size * params.min_brick_size
        self.max_area = params.max_brick_size * params.max_brick_size
        self.edge_threshold = params.edge_detection_threshold
        self.logger.info("Contour analyzer parameters updated")

    def find_brick_contours(self, frame: np.ndarray) -> List[np.ndarray]:
        """Find contours that could be Lego bricks."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Apply Gaussian blur to reduce noise (smaller kernel for performance)
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)

            # Edge detection with optimized thresholds
            edges = cv2.Canny(blurred, self.edge_threshold, self.edge_threshold * 2)

            # Skip morphological operations if not needed for performance
            # Only apply if edges are noisy
            edge_density = np.count_nonzero(edges) / edges.size
            if edge_density > 0.1:  # If more than 10% edges, clean up
                kernel = np.ones((2, 2), np.uint8)  # Smaller kernel for performance
                edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

            # Find contours with optimized parameters
            contours, hierarchy = cv2.findContours(
                edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            if not contours:
                return []

            # Performance optimization: sort contours by area (largest first)
            # and limit processing to top candidates
            contours = sorted(contours, key=cv2.contourArea, reverse=True)[:100]

            # Filter contours based on brick-like properties
            brick_contours = []
            for contour in contours:
                if self._is_brick_like(contour):
                    brick_contours.append(contour)
                    if len(brick_contours) >= 50:  # Limit results for performance
                        break

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