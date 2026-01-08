# Quickstart Guide: Automatic Preview Image Downloads

**Feature**: 003-auto-download-previews  
**Audience**: Developers implementing this feature  
**Prerequisites**: Python 3.11+, PyQt6, existing lego-brick-detection codebase

---

## Overview

This feature adds automatic preview image downloading to the brick list UI. When users load a Lego set, missing preview images download automatically in the background from BrickLink, prioritizing visible bricks in the viewport.

**Key behaviors**:
- Non-blocking: UI remains responsive during downloads
- Prioritized: Viewport images download first
- Rate-limited: 1-second delay between requests
- Cached: Downloaded images reused on subsequent loads
- Graceful: Placeholders shown on failure

---

## Installation

### 1. Install Dependencies

Add `requests` library for HTTP downloads:

```bash
pip install requests
```

Update `requirements.txt`:
```
opencv-python
numpy
matplotlib
scikit-learn
pillow
jupyter
PyQt6
ultralytics
requests  # NEW
```

---

## Implementation Steps

### Step 1: Create ImageDownloader Module

**File**: `src/utils/image_downloader.py`

Implement the core download manager with:
- Priority queue for download requests
- Background worker thread
- Qt signals for UI updates
- Rate limiting (1s delay)
- Color fallback logic (3 → 0-9)

**Key classes**:
- `ImageDownloader` - Main public interface
- `ImageDownloadWorker` - Background thread
- `DownloadSignals` - Qt signal emitter
- `DownloadRequest` - Request data structure

**Reference**: See [contracts/image_downloader_interface.py](contracts/image_downloader_interface.py) for API contract.

---

### Step 2: Extend ImageCache

**File**: `src/utils/image_cache.py` (existing)

Add download status tracking:

```python
class ImageCacheEntry:
    def __init__(self, part_number: str):
        self.part_number = part_number
        self.file_path: Optional[Path] = None
        self.status: ImageStatus = ImageStatus.MISSING  # NEW
        self.last_updated: datetime = datetime.now()    # NEW
        self.error_message: Optional[str] = None        # NEW
    
    def mark_downloading(self):
        self.status = ImageStatus.DOWNLOADING
        self.last_updated = datetime.now()
    
    def mark_complete(self, file_path: Path):
        self.status = ImageStatus.CACHED
        self.file_path = file_path
        self.last_updated = datetime.now()
    
    def mark_failed(self, error: str):
        self.status = ImageStatus.FAILED
        self.error_message = error
        self.last_updated = datetime.now()
```

---

### Step 3: Update BrickListWidget

**File**: `src/gui/brick_list_widget.py` (existing)

Integrate ImageDownloader:

```python
class BrickListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.downloader = ImageDownloader()  # NEW
        self.downloader.signals.download_complete.connect(
            self._on_image_downloaded
        )
        self.downloader.signals.download_failed.connect(
            self._on_download_failed
        )
    
    def load_set(self, lego_set: LegoSet):
        """Load bricks and request preview images."""
        for i, brick in enumerate(lego_set.bricks):
            item = BrickListItem(brick)
            self.add_item(item)
            
            # Check if image cached
            if not self.downloader.is_cached(brick.part_number):
                # Request download with priority
                priority = 0 if self._is_in_viewport(item) else i
                self.downloader.request_image(brick.part_number, priority)
    
    def _on_image_downloaded(self, part_number: str, file_path: str):
        """Update UI when image download completes."""
        item = self.find_item_by_part(part_number)
        if item:
            item.set_image(file_path)
    
    def _on_download_failed(self, part_number: str, error: str):
        """Show placeholder when download fails."""
        item = self.find_item_by_part(part_number)
        if item:
            item.show_placeholder(part_number)
```

---

### Step 4: Update BrickListItem

**File**: `src/gui/brick_list_item.py` (existing)

Add visual states for loading/placeholder:

```python
class BrickListItem(QWidget):
    def __init__(self, brick: Brick):
        super().__init__()
        self.brick = brick
        self.image_label = QLabel()
        self.loading_spinner = QMovie("assets/loading.gif")  # NEW
        self.setup_ui()
    
    def set_loading(self):
        """Show loading spinner."""
        self.image_label.setMovie(self.loading_spinner)
        self.loading_spinner.start()
    
    def set_image(self, file_path: str):
        """Display downloaded image."""
        pixmap = QPixmap(file_path)
        self.image_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))
        if self.loading_spinner.state() == QMovie.Running:
            self.loading_spinner.stop()
    
    def show_placeholder(self, part_number: str):
        """Show placeholder for failed downloads."""
        placeholder = self._generate_placeholder(part_number)
        self.image_label.setPixmap(placeholder)
        if self.loading_spinner.state() == QMovie.Running:
            self.loading_spinner.stop()
    
    def _generate_placeholder(self, part_number: str) -> QPixmap:
        """Generate gray placeholder with part number."""
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGB', (200, 200), color='lightgray')
        draw = ImageDraw.Draw(img)
        draw.text((100, 100), part_number, fill='black', anchor='mm')
        # Convert PIL to QPixmap
        return self._pil_to_qpixmap(img)
```

---

### Step 5: Implement Download Logic

**Key implementation details**:

#### URL Construction
```python
def construct_url(part_number: str, color_code: int) -> str:
    """Construct BrickLink image URL."""
    return f"https://img.bricklink.com/ItemImage/PN/{color_code}/{part_number}.png"
```

#### Color Fallback
```python
def download_with_fallback(part_number: str) -> Optional[bytes]:
    """Try color codes 3, then 0-9 until success."""
    for color_code in [3, 0, 1, 2, 4, 5, 6, 7, 8, 9]:
        url = construct_url(part_number, color_code)
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.content
        elif response.status_code == 404:
            continue  # Try next color
        else:
            return None  # Network error, stop trying
    return None  # All colors exhausted
```

