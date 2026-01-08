"""
Integration test for ImageDownloader functionality.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from utils.image_downloader import ImageDownloader
from utils.image_cache import ImageStatus


def test_image_downloader_integration():
    """Test basic ImageDownloader functionality."""
    print("Testing ImageDownloader integration...")
    
    # Initialize downloader
    cache_dir = Path("data/preview_images")
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    downloader = ImageDownloader(cache_dir=cache_dir)
    
    # Request a download
    test_part = "3001"
    print(f"Requesting download for {test_part}...")
    status = downloader.request_image(test_part, priority=0)
    print(f"Initial status: {status}")
    
    # Wait for download to complete (with timeout)
    max_wait = 15  # seconds
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        status = downloader.get_status(test_part)
        print(f"Status: {status}")
        
        if status in (ImageStatus.CACHED, ImageStatus.FAILED):
            break
        
        time.sleep(1)
    
    # Check final status
    final_status = downloader.get_status(test_part)
    print(f"Final status: {final_status}")
    
    # Get image path
    image_path = downloader.get_image_path(test_part)
    print(f"Image path: {image_path}")
    
    if image_path and image_path.exists():
        print(f"✓ Image downloaded successfully: {image_path}")
    else:
        print("✗ Image download failed or file not found")
    
    # Shutdown
    downloader.shutdown()
    print("✓ Downloader shutdown complete")


if __name__ == "__main__":
    test_image_downloader_integration()
