"""
Image Downloader Module

Handles automatic downloading of Lego brick preview images from BrickLink.
Downloads occur in background thread with priority queue and rate limiting.
"""

import os
import time
import logging
import threading
from pathlib import Path
from queue import PriorityQueue, Empty
from dataclasses import dataclass, field
from typing import Optional, Callable
from enum import Enum

import requests
from PIL import Image, ImageDraw, ImageFont
from PyQt6.QtCore import QObject, pyqtSignal

from .image_cache import ImageStatus, ImageCache, ImageCacheEntry


logger = logging.getLogger(__name__)


# Configuration constants
RATE_LIMIT_DELAY = 1.0  # seconds between downloads
REQUEST_TIMEOUT = 10  # seconds for HTTP requests
CACHE_DIR = Path("data/preview_images")
BASE_URL = "https://img.bricklink.com/ItemImage/PN"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


@dataclass(order=True)
class DownloadRequest:
    """Represents a download request with prioritization."""
    priority: int
    part_number: str = field(compare=False)
    color_code: int = field(default=3, compare=False)
    timestamp: float = field(default_factory=time.time, compare=False)
    retry_count: int = field(default=0, compare=False)


class DownloadSignals(QObject):
    """Qt signals for thread-safe UI updates."""
    download_started = pyqtSignal(str)  # part_number
    download_complete = pyqtSignal(str, str)  # part_number, file_path
    download_failed = pyqtSignal(str, str)  # part_number, error


class DownloadQueue:
    """Thread-safe priority queue for download requests."""
    
    def __init__(self):
        self._queue = PriorityQueue()
        self._in_progress = set()
        self._lock = threading.Lock()
    
    def enqueue(self, request: DownloadRequest) -> bool:
        """Add request to queue if not already queued/in progress."""
        with self._lock:
            if request.part_number in self._in_progress:
                return False
            self._in_progress.add(request.part_number)
        
        self._queue.put(request)
        return True
    
    def dequeue(self, timeout: Optional[float] = None) -> Optional[DownloadRequest]:
        """Retrieve highest-priority request (blocks if empty)."""
        try:
            return self._queue.get(timeout=timeout)
        except Empty:
            return None
    
    def is_queued(self, part_number: str) -> bool:
        """Check if part is queued or in progress."""
        with self._lock:
            return part_number in self._in_progress
    
    def mark_complete(self, part_number: str):
        """Remove part from in-progress set."""
        with self._lock:
            self._in_progress.discard(part_number)
    
    def clear(self):
        """Empty the queue."""
        with self._lock:
            while not self._queue.empty():
                try:
                    self._queue.get_nowait()
                except Empty:
                    break
            self._in_progress.clear()


