"""
Image cache for brick preview images.
Implements LRU caching with lazy loading and placeholder generation.
Extended with download status tracking for automatic image downloads.
"""

from pathlib import Path
from collections import OrderedDict
from typing import Tuple, Optional, Dict
from datetime import datetime
from enum import Enum
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import Qt
from PIL import Image
import hashlib


class ImageStatus(Enum):
    """Status of a preview image in the cache."""
    MISSING = "missing"
    DOWNLOADING = "downloading"
    CACHED = "cached"
    FAILED = "failed"


class ImageCacheEntry:
    """Represents a cached image with download status."""
    
    def __init__(self, part_number: str):
        self.part_number = part_number
        self.file_path: Optional[Path] = None
        self.status: ImageStatus = ImageStatus.MISSING
        self.last_updated: datetime = datetime.now()
        self.error_message: Optional[str] = None
    
    def mark_downloading(self):
        """Mark image as currently downloading."""
        self.status = ImageStatus.DOWNLOADING
        self.last_updated = datetime.now()
    
    def mark_complete(self, file_path: Path):
        """Mark download as complete."""
        self.status = ImageStatus.CACHED
        self.file_path = file_path
        self.last_updated = datetime.now()
        self.error_message = None
    
    def mark_failed(self, error: str):
        """Mark download as failed."""
        self.status = ImageStatus.FAILED
        self.error_message = error
        self.last_updated = datetime.now()
    
    def is_cached(self) -> bool:
        """Check if image is successfully cached."""
        return self.status == ImageStatus.CACHED and self.file_path and self.file_path.exists()


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
        self._entries: Dict[str, ImageCacheEntry] = {}  # Track download status
        
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
    
    def get_entry(self, part_number: str) -> ImageCacheEntry:
        """
        Get or create cache entry for tracking download status.
        
        Args:
            part_number: The brick part number
            
        Returns:
            ImageCacheEntry for the part
        """
        if part_number not in self._entries:
            self._entries[part_number] = ImageCacheEntry(part_number)
        return self._entries[part_number]
    
    def get_status(self, part_number: str) -> ImageStatus:
        """
        Get download status for a part.
        
        Args:
            part_number: The brick part number
            
        Returns:
            Current ImageStatus
        """
        entry = self.get_entry(part_number)
        
        # Auto-detect if file exists but status is not CACHED
        if entry.status == ImageStatus.MISSING:
            if self._load_image(part_number) is not None:
                image_path = self._find_image_path(part_number)
                if image_path:
                    entry.mark_complete(image_path)
        
        return entry.status
    
    def _find_image_path(self, part_number: str) -> Optional[Path]:
        """Find existing image file path."""
        for ext in ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']:
            image_path = self._image_dir / f"{part_number}{ext}"
            if image_path.exists():
                return image_path
        return None
    
    def get_failed_parts(self) -> list[str]:
        """
        Get list of part numbers with failed downloads.
        
        Returns:
            List of part numbers where status is FAILED
        """
        return [
            part_num for part_num, entry in self._entries.items()
            if entry.status == ImageStatus.FAILED
        ]
    
    def get_download_statistics(self) -> dict:
        """
        Get download statistics.
        
        Returns:
            Dictionary with download stats
        """
        stats = {
            'total_requested': len(self._entries),
            'total_cached': sum(1 for e in self._entries.values() if e.status == ImageStatus.CACHED),
            'total_failed': sum(1 for e in self._entries.values() if e.status == ImageStatus.FAILED),
            'total_downloading': sum(1 for e in self._entries.values() if e.status == ImageStatus.DOWNLOADING),
            'cache_size_bytes': self._calculate_cache_size_bytes()
        }
        return stats
    
    def _calculate_cache_size_bytes(self) -> int:
        """Calculate total disk space used by cached images."""
        total_size = 0
        for entry in self._entries.values():
            if entry.is_cached() and entry.file_path:
                try:
                    total_size += entry.file_path.stat().st_size
                except (OSError, FileNotFoundError):
                    pass
        return total_size
