# Implementation Plan: Bricks in Set List Interface

**Branch**: `002-brick-list-interface` | **Date**: January 4, 2026 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/002-brick-list-interface/spec.md`

## Summary

This feature implements an interactive "Bricks in Set" list interface for tracking Lego brick collection progress. Users can view brick details (preview images, IDs, names), manually track collection progress through click interactions (left-click to increment, right-click to decrement counters), mark bricks as manually found via checkboxes, and receive real-time visual feedback when bricks are detected in video frames. The interface will dynamically reorder detected bricks to the top of the list and highlight completed bricks in green.

**Technical Approach**: Extend existing PyQt6 GUI (SetInfoPanel) to transform the current basic display into an interactive QListWidget with custom list items. Each item will display brick preview images, interactive checkboxes, detection indicators, counters with click handling, and completion highlighting. The implementation will integrate with existing LegoSet, Brick, and ProgressTracker models while adding support for detection event updates from the vision pipeline.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: PyQt6 (GUI framework), Pillow (image handling for brick previews), existing YOLO detection engine  
**Storage**: In-memory state with existing CSV-based set loading; preview images stored as PNG files in data directory  
**Testing**: pytest for unit tests of models and list logic; manual integration testing for GUI interactions  
**Target Platform**: Desktop (Windows primary, cross-platform with PyQt6)  
**Project Type**: Single desktop application with GUI  
**Performance Goals**: <500ms UI update latency for detection feedback; smooth list rendering for 200+ brick types; maintain 30fps video preview during detection  
**Constraints**: Preview images must fit within compact line height; list updates must not block video processing thread; detection updates arrive at video frame rate (up to 30fps)  
**Scale/Scope**: Support sets with up to 200 unique brick types; handle up to 1000 total brick instances; support simultaneous detection of 10+ bricks per frame

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Does the plan ensure accurate spotting of Lego bricks in piles?**  
Yes - The list interface displays detection feedback from the existing YOLO-based detection engine, which already performs accurate brick identification. The interface enhances visibility of detected bricks through visual indicators and dynamic reordering.

✅ **Is the detection based on predefined set pieces?**  
Yes - The list displays only bricks from the loaded set (via CSV), and the detection scope checkbox allows filtering to set-only detection. The feature builds on existing set-based configuration.

✅ **Does it prevent re-detection after pickup?**  
Yes - The manual marking checkbox allows users to exclude physically picked bricks from detection. Additionally, the counter system tracks collected quantities, and completed bricks (green highlight) provide clear visual indication of collection status.

✅ **Is it designed for real-time video input from Kinect or webcam?**  
Yes - The interface integrates with existing video processing pipeline and updates detection indicators in real-time as frames are processed. The design explicitly targets <500ms update latency for responsive feedback.

✅ **Does it account for various lighting and angles?**  
Yes - The interface displays detection results from the YOLO model which already handles various conditions. The visual feedback system works independently of lighting/angle, simply reflecting detection engine output.

**Status**: ✅ All constitution principles satisfied. No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/002-brick-list-interface/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output - Research findings
├── data-model.md        # Phase 1 output - Data structures and state management
├── quickstart.md        # Phase 1 output - Developer quickstart guide
└── contracts/           # Phase 1 output - Component interfaces
    └── brick_list_widget.py  # Interface contract for the brick list component
```

### Source Code (repository root)

```text
src/
├── models/                      # Existing - Data models
│   ├── brick.py                # Extend: Add manual_marked flag, detection_status
│   ├── lego_set.py             # Extend: Add methods for detection updates
│   └── video_source.py         # Existing - Unchanged
├── gui/                         # Existing - GUI components
│   ├── set_info_panel.py       # MAJOR REFACTOR: Transform into brick list interface
│   ├── brick_list_widget.py    # NEW: Custom QListWidget for brick display
│   ├── brick_list_item.py      # NEW: Custom widget for individual brick entries
│   ├── main_window.py          # Extend: Wire detection updates to list
│   ├── detection_panel.py      # Existing - Unchanged
│   └── video_display.py        # Existing - Unchanged
├── vision/                      # Existing - Detection engine
│   ├── detection_engine.py     # Extend: Emit brick detection events
│   └── detection_state.py      # Existing - Track detection state
└── utils/                       # Existing - Utilities
    ├── progress_tracker.py     # Extend: Track manual vs detected finds
    └── image_cache.py          # NEW: Cache brick preview images

tests/
├── unit/
│   ├── test_brick_model.py     # NEW: Test extended Brick model
│   ├── test_brick_list_logic.py # NEW: Test counter/sorting/highlighting logic
│   └── test_image_cache.py     # NEW: Test image caching
└── integration/
    └── test_brick_list_integration.py  # NEW: Test GUI integration

data/
├── brick_images/               # NEW: Directory for brick preview images
│   └── [part_number].png      # Preview images keyed by part number
└── sample_3005.csv             # Existing - Set data
```

**Structure Decision**: Using Option 1 (Single Project) as this is a desktop application with integrated GUI and detection engine. The existing structure with src/, gui/, models/, and vision/ directories is maintained. New components are added within gui/ for the brick list widget and item, while existing models are extended with new properties and methods.

## Complexity Tracking

> No violations - Constitution Check passed all principles.
