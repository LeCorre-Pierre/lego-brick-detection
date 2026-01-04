# Data Model: Bricks in Set List Interface

**Feature**: Bricks in Set List Interface  
**Phase**: 1 - Design  
**Date**: January 4, 2026

## Overview

This document defines the data structures, state management, and data flow for the brick list interface feature.

## Core Entities

### 1. Brick (Extended)

**Location**: `src/models/brick.py`

**Purpose**: Represents an individual Lego brick with tracking state

**Properties**:
```python
@dataclass
class Brick:
    # Existing properties
    part_number: str
    color: str
    quantity: int
    found_quantity: int = 0
    dimensions: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    
    # NEW properties for this feature
    manually_marked: bool = False           # User checked the "found manually" checkbox
    detected_in_current_frame: bool = False  # Currently detected in video frame
    last_detected_timestamp: float = 0.0    # Timestamp of last detection
    original_list_position: int = 0         # Position before reordering
```

**New Methods**:
```python
def mark_as_manually_found(self) -> None:
    """Mark this brick as manually found (checkbox checked)"""
    self.manually_marked = True
    
def unmark_manually_found(self) -> None:
    """Remove manual found marking"""
    self.manually_marked = False
    
def set_detected(self, timestamp: float) -> None:
    """Mark as detected in current frame"""
    self.detected_in_current_frame = True
    self.last_detected_timestamp = timestamp
    
def clear_detected(self) -> None:
    """Clear detection status"""
    self.detected_in_current_frame = False
    
def should_be_detected(self) -> bool:
    """Check if this brick should be included in detection"""
    return not self.manually_marked and not self.is_fully_found()
```

**Validation Rules**:
- `found_quantity` cannot exceed `quantity`
- `found_quantity` cannot be negative
- If `manually_marked` is True, `should_be_detected()` returns False

---

### 2. LegoSet (Extended)

**Location**: `src/models/lego_set.py`

**Purpose**: Manages collection of bricks with detection updates

**New Methods**:
```python
def get_bricks_by_detection_status(self) -> Dict[str, List[Brick]]:
    """Get bricks grouped by detection status"""
    return {
        'detected': [b for b in self.bricks if b.detected_in_current_frame],
        'not_detected': [b for b in self.bricks if not b.detected_in_current_frame],
        'manually_marked': [b for b in self.bricks if b.manually_marked],
        'completed': [b for b in self.bricks if b.is_fully_found()]
    }
    
def update_detection_status(self, detected_part_numbers: Set[str], timestamp: float) -> None:
    """Update detection status for all bricks based on current frame"""
    for brick in self.bricks:
        if brick.part_number in detected_part_numbers:
            brick.set_detected(timestamp)
        else:
            brick.clear_detected()
            
def get_detectable_bricks(self) -> List[Brick]:
    """Get list of bricks that should be detected"""
    return [b for b in self.bricks if b.should_be_detected()]
```

---

### 3. BrickListState (NEW)

**Location**: `src/gui/brick_list_widget.py` (internal class)

**Purpose**: Manages UI state for the brick list

**Properties**:
```python
@dataclass
class BrickListState:
    """Manages state for brick list display"""
    # Original ordering (before detection-based reordering)
    original_order: List[str] = field(default_factory=list)  # part_numbers
    
    # Currently detected bricks (at top of list)
    detected_bricks: Set[str] = field(default_factory=set)  # part_numbers
    
    # Pending detection updates (batched)
    pending_detections: Set[str] = field(default_factory=set)
    
    # Image cache reference
    image_cache: Optional['ImageCache'] = None
    
    # Scroll position (to preserve during updates)
    scroll_position: int = 0
```

**Methods**:
```python
def add_detected(self, part_number: str) -> bool:
    """Add brick to detected set. Returns True if new."""
    if part_number not in self.detected_bricks:
        self.detected_bricks.add(part_number)
        return True
    return False
    
def remove_detected(self, part_number: str) -> bool:
    """Remove brick from detected set. Returns True if was detected."""
    if part_number in self.detected_bricks:
        self.detected_bricks.remove(part_number)
        return True
    return False
    
def get_sorted_brick_order(self, all_bricks: List[Brick]) -> List[Brick]:
    """Get bricks sorted with detected at top, then original order"""
    detected = [b for b in all_bricks if b.part_number in self.detected_bricks]
    not_detected = [b for b in all_bricks if b.part_number not in self.detected_bricks]
    return detected + not_detected
```

---

### 4. ImageCache (NEW)

