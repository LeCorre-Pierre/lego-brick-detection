# Data Model: Automatic Preview Image Downloads

**Feature**: 003-auto-download-previews  
**Date**: January 7, 2026  
**Purpose**: Define data structures and relationships for preview image management

## Overview

This feature extends existing data models and introduces new entities for managing automatic preview image downloads. The design emphasizes simplicity, thread safety, and integration with the existing PyQt6 GUI architecture.

---

## Core Entities

### 1. DownloadRequest

Represents a single image download request with prioritization metadata.

**Attributes**:
- `part_number: str` - Unique identifier for the Lego brick (e.g., "3001")
- `priority: int` - Download priority (0 = viewport/highest, higher = lower priority)
- `color_code: int` - Current color code being attempted (0-9)
- `timestamp: float` - Time when request was created (for FIFO tie-breaking)
- `retry_count: int` - Number of color codes tried (max 10)

**Behavior**:
- Immutable once created (functional style)
- Comparable via priority for queue ordering
- Generates URL dynamically based on current color_code

**Relationships**:
- Queued in DownloadQueue for processing
- Results in ImageCacheEntry upon completion

**Validation Rules**:
- `part_number` must not be empty
- `priority >= 0`
- `color_code` in range [0-9]
- `retry_count <= 10`

---

### 2. ImageCacheEntry

Represents cached state of a preview image (existing entity, extended).

**Attributes** (existing):
- `part_number: str` - Brick identifier
- `file_path: Path` - Absolute path to cached image file

**New Attributes**:
- `status: ImageStatus` - Current download/cache state (enum)
- `last_updated: datetime` - Timestamp of last status change
- `error_message: Optional[str]` - Failure reason if status == FAILED

**State Transitions**:
```
MISSING → DOWNLOADING → CACHED
MISSING → DOWNLOADING → FAILED
CACHED → (terminal state)
FAILED → (terminal state, no retry)
```

**Behavior**:
- `is_cached()` - Returns True if image file exists on disk
- `get_display_path()` - Returns cached path or placeholder path based on status
- `mark_downloading()` - Transitions to DOWNLOADING state
- `mark_complete(path)` - Transitions to CACHED state
- `mark_failed(error)` - Transitions to FAILED state

**Relationships**:
- One-to-one with Brick entity (via part_number)
- Referenced by BrickListItem for display

---

### 3. ImageStatus (Enum)

Defines possible states for preview images.

**Values**:
- `MISSING` - Image not yet downloaded or queued
- `DOWNLOADING` - Download in progress
- `CACHED` - Image successfully downloaded and stored locally
- `FAILED` - Download failed (network error, 404, timeout)

**Usage**:
- Controls UI rendering (loading spinner, placeholder, actual image)
- Prevents redundant download attempts
- Determines whether to queue download request

---

### 4. DownloadQueue

Priority queue managing pending download requests.

**Attributes**:
- `_queue: PriorityQueue` - Underlying thread-safe queue
- `_in_progress: Set[str]` - Part numbers currently being downloaded
- `_lock: threading.Lock` - Protects in_progress set

**Behavior**:
- `enqueue(request: DownloadRequest)` - Adds request if not in progress
- `dequeue() -> Optional[DownloadRequest]` - Retrieves highest-priority request (blocks if empty)
- `is_queued(part_number: str) -> bool` - Checks if part already queued/in-progress
- `clear()` - Empties queue (for shutdown)

**Concurrency**:
- Thread-safe via PriorityQueue and Lock
- Prevents duplicate downloads for same part_number
- Non-blocking enqueue, blocking dequeue

**Relationships**:
- Contains DownloadRequest instances
- Processed by ImageDownloadWorker

---

### 5. ImageDownloadWorker

Background thread processing download queue.

**Attributes**:
- `queue: DownloadQueue` - Source of download requests
- `signals: DownloadSignals` - Qt signals for main thread communication
- `_stop_flag: threading.Event` - Graceful shutdown signal
- `_last_download_time: float` - Timestamp for rate limiting

**Behavior**:
- `run()` - Main loop: dequeue → download → emit signal → rate limit
- `stop()` - Sets stop flag for graceful shutdown
- `_download_image(request)` - HTTP download with color fallback logic
- `_enforce_rate_limit()` - Ensures 1-second delay between requests

