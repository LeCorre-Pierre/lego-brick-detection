# Developer Quickstart Guide: Brick List Interface

**Feature**: Bricks in Set List Interface  
**Branch**: `002-brick-list-interface`  
**Last Updated**: January 4, 2026

## Overview

This guide helps developers implement the interactive brick list interface. Follow the steps sequentially for a smooth implementation.

## Prerequisites

- Python 3.11+
- PyQt6 installed (`pip install PyQt6`)
- Pillow installed (`pip install Pillow`)
- Existing project structure with `src/models/`, `src/gui/`, `src/vision/` directories
- Familiarity with PyQt6 signals/slots and QListWidget

## Implementation Roadmap

### Phase 1: Extend Data Models (1-2 hours)

**Files to modify**:
- `src/models/brick.py`
- `src/models/lego_set.py`

**Tasks**:
1. Add new properties to `Brick` class:
   ```python
   manually_marked: bool = False
   detected_in_current_frame: bool = False
   last_detected_timestamp: float = 0.0
   original_list_position: int = 0
   ```

2. Add methods to `Brick`:
   - `mark_as_manually_found()` / `unmark_manually_found()`
   - `set_detected(timestamp)` / `clear_detected()`
   - `should_be_detected() -> bool`

3. Add methods to `LegoSet`:
   - `get_bricks_by_detection_status() -> Dict`
   - `update_detection_status(detected_part_numbers, timestamp)`
   - `get_detectable_bricks() -> List[Brick]`

**Testing**:
```bash
pytest tests/unit/test_brick_model.py
```

---

### Phase 2: Implement Image Cache (2-3 hours)

**Files to create**:
- `src/utils/image_cache.py`
- `tests/unit/test_image_cache.py`

**Tasks**:
1. Create `ImageCache` class with:
   - LRU cache using `OrderedDict`
   - `get_image(part_number) -> QPixmap`
   - `_load_image(part_number) -> QPixmap`
   - `_get_placeholder(part_number) -> QPixmap`

2. Implement placeholder generation:
   ```python
   def _get_placeholder(self, part_number: str) -> QPixmap:
       """Generate colored placeholder based on part_number hash"""
       # Use hash of part_number to generate consistent color
       # Create 48x48 pixmap with color and part_number text
   ```

3. Test image loading and caching:
   ```python
   def test_image_cache_loads_from_disk():
       cache = ImageCache(Path("data/brick_images"))
       pixmap = cache.get_image("3005")
       assert not pixmap.isNull()
   ```

**Testing**:
```bash
pytest tests/unit/test_image_cache.py -v
```

---

### Phase 3: Create BrickListItem Widget (3-4 hours)

**Files to create**:
- `src/gui/brick_list_item.py`

**Tasks**:
1. Create custom `QWidget` subclass with:
   - Horizontal layout
   - Preview image (QLabel)
   - Checkbox for manual marking
   - Detection indicator icon (QLabel)
   - Brick info labels (ID, name)
   - Counter display (QLabel)

2. Implement layout:
   ```python
   layout = QHBoxLayout()
   layout.addWidget(self.preview_label)      # 48x48
   layout.addWidget(self.checkbox)           # 20x20
   layout.addWidget(self.detection_icon)     # 20x20
   layout.addWidget(self.info_widget)        # Stretch
   layout.addWidget(self.counter_label)      # Fixed width
   ```

3. Override `mousePressEvent` for click handling:
   ```python
   def mousePressEvent(self, event):
       if event.button() == Qt.MouseButton.LeftButton:
           if not self.checkbox.geometry().contains(event.pos()):
               self.counter_incremented.emit()
       elif event.button() == Qt.MouseButton.RightButton:
           self.counter_decremented.emit()
           event.accept()  # Prevent context menu
   ```

4. Implement styling methods:
   - `_apply_completion_highlight()` - Green background
   - `_remove_completion_highlight()` - Default background

**Manual Testing**:
- Create standalone test script to verify layout
- Test click handling (left/right)
- Verify checkbox behavior
- Check visual appearance

---

### Phase 4: Create BrickListWidget (4-5 hours)

**Files to create**:
- `src/gui/brick_list_widget.py`

**Tasks**:
1. Create `QListWidget` subclass with internal `BrickListState` class

