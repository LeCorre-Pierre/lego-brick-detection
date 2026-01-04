# Research Document: Bricks in Set List Interface

**Feature**: Bricks in Set List Interface  
**Phase**: 0 - Research & Technology Decisions  
**Date**: January 4, 2026

## Overview

This document consolidates research findings for implementing the interactive brick list interface. All technical unknowns from the planning phase have been investigated and resolved.

## Research Tasks Completed

### 1. PyQt6 Custom List Widget Best Practices

**Question**: What is the optimal approach for creating custom list items in PyQt6 with complex layouts (images, checkboxes, labels, counters)?

**Decision**: Use `QListWidget` with custom `QWidget` items via `setItemWidget()`

**Rationale**:
- `QListWidget` + custom widgets provides flexibility for complex item layouts
- Better performance than `QTreeWidget` for flat lists
- Easier event handling (clicks, right-clicks) per item
- Native Qt styling and theming support
- Simpler than pure `QAbstractListModel` for this scale (< 200 items)

**Implementation Pattern**:
```python
class BrickListItem(QWidget):
    """Custom widget for individual brick entries"""
    def __init__(self, brick, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        # Add: preview image (QLabel), checkbox, detection icon, 
        # brick info (ID, name), counter display
        layout.addWidget(self.preview_image)
        layout.addWidget(self.checkbox)
        # ... etc
        
list_widget = QListWidget()
item = QListWidgetItem(list_widget)
widget = BrickListItem(brick)
item.setSizeHint(widget.sizeHint())
list_widget.setItemWidget(item, widget)
```

**Alternatives Considered**:
- `QTableWidget`: Too rigid for mixed content (images + interactive elements)
- `QTreeWidget`: Unnecessary hierarchy for flat list
- `QListView` + custom model: Over-engineered for < 200 items
- Pure canvas/painting: Poor accessibility and maintainability

---

### 2. Efficient Image Loading and Caching

**Question**: How to efficiently load and cache brick preview images to prevent lag when scrolling through 200+ items?

**Decision**: Implement lazy-loading image cache with LRU eviction and background loading

**Rationale**:
- Load images only when needed (visible items)
- Cache prevents repeated disk I/O
- LRU eviction keeps memory usage bounded
- Background loading prevents UI blocking
- Fallback to placeholder for missing images

**Implementation Approach**:
```python
from PIL import Image
from functools import lru_cache
from PyQt6.QtGui import QPixmap

class ImageCache:
    def __init__(self, max_size=100):
        self._cache = {}  # part_number -> QPixmap
        self._max_size = max_size
        
    def get_image(self, part_number, size=(48, 48)):
        """Get cached or load image for brick"""
        if part_number in self._cache:
            return self._cache[part_number]
            
        # Load from disk
        pixmap = self._load_and_scale(part_number, size)
        self._cache[part_number] = pixmap
        
        # LRU eviction if needed
        if len(self._cache) > self._max_size:
            self._cache.pop(next(iter(self._cache)))
            
        return pixmap
```

**Alternatives Considered**:
- Load all images at startup: 200+ images would cause slow startup
- No caching: Repeated disk I/O causes lag during scrolling
- Database storage: Overkill for local files
- Qt resource system: Requires compile-time bundling

---

### 3. Thread-Safe Detection Updates

**Question**: How to safely update the GUI list when detection events arrive from the vision processing thread at up to 30fps?

**Decision**: Use Qt signals/slots with queued connections and update batching

**Rationale**:
- Qt signals automatically handle thread safety with queued connections
- Batching reduces UI update frequency (e.g., every 100ms instead of per-frame)
- Prevents UI blocking from high-frequency updates
- Native Qt mechanism, no additional threading primitives needed

**Implementation Pattern**:
```python
class DetectionEngine(QObject):
    brick_detected = pyqtSignal(str, float)  # part_number, confidence
    
    def process_frame(self, frame):
        # ... detection logic ...
        for detection in detections:
            self.brick_detected.emit(detection.part_number, detection.confidence)
            
class BrickListWidget(QWidget):
    def __init__(self):
        # ...
        self.detection_engine.brick_detected.connect(
            self._on_brick_detected, Qt.ConnectionType.QueuedConnection
        )
        
        # Batch updates
        self._pending_detections = set()
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._apply_detection_updates)
        self._update_timer.start(100)  # Update UI every 100ms
```

**Alternatives Considered**:
- Direct GUI manipulation from worker thread: Thread-unsafe, causes crashes
- Thread locks: More complex, potential for deadlocks
- Polling: Inefficient, adds latency
- Complete UI rebuild per frame: Too slow for 30fps

---

### 4. Dynamic List Reordering Performance

**Question**: How to efficiently move detected bricks to the top of the list without causing flicker or performance issues?

**Decision**: Use `QListWidget.takeItem()` and `insertItem()` with update suspension

**Rationale**:
- Native QListWidget operations are optimized
- Suspending updates during batch reordering prevents flicker
- Track original positions to restore when detection ends
- Only reorder changed items, not entire list

