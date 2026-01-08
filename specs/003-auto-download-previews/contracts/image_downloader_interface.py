"""
API Contract: ImageDownloader

Defines the public interface for the image download manager.
This contract establishes the behavior and guarantees for automatic
preview image downloading in the Lego brick detection application.
"""

from enum import Enum
from typing import Protocol, Optional, Callable
from pathlib import Path


class ImageStatus(Enum):
    """Status of a preview image in the cache."""
    MISSING = "missing"           # Not yet downloaded or queued
    DOWNLOADING = "downloading"    # Download in progress
    CACHED = "cached"             # Successfully downloaded and stored
    FAILED = "failed"             # Download failed permanently


class DownloadCallback(Protocol):
    """Callback protocol for download events."""
    
    def on_download_started(self, part_number: str) -> None:
        """Called when download begins for a part."""
        ...
    
    def on_download_complete(self, part_number: str, file_path: Path) -> None:
        """Called when download succeeds."""
        ...
    
    def on_download_failed(self, part_number: str, error: str) -> None:
        """Called when download fails permanently."""
        ...


class ImageDownloaderInterface(Protocol):
    """
    Public interface for automatic preview image downloading.
    
    Responsibilities:
    - Detect missing preview images
    - Download images from remote source (BrickLink)
    - Store images in local cache (data/preview_images/)
    - Prioritize downloads based on viewport visibility
    - Rate-limit requests (1 second between downloads)
    - Handle failures gracefully with placeholders
    - Notify UI of status changes via callbacks
    
    Thread Safety:
    - All public methods are thread-safe
    - Callbacks invoked on main/UI thread only
    
    Performance Guarantees:
    - Non-blocking: UI remains responsive during downloads
    - Viewport-priority: Visible images download first
    - Rate-limited: Max 1 request per second to remote server
    - No retries: Failed downloads not attempted again
    """
    
    def request_image(
        self,
        part_number: str,
        priority: int = 0,
        callback: Optional[DownloadCallback] = None
    ) -> ImageStatus:
        """
        Request a preview image for the given part number.
        
        Args:
            part_number: Unique identifier for the Lego brick (e.g., "3001")
            priority: Download priority (0=highest/viewport, higher=lower priority)
            callback: Optional callback for status updates
        
        Returns:
            Current status of the image:
            - CACHED: Image already available locally
            - DOWNLOADING: Download in progress or queued
            - MISSING: Download request queued
            - FAILED: Previous download attempt failed
        
        Behavior:
            - If image cached: returns CACHED immediately
            - If already downloading/queued: returns DOWNLOADING (no duplicate request)
            - If previously failed: returns FAILED (no retry)
            - Otherwise: queues download and returns MISSING
        
        Thread Safety:
            - Safe to call from any thread
            - Callback will be invoked on main/UI thread
        
        Example:
            >>> downloader.request_image("3001", priority=0)
            ImageStatus.MISSING  # Download queued
            >>> downloader.request_image("3001", priority=5)
            ImageStatus.DOWNLOADING  # Already in queue, not duplicated
        """
        ...
    
    def get_image_path(self, part_number: str) -> Optional[Path]:
        """
        Get the file path for a preview image.
        
        Args:
            part_number: Unique identifier for the Lego brick
        
        Returns:
            Path to image file if cached, None otherwise
        
        Behavior:
            - Returns actual image path if status == CACHED
            - Returns placeholder path if status == FAILED
            - Returns None if status in (MISSING, DOWNLOADING)
        
        Thread Safety:
            - Safe to call from any thread
        
        Example:
            >>> path = downloader.get_image_path("3001")
            >>> if path:
            ...     image = QPixmap(str(path))
        """
        ...
    
    def get_status(self, part_number: str) -> ImageStatus:
        """
        Get current status of a preview image.
        
        Args:
            part_number: Unique identifier for the Lego brick
        
        Returns:
            Current ImageStatus for the part
        
        Thread Safety:
            - Safe to call from any thread
        
        Example:
            >>> status = downloader.get_status("3001")
            >>> if status == ImageStatus.CACHED:
            ...     display_image()
            >>> elif status == ImageStatus.DOWNLOADING:
            ...     show_spinner()
        """
        ...
    
    def is_cached(self, part_number: str) -> bool:
        """
        Check if preview image is available in local cache.
        
        Args:
            part_number: Unique identifier for the Lego brick
        
        Returns:
            True if image file exists and is readable, False otherwise
        
        Thread Safety:
            - Safe to call from any thread
        
        Example:
            >>> if downloader.is_cached("3001"):
            ...     # Image ready to display
            ...     load_from_cache()
            >>> else:
            ...     # Need to download
            ...     downloader.request_image("3001")
        """
        ...
    
    def clear_cache(self) -> int:
        """
        Delete all cached preview images from disk.
        
        Returns:
            Number of files deleted
        
        Behavior:
            - Deletes all files in data/preview_images/
            - Resets all ImageCacheEntry statuses to MISSING
            - Clears download queue
        
        Thread Safety:
            - Safe to call from any thread
            - Blocks until operation complete
        
        Warning:
            This operation cannot be undone. Use with caution.
        
        Example:
            >>> deleted = downloader.clear_cache()
            >>> print(f"Cleared {deleted} cached images")
        """
        ...
    
    def shutdown(self) -> None:
        """
        Gracefully shut down the download manager.
        
        Behavior:
            - Stops background download thread
            - Completes current download (if any)
            - Clears download queue
            - Saves cache state
        
        Thread Safety:
            - Safe to call from any thread
            - Blocks until shutdown complete (max 5 seconds)
        
        Usage:
            Call before application exit to ensure clean shutdown.
        
        Example:
            >>> app.aboutToQuit.connect(downloader.shutdown)
        """
        ...