2. Implement core methods:
   ```python
   def load_set(self, lego_set: LegoSet):
       """Populate list with bricks"""
       self._state.original_order = [b.part_number for b in lego_set.bricks]
       for brick in lego_set.bricks:
           self._add_brick_item(brick)
   
   def _add_brick_item(self, brick: Brick):
       """Create and add a BrickListItem to the list"""
       item = QListWidgetItem(self)
       widget = BrickListItem(brick, self._image_cache)
       item.setSizeHint(QSize(0, 60))
       self.setItemWidget(item, widget)
       
       # Connect signals
       widget.counter_incremented.connect(
           lambda: self._on_counter_increment(brick.part_number)
       )
       widget.counter_decremented.connect(
           lambda: self._on_counter_decrement(brick.part_number)
       )
   ```

3. Implement detection update batching:
   ```python
   def __init__(self):
       # ...
       self._update_timer = QTimer()
       self._update_timer.timeout.connect(self._apply_detection_updates)
       self._update_timer.start(100)  # 100ms batching
   
   def update_detection_status(self, detected_part_numbers: Set[str]):
       """Queue detection update (batched)"""
       self._state.pending_detections = detected_part_numbers
   
   def _apply_detection_updates(self):
       """Apply batched detection updates"""
       if not self._state.pending_detections:
           return
       
       # Update brick models
       for brick in self._current_set.bricks:
           if brick.part_number in self._state.pending_detections:
               brick.set_detected(time.time())
           else:
               brick.clear_detected()
       
       # Reorder list
       self._reorder_list()
       
       # Update item widgets
       self._update_detection_icons()
       
       self._state.pending_detections.clear()
   ```

4. Implement list reordering:
   ```python
   def _reorder_list(self):
       """Move detected bricks to top"""
       self.setUpdatesEnabled(False)
       
       detected = []
       not_detected = []
       
       for i in range(self.count()):
           item = self.item(i)
           widget = self.itemWidget(item)
           if widget.brick.detected_in_current_frame:
               detected.append((item, widget))
           else:
               not_detected.append((item, widget))
       
       # Rebuild list with detected at top
       self.clear()
       for item, widget in detected + not_detected:
           new_item = QListWidgetItem(self)
           new_item.setSizeHint(item.sizeHint())
           self.addItem(new_item)
           self.setItemWidget(new_item, widget)
       
       self.setUpdatesEnabled(True)
   ```

**Testing**:
```bash
pytest tests/integration/test_brick_list_integration.py
```

---

### Phase 5: Refactor SetInfoPanel (2-3 hours)

**Files to modify**:
- `src/gui/set_info_panel.py`

**Tasks**:
1. Replace existing basic list display with `BrickListWidget`

2. Update `load_set()` method:
   ```python
   def load_set(self, lego_set: LegoSet):
       self.current_set = lego_set
       self.brick_list_widget.load_set(lego_set)
       # ... update other UI elements ...
   ```

3. Connect signals to existing methods:
   ```python
   self.brick_list_widget.brick_counter_changed.connect(
       self._update_progress
   )
   self.brick_list_widget.brick_manually_marked.connect(
       self._on_manual_marked
   )
   ```

---

### Phase 6: Wire Detection Updates (2-3 hours)

**Files to modify**:
- `src/vision/detection_engine.py`
- `src/gui/main_window.py`

**Tasks**:
1. Add signal to `DetectionEngine`:
   ```python
   class DetectionEngine(QObject):
       brick_detected = pyqtSignal(str, float)  # part_number, confidence
       frame_processed = pyqtSignal(set)  # detected_part_numbers
   ```

2. Emit signals during frame processing:
   ```python
   def process_frame(self, frame):
       detections = self.model.detect(frame)
       detected_part_numbers = {d.part_number for d in detections}
       
       for detection in detections:
           self.brick_detected.emit(detection.part_number, detection.confidence)
       
       self.frame_processed.emit(detected_part_numbers)
   ```

3. Connect to list widget in `MainWindow`:
   ```python
   def _setup_connections(self):
       self.detection_engine.frame_processed.connect(
           self.set_info_panel.brick_list_widget.update_detection_status
       )
   ```

---

### Phase 7: Add Preview Images (1-2 hours)

**Tasks**:
1. Create directory structure:
   ```bash
   mkdir -p data/brick_images
   ```

2. Generate or download brick preview images:
   - Images should be named by part number (e.g., `3005.png`)
   - Recommended size: at least 48x48 pixels
   - Format: PNG with transparency