**Lifecycle**:
1. Started as daemon thread when GUI initializes
2. Processes queue continuously until stop flag set
3. Joins main thread on application exit

**Relationships**:
- Consumes from DownloadQueue
- Emits DownloadSignals
- Updates ImageCacheEntry status

---

### 6. DownloadSignals (QObject)

Qt signal emitter for thread-safe GUI updates.

**Signals**:
- `download_started(part_number: str)` - Download initiated
- `download_complete(part_number: str, file_path: str)` - Success
- `download_failed(part_number: str, error: str)` - Failure

**Usage**:
```python
signals = DownloadSignals()
signals.download_complete.connect(self._on_download_complete)
signals.download_started.emit(part_number)
```

**Thread Safety**:
- QObject ensures signals processed on main thread
- Emitted from worker thread, handled in GUI thread
- Prevents race conditions when updating widgets

**Relationships**:
- Created by ImageDownloader
- Connected to BrickListWidget slots
- Emitted by ImageDownloadWorker

---

## Data Relationships

```
┌─────────────────┐
│     Brick       │ (existing model)
│  - part_number  │
└────────┬────────┘
         │ 1:1
         ↓
┌─────────────────────┐
│  ImageCacheEntry    │ (extended)
│  - part_number      │
│  - file_path        │
│  - status: ImageStatus │
│  - last_updated     │
│  - error_message    │
└──────────┬──────────┘
           │ referenced by
           ↓
┌─────────────────────┐
│  BrickListItem      │ (existing widget, updated)
│  - displays image   │
│  - shows status     │
└─────────────────────┘

┌─────────────────────┐
│  DownloadRequest    │
│  - part_number      │
│  - priority         │
│  - color_code       │
└──────────┬──────────┘
           │ queued in
           ↓
┌─────────────────────┐
│  DownloadQueue      │
│  - _queue           │
│  - _in_progress     │
└──────────┬──────────┘
           │ processed by
           ↓
┌─────────────────────┐
│ ImageDownloadWorker │ (daemon thread)
│  - run()            │
│  - _download_image()│
└──────────┬──────────┘
           │ emits
           ↓
┌─────────────────────┐
│  DownloadSignals    │ (QObject)
│  - download_complete│
│  - download_failed  │
└──────────┬──────────┘
           │ updates
           ↓
┌─────────────────────┐
│  BrickListWidget    │ (main thread)
│  - slot handlers    │
└─────────────────────┘
```

---

## File System Structure

### Directory Layout

```
data/
└── preview_images/              # Auto-created on first download
    ├── 3001.png                 # Cached brick images
    ├── 3003.png
    ├── 2456.png
    ├── placeholder_3002.png     # Generated placeholders for failures
    └── ...
```

**Naming Convention**:
- Successful downloads: `<part_number>.png`
- Placeholders: `placeholder_<part_number>.png`
- Special characters in part_number replaced with underscores

**File Operations**:
- Check existence: `os.path.exists(file_path)`
- Create directory: `os.makedirs(path, exist_ok=True)`
- Write image: `image.save(file_path)`
- Read image: `QPixmap(file_path)`

---

## Concurrency Model

### Thread Architecture

```
Main Thread (GUI):
├── BrickListWidget renders items
├── Enqueues DownloadRequests based on viewport
├── Connects to DownloadSignals
└── Updates UI on signal reception

Background Thread (Worker):
├── Dequeues DownloadRequest
├── Downloads image via HTTP
├── Saves to filesystem
├── Emits DownloadSignals
└── Enforces 1-second rate limit
```

### Synchronization Points

1. **DownloadQueue**: Thread-safe via `queue.PriorityQueue`
2. **ImageCacheEntry status**: Protected by Qt's main thread affinity
3. **DownloadSignals**: Qt's signal/slot mechanism ensures thread safety
4. **File system writes**: Sequential (one thread writes), no locking needed

**No shared mutable state** between threads except:
- DownloadQueue (thread-safe)
- Qt signals (thread-safe by design)

---

## Validation Rules

### Part Number Validation
- Non-empty string
- Allowed characters: alphanumeric + hyphen + underscore
- Special characters sanitized for filenames

### Color Code Validation
- Integer in range [0-9]
- Fallback sequence: start at 3, then 0-9
- Stop after first success or after 10 attempts

