# Research: Automatic Preview Image Downloads

**Feature**: 003-auto-download-previews  
**Date**: January 7, 2026  
**Purpose**: Document technical decisions and research findings for implementation

## Research Questions Resolved

### 1. Image Source and URL Construction

**Decision**: Use BrickLink Image API  
**URL Pattern**: `https://img.bricklink.com/ItemImage/PN/<color_code>/<part_number>.png`

**Rationale**:
- BrickLink provides comprehensive coverage of Lego parts with public image URLs
- Predictable URL structure allows dynamic construction without API authentication
- PNG format ensures transparency support for brick previews
- Color code fallback strategy (3 → 0-9) handles missing color variants

**Alternatives considered**:
- Rebrickable API: Requires authentication and rate limiting
- LEGO official CDN: Limited public access, less comprehensive
- Local-only storage: Requires manual image collection

**Implementation details**:
- Start with color code 3 (yellow) as default since color accuracy is not critical
- Iterate through color codes 0-9 if color 3 fails (404 response)
- Stop iteration after first successful download
- No retry on final failure to prevent infinite loops

---

### 2. Background Download Architecture

**Decision**: Python threading with queue-based prioritization

**Rationale**:
- PyQt6 already used in project; native thread support integrates well
- `queue.PriorityQueue` provides built-in priority handling for viewport-first downloads
- `threading.Thread` with daemon mode ensures clean shutdown
- QTimer integration allows UI updates on main thread without blocking

**Alternatives considered**:
- asyncio with aiohttp: Adds complexity; threading sufficient for I/O-bound downloads
- multiprocessing: Overkill for I/O operations; higher overhead
- QThread: More Qt-native but threading.Thread simpler and equally effective

**Implementation details**:
- Single background worker thread processes download queue
- Main thread enqueues downloads with priorities (viewport=0, others=line_number)
- Downloaded images emit Qt signals to update UI on main thread
- 1-second delay enforced between requests using `time.sleep(1)`

---

### 3. Rate Limiting Strategy

**Decision**: Simple time-based delay (1 second between requests)

**Rationale**:
- Prevents overwhelming BrickLink servers (good citizenship)
- Simple implementation: `time.sleep(1)` after each download
- Acceptable user experience: most sets load within 10 seconds
- No complex token bucket or sliding window needed

**Alternatives considered**:
- Token bucket algorithm: Over-engineered for this use case
- Exponential backoff: Unnecessary since no retries on failure
- No rate limiting: Risks server blocking and poor citizenship

**Implementation details**:
- Delay occurs in background thread after each download attempt
- Delay applies regardless of success/failure
- No burst handling needed due to sequential queue processing

---

### 4. Priority Queue Implementation

**Decision**: Two-tier priority system based on viewport visibility

**Rationale**:
- Users see viewport images first, improving perceived performance
- Scrolled-out images download progressively without blocking visible content
- Simple priority scheme: viewport items get priority 0, others use list index

**Alternatives considered**:
- Distance-based priority: Complex calculation, minimal benefit
- LRU-based priority: Adds state management complexity
- FIFO queue: Poor UX as visible images may download last

**Implementation details**:
```python
priority = 0 if brick_in_viewport else brick_list_index
queue.put((priority, part_number, download_params))
```
- Lower priority number = higher priority
- Viewport detection uses QScrollArea visible region
- Re-prioritization on scroll would add complexity; not implemented initially

---

### 5. Failure Handling and Placeholders

**Decision**: Static placeholder image with part number overlay

**Rationale**:
- Clear visual indicator that image is unavailable
- Part number ensures brick identification without image
- No retry logic simplifies implementation and prevents server hammering
- User can manually refresh/reload if needed

**Alternatives considered**:
- Automatic retry with backoff: Adds complexity, may not succeed anyway
- Blank/broken image icon: Less informative for users
- Text-only fallback: Inconsistent with image-based UI

**Implementation details**:
- Placeholder generated using Pillow: gray background + centered text
- Cached as `placeholder_<part_number>.png` to avoid regeneration
- Displayed immediately on download failure (network error, 404, timeout)
- No distinction between network errors and missing images

---

### 6. Cache Management and Directory Structure

**Decision**: Flat directory structure with part-number-based filenames

**Rationale**:
- Simple lookup: `data/preview_images/{part_number}.png`
- No nested folders; all parts have unique identifiers
- Easy to inspect, backup, and manually manage
- Directory auto-created using `os.makedirs(exist_ok=True)`

**Alternatives considered**:
- Nested by set: Complicates sharing images across sets
- Color-coded subfolders: Unnecessary since colors flexible
- Database index: Over-engineered; filesystem sufficient