3. Test with sample images:
   ```bash
   # Place test images in data/brick_images/
   # Run application and verify images load
   python -m src.main --set-file ./data/sample_3005.csv --camera 0
   ```

---

### Phase 8: Testing & Polish (3-4 hours)

**Tasks**:
1. Run full test suite:
   ```bash
   pytest tests/ -v --cov=src/gui --cov=src/models
   ```

2. Manual testing checklist:
   - [ ] Load set and verify all bricks displayed
   - [ ] Left-click increments counter
   - [ ] Right-click decrements counter
   - [ ] Counter stops at required quantity
   - [ ] Green highlight appears when complete
   - [ ] Checkbox marks brick as manually found
   - [ ] Detection icon appears for detected bricks
   - [ ] Detected bricks move to top of list
   - [ ] List scrolling is smooth
   - [ ] Preview images load correctly
   - [ ] Placeholders shown for missing images

3. Performance testing:
   - Test with set containing 200+ bricks
   - Verify smooth scrolling
   - Check detection update latency (<500ms)
   - Monitor memory usage

4. Polish:
   - Adjust colors/fonts for readability
   - Fine-tune layout spacing
   - Add tooltips for icons
   - Improve error messages

---

## Common Pitfalls & Solutions

### Issue: List flickers during reordering

**Solution**: Wrap reorder operations in `setUpdatesEnabled(False/True)`:
```python
self.setUpdatesEnabled(False)
# ... reorder operations ...
self.setUpdatesEnabled(True)
```

### Issue: Right-click shows context menu

**Solution**: Call `event.accept()` in `mousePressEvent`:
```python
elif event.button() == Qt.MouseButton.RightButton:
    self.counter_decremented.emit()
    event.accept()  # Prevents context menu
```

### Issue: Detection updates block UI

**Solution**: Ensure using `Qt.ConnectionType.QueuedConnection` and batching:
```python
self.detection_engine.brick_detected.connect(
    self._on_brick_detected, 
    Qt.ConnectionType.QueuedConnection
)
```

### Issue: Images not loading

**Solution**: Check file paths and add error logging:
```python
def _load_image(self, part_number: str) -> QPixmap:
    path = self._image_dir / f"{part_number}.png"
    if not path.exists():
        self.logger.warning(f"Image not found: {path}")
        return self._get_placeholder(part_number)
    # ...
```

---

## Debugging Tips

### Enable debug logging:
```python
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("brick_list")
```

### Inspect list state:
```python
def debug_list_state(self):
    print(f"Total items: {self.count()}")
    print(f"Detected: {self._state.detected_bricks}")
    print(f"Pending: {self._state.pending_detections}")
```

### Profile performance:
```python
import cProfile
cProfile.run('self.brick_list.update_detection_status(detected_set)')
```

---

## Integration Checklist

Before merging to main branch:

- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing complete (see Phase 8)
- [ ] Code reviewed by teammate
- [ ] Documentation updated (README, docstrings)
- [ ] No `TODO` or `FIXME` comments remain
- [ ] Git commit messages are descriptive
- [ ] Branch rebased on latest main
- [ ] No merge conflicts

---

## Estimated Total Time

| Phase | Hours |
|-------|-------|
| 1. Data Models | 1-2 |
| 2. Image Cache | 2-3 |
| 3. BrickListItem | 3-4 |
| 4. BrickListWidget | 4-5 |
| 5. SetInfoPanel Refactor | 2-3 |
| 6. Detection Wiring | 2-3 |
| 7. Preview Images | 1-2 |
| 8. Testing & Polish | 3-4 |
| **Total** | **18-26 hours** |

Plan for 3-5 days of focused development for a single developer.

---

## Next Steps After Completion

1. Run `/speckit.tasks` to generate implementation task breakdown
2. Create pull request with comprehensive description
3. Request code review
4. Address feedback and merge
5. Update project documentation
6. Celebrate! 🎉

---

## Questions or Issues?

Refer to:
- [spec.md](spec.md) - Feature specification
- [data-model.md](data-model.md) - Data structures and flow
- [contracts/brick_list_interface.py](contracts/brick_list_interface.py) - Component interfaces
- [research.md](research.md) - Technical decisions and alternatives

For implementation-specific questions, check existing PyQt6 docs and the project's constitution principles.
