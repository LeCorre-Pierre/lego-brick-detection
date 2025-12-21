"""
Color matching and brick identification for Lego Brick Detection application.
"""

import cv2
import numpy as np
from typing import List, Optional, Dict, NamedTuple, Tuple
from ..models.detection_params import DetectionParams
from ..models.lego_set import LegoSet
from ..models.brick import Brick
from ..utils.logger import get_logger

logger = get_logger("color_matcher")

class ColorMatch(NamedTuple):
    """Result of a color matching operation."""
    brick_id: str
    color_name: str
    confidence: float
    rgb_values: Tuple[int, int, int]

class ColorMatcher:
    """Matches detected colors to known Lego brick colors."""

    # Standard Lego brick colors (RGB values)
    LEGO_COLORS = {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'red': (255, 0, 0),
        'blue': (0, 0, 255),
        'green': (0, 255, 0),
        'yellow': (255, 255, 0),
        'orange': (255, 165, 0),
        'purple': (128, 0, 128),
        'pink': (255, 192, 203),
        'brown': (165, 42, 42),
        'gray': (128, 128, 128),
        'light_gray': (211, 211, 211),
        'dark_gray': (64, 64, 64),
        'lime': (50, 205, 50),
        'cyan': (0, 255, 255),
        'magenta': (255, 0, 255),
        'tan': (210, 180, 140),
        'dark_blue': (0, 0, 139),
        'bright_green': (0, 255, 127),
    }

    def __init__(self):
        self.logger = logger
        self.current_bricks = []  # List of bricks in current set
        self.color_cache = {}  # Cache for color distance calculations
    def set_params(self, params: DetectionParams):
        """Update color matching parameters."""
        self.color_threshold = params.color_threshold
        self.saturation_boost = params.color_saturation_boost
        self.logger.info("Color matcher parameters updated")

    def set_brick_colors(self, lego_set: LegoSet):
        """Set the brick colors for the current Lego set."""
        self.current_bricks = lego_set.bricks
        self.color_cache.clear()  # Clear cache when set changes
        self.logger.info(f"Set brick colors for {len(self.current_bricks)} bricks")

    def match_brick_color(self, roi: np.ndarray) -> Optional[ColorMatch]:
        """Match the color of a region of interest to known brick colors."""
        try:
            # Performance optimization: early exit for very small ROIs
            if roi.size < 100:  # Less than 10x10 pixels
                return None

            # Extract dominant color from ROI
            dominant_color = self._extract_dominant_color(roi)

            # Find best matching brick (limit to bricks that aren't fully found)
            best_match = None
            best_confidence = 0.0

            # Performance: only check bricks that still need to be found
            bricks_to_check = [b for b in self.current_bricks if not b.is_fully_found()]
            if not bricks_to_check:
                return None  # All bricks found

            for brick in bricks_to_check[:20]:  # Limit bricks to check for performance
                brick_color_name = self._get_brick_color_name(brick)
                if brick_color_name in self.LEGO_COLORS:
                    target_color = self.LEGO_COLORS[brick_color_name]
                    confidence = self._calculate_color_similarity(dominant_color, target_color)

                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = ColorMatch(
                            brick_id=brick.id,
                            color_name=brick_color_name,
                            confidence=confidence,
                            rgb_values=target_color
                        )

            # Only return matches above threshold
            threshold_confidence = self.color_threshold / 255.0  # Convert to 0-1 scale
            if best_match and best_match.confidence > threshold_confidence:
                return best_match
            else:
                return None

        except Exception as e:
            self.logger.error(f"Error matching brick color: {e}")
            return None

    def _extract_dominant_color(self, roi: np.ndarray) -> Tuple[int, int, int]:
        """Extract the dominant color from a region of interest."""
        try:
            # Performance optimization: use mean color for small ROIs
            if roi.size < 1000:  # Less than ~30x30 pixels
                avg_color = cv2.mean(roi)[:3]
                return (int(avg_color[0]), int(avg_color[1]), int(avg_color[2]))

            # Ensure roi is a proper 3D array
            if len(roi.shape) != 3 or roi.shape[2] != 3:
                self.logger.warning(f"ROI has unexpected shape: {roi.shape}, using mean color")
                avg_color = cv2.mean(roi)[:3]
                return (int(avg_color[0]), int(avg_color[1]), int(avg_color[2]))

            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

            # Verify HSV conversion worked
            if len(hsv.shape) != 3 or hsv.shape[2] != 3:
                self.logger.warning(f"HSV conversion failed, shape: {hsv.shape}, using mean color")
                avg_color = cv2.mean(roi)[:3]
                return (int(avg_color[0]), int(avg_color[1]), int(avg_color[2]))

            # Use k-means clustering for better color extraction (but limit clusters for performance)
            pixels = hsv.reshape(-1, 3).astype(np.float32)

            # Sample pixels for performance (every 4th pixel)
            if len(pixels) > 1000:
                pixels = pixels[::4]

            # Simple approach: use the most frequent hue
            hist = cv2.calcHist([hsv], [0], None, [12], [0, 180])  # 12 hue bins
            dominant_hue_bin = np.argmax(hist)

            # Get average saturation and value for this hue range
            try:
                mask = (hsv[:, :, 0] >= dominant_hue_bin * 15) & (hsv[:, :, 0] < (dominant_hue_bin + 1) * 15)
                hue_pixels = hsv[mask]  # This gives us (N, 3) array of pixels
                if len(hue_pixels) > 0:
                    avg_s = np.mean(hue_pixels[:, 1])  # Saturation is column 1
                    avg_v = np.mean(hue_pixels[:, 2])  # Value is column 2
                    dominant_hsv = [dominant_hue_bin * 15, avg_s, avg_v]
                else:
                    # Fallback to average
                    dominant_hsv = cv2.mean(hsv)[:3]
            except Exception as mask_error:
                self.logger.warning(f"Error in hue range calculation: {mask_error}, using average")
                dominant_hsv = cv2.mean(hsv)[:3]

            # Convert back to BGR
            bgr = cv2.cvtColor(np.uint8([[[dominant_hsv[0], dominant_hsv[1], dominant_hsv[2]]]]), cv2.COLOR_HSV2BGR)[0][0]

            return (int(bgr[0]), int(bgr[1]), int(bgr[2]))

        except Exception as e:
            self.logger.error(f"Error extracting dominant color: {e}")
            # Return average color as fallback
            avg_color = cv2.mean(roi)[:3]
            return (int(avg_color[0]), int(avg_color[1]), int(avg_color[2]))

    def _calculate_color_similarity(self, color1: Tuple[int, int, int],
                                  color2: Tuple[int, int, int]) -> float:
        """Calculate color similarity using Euclidean distance in RGB space."""
        # Use cache for repeated calculations
        cache_key = (color1, color2)
        if cache_key in self.color_cache:
            return self.color_cache[cache_key]

        # Calculate Euclidean distance
        distance = np.sqrt(
            (color1[0] - color2[0]) ** 2 +
            (color1[1] - color2[1]) ** 2 +
            (color1[2] - color2[2]) ** 2
        )

        # Normalize to 0-1 scale (255 * sqrt(3) is max distance)
        max_distance = 255 * np.sqrt(3)
        similarity = 1.0 - (distance / max_distance)

        self.color_cache[cache_key] = similarity
        return similarity

    def _get_brick_color_name(self, brick: Brick) -> str:
        """Get the color name for a brick (placeholder implementation)."""
        # In a real implementation, this would come from the brick data
        # For now, we'll use a simple mapping based on brick ID or name

        brick_name_lower = brick.name.lower()

        # Simple keyword matching
        if 'black' in brick_name_lower:
            return 'black'
        elif 'white' in brick_name_lower:
            return 'white'
        elif 'red' in brick_name_lower:
            return 'red'
        elif 'blue' in brick_name_lower:
            return 'blue'
        elif 'green' in brick_name_lower:
            return 'green'
        elif 'yellow' in brick_name_lower:
            return 'yellow'
        elif 'orange' in brick_name_lower:
            return 'orange'
        elif 'gray' in brick_name_lower or 'grey' in brick_name_lower:
            return 'gray'
        else:
            # Default to red for unknown colors
            return 'red'

    def get_available_colors(self) -> List[str]:
        """Get list of available Lego colors."""
        return list(self.LEGO_COLORS.keys())

    def visualize_color_match(self, frame: np.ndarray, match: ColorMatch,
                            bbox: Tuple[int, int, int, int]) -> np.ndarray:
        """Visualize a color match on a frame."""
        try:
            result = frame.copy()
            x, y, w, h = bbox

            # Draw color swatch
            swatch_size = 20
            swatch_x = x + w + 5
            swatch_y = y

            cv2.rectangle(result, (swatch_x, swatch_y),
                         (swatch_x + swatch_size, swatch_y + swatch_size),
                         match.rgb_values[::-1], -1)  # BGR to RGB

            cv2.rectangle(result, (swatch_x, swatch_y),
                         (swatch_x + swatch_size, swatch_y + swatch_size),
                         (255, 255, 255), 1)

            # Draw label
            label = f"{match.color_name} ({match.confidence:.2f})"
            cv2.putText(result, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                       0.5, (255, 255, 255), 1)

            return result

        except Exception as e:
            self.logger.error(f"Error visualizing color match: {e}")
            return frame