**Location**: `src/utils/image_cache.py`

**Purpose**: Efficiently load and cache brick preview images

**Properties**:
```python
class ImageCache:
    """LRU cache for brick preview images"""
    def __init__(self, image_dir: Path, max_size: int = 100, image_size: Tuple[int, int] = (48, 48)):
        self._image_dir = image_dir
        self._max_size = max_size
        self._image_size = image_size
        self._cache: OrderedDict[str, QPixmap] = OrderedDict()
        self._placeholder: Optional[QPixmap] = None
```

**Methods**:
```python
def get_image(self, part_number: str) -> QPixmap:
    """Get cached or load image for brick part number"""
    
def _load_image(self, part_number: str) -> QPixmap:
    """Load image from disk and scale to target size"""
    
def _get_placeholder(self, part_number: str) -> QPixmap:
    """Generate colored placeholder for missing images"""
    
def preload_images(self, part_numbers: List[str]) -> None:
    """Preload images in background"""
    
def clear(self) -> None:
    """Clear all cached images"""
```

---

## Component Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                        MainWindow                            │
│  - Coordinates detection updates to list                    │
│  - Wires signals between detection engine and list widget   │
└───────────────┬─────────────────────────────┬───────────────┘
                │                             │
                │                             │
        ┌───────▼────────┐           ┌────────▼──────────┐
        │ DetectionEngine│           │ SetInfoPanel      │
        │                │           │ (refactored)      │
        │ - Emits:       │           │                   │
        │   brick_       │           │ Contains:         │
        │   detected     │◄──────────┤ BrickListWidget   │
        │   signal       │           │                   │
        └────────────────┘           └─────────┬─────────┘
                                               │
                                               │
                               ┌───────────────▼──────────────┐
                               │      BrickListWidget          │
                               │  - QListWidget subclass       │
                               │  - Manages BrickListState     │
                               │  - Handles reordering         │
                               │  - Batches detection updates  │
                               └────┬──────────────────┬───────┘
                                    │                  │
                        ┌───────────▼─────┐   ┌────────▼─────────┐
                        │ BrickListItem   │   │  ImageCache       │
                        │ (custom widget) │   │  - Loads images   │
                        │ - Preview image │◄──┤  - LRU eviction   │
                        │ - Checkbox      │   │  - Placeholders   │
                        │ - Counter       │   └──────────────────┘
                        │ - Detection icon│
                        └─────────────────┘
                                │
                                │
                     ┌──────────▼────────────┐
                     │  Brick (model)        │
                     │  - Properties         │
                     │  - State tracking     │
                     └───────────────────────┘
```

## State Transitions

### Brick Detection State Machine

```
┌────────────┐
│  Initial   │ (not detected, not marked)
└─────┬──────┘
      │
      │ Detection event arrives
      │
      ▼
┌────────────┐
│  Detected  │ (detected_in_current_frame = True)
└─────┬──────┘
      │
      │ Frame processed without detection
      │
      ▼
┌────────────┐
│ Not Detected│ (detected_in_current_frame = False)
└─────┬──────┘
      │
      │ User checks "manually found"
      │
      ▼
┌────────────┐
│Manually    │ (manually_marked = True)
│Marked      │ → Excluded from detection
└────────────┘
```

### Counter State Transitions

```
┌──────────────┐
│ found_qty: 0 │
└──────┬───────┘
       │
       │ Left click
       ▼
┌──────────────┐
│ found_qty: 1 │
└──────┬───────┘
       │
       │ Left click (repeat)
       ▼
       ...
       ▼
┌──────────────┐           ┌──────────────┐
│ found_qty: N │──Right───▶│ found_qty:N-1│
│ (N = quantity)│  click    └──────────────┘
│ → GREEN      │
│   HIGHLIGHT  │
└──────────────┘
```

### List Order State Transitions

```
Original Order:
[Brick A, Brick B, Brick C, Brick D, Brick E]
                    │
                    │ Brick C detected
                    ▼
Reordered:
[Brick C, Brick A, Brick B, Brick D, Brick E]
                    │
                    │ Brick C no longer detected
                    ▼
Restored:
[Brick A, Brick B, Brick C, Brick D, Brick E]
```

## Data Flow

### 1. Set Loading Flow

```
User loads set → SetLoader reads CSV → Creates LegoSet with Bricks
                                              │
                                              ▼
                                    BrickListWidget.load_set()
                                              │
                                              ├─> Store original order
                                              ├─> Create BrickListItem for each brick
                                              ├─> Preload images (background)
                                              └─> Display list