### Priority Validation
- Non-negative integer
- Viewport items: priority = 0
- Non-viewport items: priority = list_index (1, 2, 3, ...)

### File Path Validation
- Must be within `data/preview_images/` directory
- File extension: `.png`
- Sanitized filename (no path traversal)

---

## State Management

### ImageCacheEntry Lifecycle

```
┌─────────┐
│ MISSING │ ← Initial state
└────┬────┘
     │ download requested
     ↓
┌──────────────┐
│ DOWNLOADING  │ ← Intermediate state
└────┬─────────┘
     │
     ├─ success ─→ ┌─────────┐
     │              │ CACHED  │ ← Terminal state
     │              └─────────┘
     │
     └─ failure ─→ ┌─────────┐
                    │ FAILED  │ ← Terminal state (no retry)
                    └─────────┘
```

### DownloadRequest Lifecycle

```
Created → Enqueued → Dequeued → Processing → [Color fallback loop] → Complete/Failed
```

**Color Fallback**:
```python
for color_code in [3, 0, 1, 2, 4, 5, 6, 7, 8, 9]:
    url = f"https://img.bricklink.com/ItemImage/PN/{color_code}/{part_number}.png"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        return response.content  # Success, stop iteration
# All colors failed
return None
```

---

## Error Handling

### Download Errors

| Error Type | Detection | Handling |
|------------|-----------|----------|
| Network timeout | `requests.exceptions.Timeout` | Mark FAILED, emit signal |
| HTTP 404 | `response.status_code == 404` | Try next color code |
| Connection error | `requests.exceptions.ConnectionError` | Mark FAILED immediately |
| Invalid image | `PIL.Image.open()` raises | Mark FAILED, log error |
| Disk full | `OSError` on write | Mark FAILED, show error |

**No retries**: Once all color codes exhausted or critical error occurs, status set to FAILED permanently.

### Placeholder Generation

On FAILED status:
1. Generate 200x200 gray image using Pillow
2. Draw part number text centered
3. Save as `placeholder_<part_number>.png`
4. Display in BrickListItem

---

## Performance Considerations

### Memory Usage
- `DownloadQueue`: O(N) where N = number of bricks in set (~50-500)
- `ImageCacheEntry`: O(M) where M = total unique bricks across all sets (~1000s)
- Downloaded images: ~50-200KB each, total <100MB for typical set

### Download Time
- Network request: ~1-3 seconds per image
- Rate limiting: +1 second per image
- Typical set (100 bricks): ~3-5 minutes total
- Viewport priority: Visible images load in ~10 seconds

### UI Responsiveness
- No blocking on main thread (all downloads in worker thread)
- Signals processed asynchronously
- Scrolling remains smooth during downloads

---

## Testing Scenarios

### Unit Test Cases

1. **DownloadRequest priority comparison**
   - Viewport request (priority=0) < non-viewport request (priority=5)

2. **Color fallback logic**
   - Mock 404 responses for colors 3,0,1,2 → success on color 4
   - Mock 404 for all colors → status = FAILED

3. **Rate limiting enforcement**
   - Verify 1-second delay between consecutive downloads

4. **Priority queue ordering**
   - Enqueue requests with priorities [5, 0, 3, 1] → dequeue order [0, 1, 3, 5]

5. **Duplicate request prevention**
   - Enqueue same part_number twice → only one download occurs

### Integration Test Cases

1. **End-to-end download flow**
   - Clear cache → load set → verify viewport images download first

2. **Failure placeholder display**
   - Disconnect network → load set → verify placeholders appear

3. **Cache persistence**
   - Download images → restart app → verify no re-downloads

4. **Viewport prioritization**
   - Load large set → scroll down → verify top items still prioritized

---

## Future Extensions

### Potential Enhancements

1. **Download cancellation**: Allow user to pause/cancel downloads
2. **Progress tracking**: Show "X of Y downloaded" counter
3. **Retry mechanism**: Button to retry failed downloads
4. **Color preference**: User-configurable default color code
5. **Batch download**: Preload all images for a set
6. **Cache expiration**: Delete old/unused images after N days
7. **Multiple image sources**: Fallback to Rebrickable if BrickLink fails

These enhancements deferred to maintain implementation simplicity.