**Implementation details**:
- Filename sanitization: Replace special characters with underscores
- Format: Always PNG for consistency
- No expiration: Images persist indefinitely unless manually deleted
- File existence check before download: `os.path.exists(image_path)`

---

### 7. UI State Management During Downloads

**Decision**: Three visual states - cached, loading, failed

**Rationale**:
- Clear feedback for each state improves UX
- Non-blocking UI: users can interact during downloads
- Incremental updates as images arrive

**State transitions**:
1. **Cached**: Image exists locally → display immediately
2. **Loading**: Download in progress → show spinner/progress indicator
3. **Failed**: Download failed → show placeholder with part number

**Alternatives considered**:
- Binary states (loaded/not loaded): Less informative
- Percentage progress: Can't determine file size upfront; misleading
- Queue position indicator: Adds complexity

**Implementation details**:
- BrickListItem widget manages its own state
- Qt signals trigger state updates from background thread
- QMovie used for animated loading spinner
- State persists across scrolling (widget reuse handled correctly)

---

### 8. Threading Safety and Signal/Slot Pattern

**Decision**: Qt signals/slots for thread-safe UI updates

**Rationale**:
- Qt's signal/slot mechanism handles cross-thread communication safely
- Prevents race conditions when updating GUI from worker thread
- Well-documented PyQt6 pattern

**Alternatives considered**:
- Direct widget updates: Not thread-safe, causes crashes
- Queue polling: Inefficient, adds latency
- Thread locks: Error-prone, unnecessary with signals

**Implementation details**:
```python
class DownloadSignals(QObject):
    download_complete = pyqtSignal(str, str)  # part_number, file_path
    download_failed = pyqtSignal(str)         # part_number
    
# Background thread emits signals
signals.download_complete.emit(part_number, path)

# Main thread handles updates
signals.download_complete.connect(self._on_download_complete)
```

---

### 9. Testing Strategy

**Decision**: Unit tests for downloader logic, integration tests for UI

**Unit tests** (pytest):
- Mock HTTP requests using `unittest.mock.patch`
- Test color fallback logic (3 → 0-9 iteration)
- Test priority queue ordering
- Test rate limiting enforcement
- Test filename sanitization

**Integration tests** (manual + automated):
- Delete cache and reload set to trigger downloads
- Verify viewport-first prioritization
- Test placeholder display on network disconnect
- Verify no UI freezing during downloads

**Alternatives considered**:
- End-to-end GUI tests: Brittle, slow; manual testing sufficient
- Load testing: Unnecessary for single-user desktop app

---

### 10. Error Logging and Debugging

**Decision**: Python logging module with configurable levels

**Rationale**:
- Standard library; no additional dependencies
- Log download attempts, failures, and timing for debugging
- User-facing errors shown in UI; technical details in logs

**Log levels**:
- INFO: Successful downloads, cache hits
- WARNING: Download failures (404, network errors)
- ERROR: Unexpected exceptions
- DEBUG: Queue operations, priority assignments

**Implementation details**:
```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Downloaded image for {part_number}")
logger.warning(f"Failed to download {part_number}: {error}")
```

---

## Dependencies and Libraries

| Library | Purpose | Version | Installation |
|---------|---------|---------|--------------|
| PyQt6 | GUI framework (existing) | Latest | `pip install PyQt6` |
| requests | HTTP downloads | Latest | `pip install requests` |
| Pillow | Image handling (existing) | Latest | `pip install Pillow` |
| threading | Background downloads | stdlib | Built-in |
| queue | Priority queue | stdlib | Built-in |
| logging | Error tracking | stdlib | Built-in |

**Note**: No new major dependencies required; requests is the only addition.

---

## Best Practices Applied

1. **Separation of concerns**: ImageDownloader isolated from GUI code
2. **Thread safety**: Signals/slots for all cross-thread communication
3. **Graceful degradation**: Placeholders ensure UI usability without images
4. **Good citizenship**: Rate limiting respects BrickLink servers
5. **User responsiveness**: Background processing keeps UI interactive
6. **Testability**: Mocked HTTP requests for unit testing
7. **Error transparency**: Clear visual feedback + logging for debugging
8. **Simple file structure**: Flat directory for easy maintenance

---

## Open Questions / Future Enhancements

- **Image quality**: Could offer multiple resolutions (currently fixed)
- **Offline mode**: Pre-download all images for known sets
- **Retry mechanism**: Could add user-triggered retry button
- **Progress indicator**: Could show "X of Y downloaded" in UI
- **Color preference**: Could allow users to specify preferred color codes
- **Batch download**: Could offer "Download all" button for eager loading

These enhancements are deferred to maintain initial simplicity.
