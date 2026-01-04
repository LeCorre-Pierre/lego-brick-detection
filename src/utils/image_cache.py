"""
Image cache for brick preview images.
Implements LRU caching with lazy loading and placeholder generation.
"""

from pathlib import Path
from collections import OrderedDict
from typing import Tuple, Optional
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import Qt
from PIL import Image
import hashlib


class ImageCache:
    """LRU cache for brick preview images with placeholder generation."""
    
    def __init__(
        self, 
        image_dir: Path, 
        max_size: int = 100, 
        image_size: Tuple[int, int] = (48, 48)
    ):
        """
        Initialize image cache.
        
        Args:
            image_dir: Directory containing brick preview images
            max_size: Maximum number of images to cache
            image_size: Target size for loaded images (width, height)
        """
        self._image_dir = Path(image_dir)
        self._max_size = max_size
        self._image_size = image_size
        self._cache: OrderedDict[str, QPixmap] = OrderedDict()
        self._placeholder_cache: OrderedDict[str, QPixmap] = OrderedDict()
        
    def get_image(self, part_number: str) -> QPixmap:
        """
        Get cached or load image for brick part number.
        
        Args:
            part_number: The brick part number
            
        Returns:
            QPixmap containing the brick image or a placeholder
        """
        # Check cache first
        if part_number in self._cache:
            # Move to end (most recently used)
            self._cache.move_to_end(part_number)
            return self._cache[part_number]
        
        # Try to load from disk
        pixmap = self._load_image(part_number)
        
        if pixmap is None or pixmap.isNull():
            # Generate placeholder
            pixmap = self._get_placeholder(part_number)
        
        # Add to cache
        self._cache[part_number] = pixmap
        
        # Enforce max size (LRU eviction)
        if len(self._cache) > self._max_size:
            # Remove oldest (first) item
            self._cache.popitem(last=False)
        
        return pixmap
    
    def _load_image(self, part_number: str) -> Optional[QPixmap]:
        """
        Load image from disk and scale to target size.
        
        Args:
            part_number: The brick part number
            
        Returns:
            QPixmap if successful, None otherwise
        """
        # Try common image extensions
        for ext in ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']:
            image_path = self._image_dir / f"{part_number}{ext}"
            if image_path.exists():
                pixmap = QPixmap(str(image_path))
                if not pixmap.isNull():
                    # Scale to target size while maintaining aspect ratio
                    return pixmap.scaled(
                        self._image_size[0],
                        self._image_size[1],
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
        
        return None
    
    def _get_placeholder(self, part_number: str) -> QPixmap:
        """
        Generate colored placeholder for missing images.
        
        Args:
            part_number: The brick part number
            
        Returns:
            QPixmap with colored background and part number text
        """
        # Check placeholder cache
        if part_number in self._placeholder_cache:
            return self._placeholder_cache[part_number]
        
        # Generate consistent color from part number hash
        hash_val = int(hashlib.md5(part_number.encode()).hexdigest()[:6], 16)
        hue = hash_val % 360
        
        # Create pixmap
        pixmap = QPixmap(self._image_size[0], self._image_size[1])
        
        # Fill with color
        color = QColor.fromHsv(hue, 100, 200)
        pixmap.fill(color)
        
        # Draw part number text
        painter = QPainter(pixmap)
        painter.setPen(QColor(0, 0, 0, 180))
        
        # Use smaller font for longer part numbers
        font_size = 8 if len(part_number) > 6 else 10
        font = QFont("Arial", font_size, QFont.Weight.Bold)
        painter.setFont(font)
        
        painter.drawText(
            pixmap.rect(),
            Qt.AlignmentFlag.AlignCenter,
            part_number
        )
        painter.end()
        
        # Cache placeholder
        self._placeholder_cache[part_number] = pixmap
        
        return pixmap
    
    def preload_images(self, part_numbers: list[str]) -> None:
        """
        Preload images for the given part numbers (foreground operation).
        
        Args:
            part_numbers: List of part numbers to preload
        """
        for part_number in part_numbers:
            if part_number not in self._cache:
                self.get_image(part_number)
    
    def clear_cache(self) -> None:
        """Clear all cached images."""
        self._cache.clear()
        self._placeholder_cache.clear()
    
    def get_cache_size(self) -> int:
        """
        Get the number of images currently cached.
        
        Returns:
            Number of cached images
        """
        return len(self._cache)