# Functional Requirements Mapping
# --------------------------------
# FR-001: Detect missing images → is_cached(), get_status()
# FR-002: Download without intervention → request_image() auto-queues
# FR-003: Store in data/preview_images/ → get_image_path() returns correct directory
# FR-004: Name files by part number → get_image_path() uses part_number
# FR-005: Handle failures gracefully → ImageStatus.FAILED, placeholder generation
# FR-006: Cache locally → is_cached(), get_image_path()
# FR-007: Auto-create directory → Implementation detail
# FR-008: Support PNG format → Implementation detail
# FR-009: Prioritize shape over color → Color fallback logic (3 → 0-9)
# FR-010: Non-blocking UI → Async downloads, callbacks on main thread


class ImageCacheInterface(Protocol):
    """
    Public interface for querying and managing the image cache.
    
    Provides read-only access to cache status and statistics.
    Write operations handled internally by ImageDownloader.
    """
    
    def get_cache_size(self) -> int:
        """
        Get total number of cached images.
        
        Returns:
            Count of successfully cached images (status == CACHED)
        
        Example:
            >>> cache.get_cache_size()
            42  # 42 images cached
        """
        ...
    
    def get_cache_size_bytes(self) -> int:
        """
        Get total disk space used by cached images.
        
        Returns:
            Total bytes consumed by all cached image files
        
        Example:
            >>> size_mb = cache.get_cache_size_bytes() / (1024 * 1024)
            >>> print(f"Cache: {size_mb:.1f} MB")
        """
        ...
    
    def get_failed_parts(self) -> list[str]:
        """
        Get list of part numbers with failed downloads.
        
        Returns:
            List of part numbers where download failed
        
        Use Case:
            Display failed parts to user for troubleshooting
        
        Example:
            >>> failed = cache.get_failed_parts()
            >>> if failed:
            ...     print(f"Failed to download: {', '.join(failed)}")
        """
        ...
    
    def get_download_statistics(self) -> dict:
        """
        Get download statistics for monitoring.
        
        Returns:
            Dictionary with keys:
            - total_requested: int
            - total_cached: int
            - total_failed: int
            - total_downloading: int
            - cache_size_bytes: int
        
        Example:
            >>> stats = cache.get_download_statistics()
            >>> print(f"{stats['total_cached']}/{stats['total_requested']} cached")
        """
        ...


# Usage Examples
# --------------

def example_basic_usage():
    """Basic usage pattern for ImageDownloader."""
    from some_implementation import ImageDownloader, ImageCache
    
    # Initialize downloader
    downloader = ImageDownloader()
    
    # Request image with viewport priority
    status = downloader.request_image("3001", priority=0)
    
    if status == ImageStatus.CACHED:
        # Image already available
        path = downloader.get_image_path("3001")
        display_image(path)
    
    elif status == ImageStatus.DOWNLOADING:
        # Show loading indicator
        show_loading_spinner()
    
    elif status == ImageStatus.FAILED:
        # Show placeholder
        path = downloader.get_image_path("3001")  # Returns placeholder
        display_placeholder(path)


def example_with_callback():
    """Usage with callback for asynchronous updates."""
    
    class MyCallback:
        def on_download_started(self, part_number: str) -> None:
            print(f"Downloading {part_number}...")
        
        def on_download_complete(self, part_number: str, file_path: Path) -> None:
            print(f"✓ Downloaded {part_number} to {file_path}")
            # Update UI with new image
            self.update_brick_list_item(part_number, file_path)
        
        def on_download_failed(self, part_number: str, error: str) -> None:
            print(f"✗ Failed to download {part_number}: {error}")
            # Show placeholder in UI
            self.show_placeholder(part_number)
    
    downloader = ImageDownloader()
    callback = MyCallback()
    downloader.request_image("3001", priority=0, callback=callback)


def example_batch_request():
    """Request multiple images with prioritization."""
    downloader = ImageDownloader()
    
    # Viewport parts (high priority)
    viewport_parts = ["3001", "3003", "3004"]
    for i, part in enumerate(viewport_parts):
        downloader.request_image(part, priority=0 + i)
    
    # Off-screen parts (lower priority)
    other_parts = ["3005", "3006", "3007"]
    for i, part in enumerate(other_parts):
        downloader.request_image(part, priority=100 + i)


def example_cache_management():
    """Query and manage cache."""
    cache = ImageCache()
    
    # Get statistics
    stats = cache.get_download_statistics()
    print(f"Cache: {stats['total_cached']} images, "
          f"{stats['cache_size_bytes'] / 1024 / 1024:.1f} MB")
    
    # Check failed downloads
    failed = cache.get_failed_parts()
    if failed:
        print(f"Warning: {len(failed)} parts failed to download")
        for part in failed:
            print(f"  - {part}")