```

### 2. Detection Update Flow

```
Camera frame → DetectionEngine.process_frame()
                       │
                       ├─> Detects Brick X
                       └─> Emits brick_detected(part_number="X")
                                   │
                                   ▼
                      BrickListWidget._on_brick_detected()
                                   │
                                   ├─> Add to pending_detections
                                   └─> (batched via QTimer)
                                              │
                                              ▼ (every 100ms)
                           BrickListWidget._apply_detection_updates()
                                              │
                                              ├─> Update Brick.detected_in_current_frame
                                              ├─> Move detected bricks to top
                                              ├─> Update detection icons
                                              └─> Clear pending_detections
```

### 3. User Interaction Flow (Counter)

```
User clicks brick item → BrickListItem.mousePressEvent()
                                   │
                    ┌──────────────┴────────────────┐
                    │                               │
              Left click                      Right click
                    │                               │
                    ▼                               ▼
        increment_counter signal          decrement_counter signal
                    │                               │
                    └──────────┬────────────────────┘
                               ▼
                   BrickListWidget._on_counter_changed()
                               │
                               ├─> Update Brick.found_quantity
                               ├─> Update BrickListItem display
                               ├─> Check if complete (apply green highlight)
                               └─> Update progress tracker
```

### 4. Manual Marking Flow

```
User clicks checkbox → BrickListItem.checkbox.toggled signal
                                   │
                                   ▼
                   BrickListWidget._on_manual_marked()
                                   │
                                   ├─> Update Brick.manually_marked
                                   ├─> Remove from detectable set
                                   └─> Update detection engine filter
```

## Data Persistence

**Session State** (in-memory only):
- Brick counters (`found_quantity`)
- Manual marking status (`manually_marked`)
- Detection status (transient, not persisted)

**Future Enhancement** (out of scope for this feature):
- Save/load session state to JSON
- Export progress reports

## Performance Considerations

### Memory Usage

| Component | Memory per Item | Total (200 items) |
|-----------|----------------|-------------------|
| Brick object | ~200 bytes | 40 KB |
| BrickListItem widget | ~2 KB | 400 KB |
| Cached QPixmap (48x48) | ~10 KB | 1 MB (for 100 cached) |
| **Total Estimate** | | **~1.5 MB** |

### Update Frequency

| Operation | Frequency | Batch Size | UI Update Rate |
|-----------|-----------|------------|----------------|
| Detection updates | 30 fps | 100ms batches | 10 Hz |
| Counter clicks | User-driven | Immediate | N/A |
| List reordering | Per batch | 100ms | 10 Hz |
| Image loading | On-demand | Lazy | N/A |

## Validation Rules

### Brick Level
- `found_quantity` ≤ `quantity`
- `found_quantity` ≥ 0
- If `manually_marked`, exclude from detection
- If `is_fully_found()`, apply green highlight

### List Level
- Detected bricks always at top
- Maintain original order within detected/non-detected groups
- Preserve scroll position during updates (where possible)

### UI Level
- Counter display format: "X/Y" (found/required)
- Green highlight when X == Y
- Detection icon visible only when `detected_in_current_frame`
- Checkbox disabled if brick is completed

## Error Handling

| Error Condition | Handling Strategy |
|----------------|-------------------|
| Missing preview image | Show colored placeholder based on part_number hash |
| Invalid counter value | Clamp to [0, quantity] range |
| Detection for unknown brick | Log warning, ignore update |
| Image load failure | Use placeholder, log error |
| Thread synchronization issue | Qt signals handle automatically |

## Testing Strategy

### Unit Tests
- `Brick` model extensions (manual marking, detection status)
- `ImageCache` LRU behavior and placeholder generation
- Counter increment/decrement logic
- List sorting with detected bricks

### Integration Tests
- Detection updates trigger list reordering
- Counter updates trigger highlight changes
- Manual marking excludes from detection
- Image caching during scroll

### Manual Testing
- Visual inspection of layout and styling
- Performance with 200-item list
- Smooth reordering without flicker
- Right-click behavior

## Data Model Summary

**New Classes**: 2 (`ImageCache`, `BrickListState`)  
**Extended Classes**: 2 (`Brick`, `LegoSet`)  
**New GUI Components**: 2 (`BrickListWidget`, `BrickListItem`)  
**Total Data Properties Added**: 5 (in `Brick` model)  
**Total New Methods**: ~20 across all components  

---

**Status**: ✅ Data model design complete. Ready for contract definition and quickstart guide.