**Implementation Pattern**:
```python
def move_to_top(self, part_numbers):
    """Move specified bricks to top of list"""
    self.setUpdatesEnabled(False)  # Prevent flicker
    
    # Collect items to move
    items_to_move = []
    for i in range(self.count()):
        item = self.item(i)
        widget = self.itemWidget(item)
        if widget.brick.part_number in part_numbers:
            items_to_move.append((item, widget))
    
    # Remove and reinsert at top
    for item, widget in items_to_move:
        row = self.row(item)
        self.takeItem(row)
        self.insertItem(0, item)
        self.setItemWidget(item, widget)
    
    self.setUpdatesEnabled(True)  # Re-enable updates
```

**Alternatives Considered**:
- Full list rebuild: Too slow, loses scroll position
- Custom sort model: Over-engineered for this use case
- Virtual scrolling: Unnecessary complexity for < 200 items

---

### 5. Right-Click Handling in List Items

**Question**: How to handle right-click events on list items to decrement counters?

**Decision**: Override `mousePressEvent` in custom widget and check for right button

**Rationale**:
- Direct event handling in custom widget is simplest
- Gives fine-grained control over click regions
- Can differentiate between clicking on counter vs checkbox vs image
- Prevents right-click context menu interference

**Implementation Pattern**:
```python
class BrickListItem(QWidget):
    counter_incremented = pyqtSignal(str)  # part_number
    counter_decremented = pyqtSignal(str)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Ignore if clicked on checkbox (it handles itself)
            if not self.checkbox.geometry().contains(event.pos()):
                self.counter_incremented.emit(self.brick.part_number)
        elif event.button() == Qt.MouseButton.RightButton:
            self.counter_decremented.emit(self.brick.part_number)
            event.accept()  # Prevent context menu
        super().mousePressEvent(event)
```

**Alternatives Considered**:
- Context menu for decrement: Extra click required, poor UX
- Separate +/- buttons: Takes up more space
- Double-click for decrement: Unintuitive

---

### 6. Completion Highlighting Approach

**Question**: What is the best way to highlight list items in green when brick counters reach required quantity?

**Decision**: Use `setStyleSheet()` on the custom widget with dynamic color updates

**Rationale**:
- Simple and performant for < 200 items
- Allows smooth transitions (can add CSS animations)
- Consistent with Qt styling system
- Easy to modify/theme

**Implementation Pattern**:
```python
class BrickListItem(QWidget):
    def update_completion_status(self, is_complete):
        if is_complete:
            self.setStyleSheet("""
                BrickListItem {
                    background-color: #d4edda;
                    border-left: 4px solid #28a745;
                }
            """)
        else:
            self.setStyleSheet("")  # Reset to default
```

**Alternatives Considered**:
- Manual QPainter drawing: More complex, harder to maintain
- Item background roles: Less flexible for styling
- Overlay widget: Overkill for simple highlight

---

## Technology Stack Summary

| Component | Technology | Justification |
|-----------|------------|---------------|
| GUI Framework | PyQt6 | Already in use, mature, cross-platform |
| List Widget | QListWidget + custom QWidget items | Balance of flexibility and simplicity |
| Image Loading | Pillow + QPixmap | Standard Python imaging, Qt integration |
| Image Caching | Custom LRU cache | Simple, memory-efficient |
| Thread Safety | Qt Signals/Slots | Built-in, safe, idiomatic |
| Update Batching | QTimer (100ms intervals) | Reduces UI update frequency |
| Styling | Qt StyleSheets | Native, themeable, easy to modify |
| Testing | pytest + pytest-qt | Python standard, Qt GUI testing support |

## Performance Expectations

Based on research and existing Qt applications:

- **List rendering**: < 50ms for 200 items with images
- **Image caching**: < 10ms per cached image load
- **Detection update**: < 100ms from detection to UI update (with batching)
- **Reordering**: < 20ms to move items to top
- **Counter update**: < 5ms per click
- **Memory usage**: ~50-100MB for 200 cached images (48x48 px)

## Implementation Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Image files missing/corrupt | Medium | Medium | Fallback to colored placeholder based on brick ID |
| Detection update rate too high | Low | Medium | Batching reduces updates to 10fps max |
| Large sets (>200 bricks) slow | Low | Medium | Lazy loading, consider virtual scrolling if needed |
| Right-click triggers context menu | Medium | Low | `event.accept()` in mouse handler |
| List flicker during reorder | Low | Medium | Suspend updates during batch operations |

## Open Questions Resolved

All technical clarifications from the planning phase have been addressed:

✅ Custom list widget approach (QListWidget + custom items)  
✅ Image loading and caching strategy (LRU cache with lazy loading)  
✅ Thread-safe detection updates (Qt signals + batching)  
✅ Dynamic reordering without flicker (update suspension)  
✅ Right-click handling (custom mousePressEvent)  
✅ Completion highlighting (dynamic stylesheets)

## Next Steps

Proceed to **Phase 1: Design** to create:
- `data-model.md`: Detailed data structures and state management
- `contracts/`: Component interfaces
- `quickstart.md`: Developer setup and implementation guide