#### Rate Limiting
```python
def enforce_rate_limit(self):
    """Ensure 1-second delay between downloads."""
    elapsed = time.time() - self._last_download_time
    if elapsed < 1.0:
        time.sleep(1.0 - elapsed)
    self._last_download_time = time.time()
```

---

## Testing

### Unit Tests

**File**: `tests/unit/test_image_downloader.py`

```python
import pytest
from unittest.mock import patch, Mock
from src.utils.image_downloader import ImageDownloader, ImageStatus

def test_request_image_queues_download():
    downloader = ImageDownloader()
    status = downloader.request_image("3001", priority=0)
    assert status in (ImageStatus.MISSING, ImageStatus.DOWNLOADING)

def test_cached_image_not_re_downloaded():
    downloader = ImageDownloader()
    # Pre-populate cache
    downloader._cache["3001"].status = ImageStatus.CACHED
    status = downloader.request_image("3001")
    assert status == ImageStatus.CACHED

@patch('requests.get')
def test_color_fallback_logic(mock_get):
    """Test that color 3 is tried first, then 0-9."""
    mock_get.side_effect = [
        Mock(status_code=404),  # Color 3 fails
        Mock(status_code=404),  # Color 0 fails
        Mock(status_code=200, content=b'image_data')  # Color 1 succeeds
    ]
    downloader = ImageDownloader()
    result = downloader._download_with_fallback("3001")
    assert result == b'image_data'
    assert mock_get.call_count == 3

def test_rate_limiting():
    """Verify 1-second delay between downloads."""
    downloader = ImageDownloader()
    start = time.time()
    downloader._download_image("3001")
    downloader._download_image("3002")
    elapsed = time.time() - start
    assert elapsed >= 1.0  # At least 1 second delay
```

### Integration Tests

**File**: `tests/integration/test_preview_download_integration.py`

```python
def test_end_to_end_download_flow():
    """Test complete download workflow."""
    # Clear cache
    cache_dir = Path("data/preview_images")
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    
    # Initialize downloader
    downloader = ImageDownloader()
    
    # Request image
    status = downloader.request_image("3001", priority=0)
    assert status == ImageStatus.MISSING
    
    # Wait for download
    time.sleep(5)
    
    # Verify cached
    assert downloader.is_cached("3001")
    path = downloader.get_image_path("3001")
    assert path.exists()
    assert path.suffix == ".png"
```

### Manual Testing

1. **Test viewport prioritization**:
   - Clear cache: `rm -rf data/preview_images`
   - Load large set (100+ bricks)
   - Verify top visible bricks load first

2. **Test failure handling**:
   - Disconnect network
   - Load set
   - Verify placeholders appear

3. **Test cache persistence**:
   - Download images
   - Restart application
   - Verify no re-downloads occur

---

## Configuration

### Directory Structure

Ensure `data/preview_images/` directory is created automatically:

```python
CACHE_DIR = Path("data/preview_images")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
```

### Rate Limiting

Adjust delay between requests (default 1 second):

```python
RATE_LIMIT_DELAY = 1.0  # seconds
```

### Timeout

Configure HTTP request timeout (default 10 seconds):

```python
REQUEST_TIMEOUT = 10  # seconds
```

---

## Troubleshooting

### Issue: Images not downloading

**Symptoms**: Status stays MISSING, no downloads occur

**Solutions**:
1. Check network connectivity
2. Verify BrickLink URLs are accessible
3. Check logs for error messages
4. Ensure worker thread is running

### Issue: UI freezing during downloads

**Symptoms**: Application becomes unresponsive

**Solutions**:
1. Verify downloads occur in background thread
2. Check Qt signals are connected correctly
3. Ensure no blocking operations on main thread

### Issue: All downloads failing

**Symptoms**: All images show placeholders

**Solutions**:
1. Verify URL construction logic
2. Check BrickLink service status
3. Review error logs for HTTP status codes
4. Test with known valid part numbers (e.g., "3001")

### Issue: Excessive memory usage

**Symptoms**: Application consumes too much RAM

**Solutions**:
1. Limit queue size (max 100 pending requests)
2. Implement image resolution downscaling
3. Use weak references for cached entries

---

## Performance Tips

1. **Preload common bricks**: Download frequently used parts on startup
2. **Batch prioritization**: Group viewport items for efficient queueing
3. **Lazy loading**: Only request images for visible items
4. **Image compression**: Store compressed PNGs to reduce disk usage

---

## Security Considerations

1. **URL validation**: Sanitize part numbers to prevent injection attacks
2. **File path safety**: Prevent path traversal with filename sanitization
3. **HTTPS only**: Use secure connections for downloads
4. **Size limits**: Enforce maximum file size (e.g., 5MB per image)

---

## Next Steps

After implementing this feature:

1. **Monitoring**: Add telemetry for download success rates
2. **Caching policy**: Implement LRU eviction for large caches
3. **Retry mechanism**: Optional user-triggered retry for failed downloads
4. **Multiple sources**: Fallback to Rebrickable if BrickLink unavailable
5. **Batch download**: "Download all" button for eager loading

---

## References

- [Feature Spec](spec.md)
- [Data Model](data-model.md)
- [Research](research.md)
- [API Contract](contracts/image_downloader_interface.py)
- [BrickLink Image API](https://www.bricklink.com/help.asp?helpID=207)

---

## Support

For questions or issues:
1. Review [research.md](research.md) for technical decisions
2. Check [data-model.md](data-model.md) for architecture details
3. Consult [contracts/](contracts/) for API specifications
4. Open issue on project repository with logs and reproduction steps
