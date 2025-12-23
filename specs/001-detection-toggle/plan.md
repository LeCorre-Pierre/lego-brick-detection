# Implementation Plan: Real-Time YOLOv8 Brick Detection Toggle

**Branch**: `001-detection-toggle` | **Date**: December 23, 2025 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-detection-toggle/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a toggle mechanism to enable/disable real-time YOLOv8 brick detection on camera preview. Model loads asynchronously in background thread on startup (non-blocking UI). Detection button disabled until model ready. When enabled, renders bounding boxes and brick labels on each frame. When disabled, shows camera preview only. Model persists in memory for responsive (<100ms) toggling. Key technical approach: background threading for model loading, frame processing queue for detection, thread-safe state management for toggle control.

## Technical Context

**Language/Version**: Python 3.11+ (matches existing project)  
**Primary Dependencies**: YOLOv8 (ultralytics), PyQt6, OpenCV (cv2), threading (stdlib), numpy  
**Storage**: File-based model loading (models/ directory); no persistent storage needed  
**Testing**: pytest (unit tests), manual integration tests with camera  
**Target Platform**: Desktop (Windows/Linux/macOS with webcam or Kinect)  
**Project Type**: Single desktop application (existing structure)  
**Performance Goals**: Model load <5s, detection toggle response <100ms, render 30fps+ with overlays, 95% detection accuracy  
**Constraints**: Non-blocking UI during model load, thread-safe detection state, model kept in memory for responsive toggle, graceful error handling for missing model  
**Scale/Scope**: Single feature (detection toggle) integrated into existing Lego Brick Inventory app; ~500-800 LOC for core implementation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ **Accurate Lego Brick Spotting**: YOLOv8 detection with bounding boxes enables accurate identification of target bricks in pile
- ✅ **Set-Based Brick Definition**: Detection uses set pieces from loaded Lego set as reference classes; labels show brick type from set
- ✅ **No Re-detection After Pickup**: Detection feature is user-controlled (toggle on/off); users disable detection after picking brick, preventing redundant detection
- ✅ **Real-Time Video Input**: Design uses live camera feed (webcam/Kinect) continuously; preview displays in real-time
- ✅ **Robust Environmental Detection**: YOLOv8 model handles various lighting/angles; trained on diverse brick images under different conditions
- ✅ **Focus on Simplicity**: Single toggle button for detection control; automatic model loading; clear feedback (button states); no manual configuration needed

**Constitution Gate Status**: ✅ **PASS** - Implementation aligns with all core principles

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

**Current Structure**: The project already follows Option 1 (single project) with clear separation:

```text
src/
├── gui/                    # PyQt6 UI components
│   ├── main_window.py      # Main application window (will add detection toggle UI)
│   ├── video_display.py    # Video preview widget (will add detection rendering)
│   └── ...
├── vision/                 # Computer vision modules
│   ├── camera_scanner.py
│   ├── color_matcher.py
│   ├── contour_analyzer.py
│   ├── video_utils.py      # Helper utilities
│   └── ...
├── models/                 # Data models
│   ├── brick.py
│   ├── lego_set.py
│   └── video_source.py
└── utils/                  # Utilities
    ├── config_manager.py
    ├── logger.py
    └── ...

models/                     # YOLOv8 model files (existing directory)
├── [yolov8-brick-model].pt # Model to be added

tests/                      # Test suite (will add detection tests)
```

**New Components for Detection Toggle**:
- `src/vision/detection_engine.py` - YOLOv8 wrapper, model loading, inference (NEW)
- `src/vision/detection_state.py` - Detection state enum and management (NEW)
- `src/gui/detection_panel.py` - Detection toggle button/slider UI component (NEW)
- Updates to `src/gui/main_window.py` - Integrate detection panel and control flow
- Updates to `src/gui/video_display.py` - Add bounding box/label rendering

**Structure Decision**: Extend existing single-project structure with new vision module (`detection_engine.py`) for YOLOv8 handling and new GUI component (`detection_panel.py`) for toggle control. Minimal disruption to existing code; clear separation of concerns.

## Complexity Tracking

No Constitution violations. Plan is straightforward and aligned with all core principles. No complexity exceptions required.

---

## Phase 0: Research (Unknowns Resolution)

**Status**: To be completed in next /speckit.plan execution

### Research Tasks
1. **YOLOv8 Model Loading Patterns**: Best practices for loading ultralytics YOLOv8 models, inference API, handling CUDA/CPU fallback
2. **PyQt6 Thread Safety**: Patterns for updating UI from worker threads, signal/slot mechanism for thread-safe state updates
3. **Real-Time Frame Processing**: Optimal queue/buffer strategy for camera → detection → display pipeline, frame synchronization
4. **Performance Benchmarking**: Expected inference time per frame, CUDA vs CPU performance, memory usage during model loading

**Output**: `research.md` with findings, rationale, and alternatives considered

---

## Phase 1: Design & Contracts

**Status**: To be completed in next /speckit.plan execution

### Deliverables
1. **data-model.md** - Detection state machine, bounding box structure, model configuration
2. **contracts/** - Function signatures for detection engine, UI components, threading interfaces
3. **quickstart.md** - Step-by-step implementation checklist

### Key Design Decisions Pending Research
- Queue-based or event-driven frame processing?
- Daemon thread or QThread for model loading?
- Confidence threshold for bounding box filtering?

**Output**: Design documents ready for implementation planning

---

## Next Steps

1. Run `/speckit.plan` to execute Phase 0 research tasks and generate findings
2. Review research.md for YOLOv8/threading patterns
3. Complete Phase 1 design documents
4. Proceed to `/speckit.tasks` for detailed implementation task breakdown