class ImageDownloadWorker(threading.Thread):
    """Background thread that processes download queue."""
    
    def __init__(self, queue: DownloadQueue, signals: DownloadSignals, cache: ImageCache):
        super().__init__(daemon=True)
        self.queue = queue
        self.signals = signals
        self.cache = cache
        self._stop_flag = threading.Event()
        self._last_download_time = 0.0
    
    def run(self):
        """Main loop: dequeue → download → emit signal → rate limit."""
        logger.info("ImageDownloadWorker started")
        
        while not self._stop_flag.is_set():
            request = self.queue.dequeue(timeout=1.0)
            
            if request is None:
                continue
            
            try:
                # T026: Log download started
                logger.info(f"Starting download for {request.part_number} (priority {request.priority})")
                self.signals.download_started.emit(request.part_number)
                file_path = self._download_image(request)
                
                if file_path:
                    # Mark as complete in cache
                    entry = self.cache.get_entry(request.part_number)
                    entry.mark_complete(file_path)
                    self.signals.download_complete.emit(request.part_number, str(file_path))
                    logger.info(f"Successfully downloaded {request.part_number} to {file_path}")
                else:
                    # Mark as failed
                    entry = self.cache.get_entry(request.part_number)
                    entry.mark_failed("Download failed for all color variants")
                    self.signals.download_failed.emit(request.part_number, "No image available")
                    logger.warning(f"Failed to download {request.part_number} - no image available")
                    
            except Exception as e:
                logger.error(f"Error processing {request.part_number}: {e}")
                entry = self.cache.get_entry(request.part_number)
                entry.mark_failed(str(e))
                self.signals.download_failed.emit(request.part_number, str(e))
            finally:
                self.queue.mark_complete(request.part_number)
                self._enforce_rate_limit()
        
        logger.info("ImageDownloadWorker stopped")
    
    def stop(self):
        """Signal worker to stop gracefully."""
        self._stop_flag.set()
    
    def _download_image(self, request: DownloadRequest) -> Optional[Path]:
        """
        Download image with color fallback logic.
        (T028, T029, T035)
        
        Args:
            request: Download request with part number
            
        Returns:
            Path to saved image file (real or placeholder), or None if save failed
        """
        try:
            content = self._download_with_color_fallback(request.part_number)
            
            if content:
                # Save to disk with sanitized filename (T035)
                safe_filename = self._sanitize_filename(request.part_number)
                file_path = CACHE_DIR / f"{safe_filename}.png"
                try:
                    with open(file_path, 'wb') as f:
                        f.write(content)
                    return file_path
                except IOError as e:
                    logger.error(f"Failed to save {request.part_number}: {e}")
                    return None
            else:
                # Download failed - generate placeholder (T029)
                return self._generate_placeholder(request.part_number)
                
        except (requests.exceptions.Timeout, 
                requests.exceptions.ConnectionError,
                requests.exceptions.RequestException) as e:
            # Network error - generate placeholder (T028, T029)
            logger.error(f"Network error for {request.part_number}: {e}")
            return self._generate_placeholder(request.part_number)
    
    def _download_with_color_fallback(self, part_number: str) -> Optional[bytes]:
        """
        Try downloading with color fallback (3, then 0-9).
        (T033: Enhanced error logging)
        
        Args:
            part_number: Brick part number
            
        Returns:
            Image bytes if successful, None otherwise
        """
        # Try color 3 first, then 0-9
        color_sequence = [3, 0, 1, 2, 4, 5, 6, 7, 8, 9]
        
        for color_code in color_sequence:
            url = self._construct_url(part_number, color_code)
            
            try:
                # Add User-Agent header to avoid 403 errors from BrickLink
                headers = {'User-Agent': USER_AGENT}
                response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
                
                if response.status_code == 200:
                    logger.debug(f"Downloaded {part_number} with color {color_code}")
                    return response.content
                elif response.status_code == 404:
                    # Try next color (T033: specific 404 logging)
                    logger.debug(f"404 Not Found for {part_number} color {color_code}, trying next color")
                    continue
                else:
                    # Other error - stop trying (T033: log HTTP status)
                    logger.warning(f"HTTP {response.status_code} for {part_number} color {color_code}")
                    break
                    
            except requests.exceptions.Timeout:
                # T033: Specific timeout error logging
                logger.warning(f"Timeout (>{REQUEST_TIMEOUT}s) downloading {part_number} color {color_code}")
                break
            except requests.exceptions.ConnectionError as e:
                # T033: Specific connection error logging
                logger.warning(f"Connection error downloading {part_number}: {str(e)[:100]}")
                break
            except Exception as e:
                # T033: Generic error fallback
                logger.error(f"Unexpected error downloading {part_number}: {e}")
                break
        
        return None
    
    def _generate_placeholder(self, part_number: str) -> Path:
        """
        Generate a placeholder image for failed downloads.
        (T027, T035)
        
        Args:
            part_number: Brick part number to display on placeholder
            
        Returns:
            Path to the generated placeholder image
        """
        # Create 48x48 gray placeholder with part number text
        img = Image.new('RGB', (48, 48), color=(200, 200, 200))
        draw = ImageDraw.Draw(img)
        
        # Try to use a default font, fallback to basic if not available
        try:
            # Use a small font size that fits in 48x48
            font = ImageFont.truetype("arial.ttf", 8)
        except:
            font = ImageFont.load_default()
        
        # Draw part number text (centered)
        text = f"#{part_number}"
        
        # Calculate text bounding box for centering
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (48 - text_width) // 2
        y = (48 - text_height) // 2
        
        draw.text((x, y), text, fill=(80, 80, 80), font=font)
        
        # Save placeholder with sanitized filename (T035)
        safe_filename = self._sanitize_filename(part_number)
        file_path = CACHE_DIR / f"{safe_filename}.png"
        img.save(file_path)
        logger.info(f"Generated placeholder for {part_number}")
        
        return file_path
    
    def _sanitize_filename(self, part_number: str) -> str:
        """
        Sanitize part number for use as filename.
        (T034)
        
        Args:
            part_number: Raw part number
            
        Returns:
            Sanitized filename-safe string
        """
        import re
        # Replace any character that's not alphanumeric, dash, or underscore with underscore
        sanitized = re.sub(r'[^a-zA-Z0-9\-_]', '_', part_number)
        return sanitized
    
    def _construct_url(self, part_number: str, color_code: int) -> str:
        """
        Construct BrickLink image URL.
        
        Args:
            part_number: Brick part number
            color_code: Color code (0-9)
            
        Returns:
            Full URL to image
        """
        return f"{BASE_URL}/{color_code}/{part_number}.png"
    
    def _enforce_rate_limit(self):
        """Ensure minimum delay between downloads."""
        elapsed = time.time() - self._last_download_time
        if elapsed < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - elapsed)
        self._last_download_time = time.time()


class ImageDownloader:
    """Main interface for automatic preview image downloading."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize ImageDownloader with cache integration."""
        self.cache_dir = cache_dir or CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.cache = ImageCache(self.cache_dir)
        self.signals = DownloadSignals()
        self.queue = DownloadQueue()
        self.worker = ImageDownloadWorker(self.queue, self.signals, self.cache)
        self.worker.start()
        logger.info("ImageDownloader initialized")
    
    def request_image(self, part_number: str, priority: int = 0) -> ImageStatus:
        """
        Request a preview image download.
        
        Args:
            part_number: Unique identifier for the brick
            priority: Download priority (0=highest)
        
        Returns:
            Current status of the image
        """
        # Check status first to auto-detect existing files
        status = self.cache.get_status(part_number)
        
        # Check if already cached
        if status == ImageStatus.CACHED:
            return ImageStatus.CACHED
        
        # Check if failed previously
        if status == ImageStatus.FAILED:
            return ImageStatus.FAILED
        
        entry = self.cache.get_entry(part_number)
        
        # Create download request
        request = DownloadRequest(priority=priority, part_number=part_number)
        
        if self.queue.enqueue(request):
            entry.mark_downloading()
            logger.info(f"Queued download for {part_number} with priority {priority}")
            return ImageStatus.DOWNLOADING
        else:
            logger.debug(f"{part_number} already queued/downloading")
            return ImageStatus.DOWNLOADING
    
    def get_image_path(self, part_number: str) -> Optional[Path]:
        """Get file path for a preview image."""
        entry = self.cache.get_entry(part_number)
        
        if entry.is_cached() and entry.file_path:
            return entry.file_path
        
        # Check if failed - return placeholder path
        if entry.status == ImageStatus.FAILED:
            placeholder_path = self.cache_dir / f"placeholder_{part_number}.png"
            if placeholder_path.exists():
                return placeholder_path
        
        return None
    
    def get_status(self, part_number: str) -> ImageStatus:
        """Get current status of a preview image."""
        return self.cache.get_status(part_number)
    
    def is_cached(self, part_number: str) -> bool:
        """Check if preview image is cached locally."""
        entry = self.cache.get_entry(part_number)
        return entry.is_cached()
    
    def clear_cache(self) -> int:
        """
        Delete all cached preview images.
        (T041)
        
        Returns:
            Number of files deleted
        """
        count = 0
        if self.cache_dir.exists():
            for file_path in self.cache_dir.glob("*.png"):
                try:
                    file_path.unlink()
                    count += 1
                except OSError as e:
                    logger.warning(f"Failed to delete {file_path}: {e}")
        
        # Clear cache entries
        self.cache.clear()
        logger.info(f"Cleared {count} cached preview images")
        return count
    
    def shutdown(self):
        """
        Gracefully shut down the download manager.
        (T042)
        """
        logger.info("Shutting down ImageDownloader")
        self.worker.stop()
        self.worker.join(timeout=5.0)
        self.queue.clear()
