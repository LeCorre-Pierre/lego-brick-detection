# Tasks: Real-Time YOLOv8 Brick Detection Toggle

**Input**: Design documents from `/specs/001-detection-toggle/`  
**Prerequisites**: plan.md (complete), spec.md (complete), research.md (in progress)  
**Branch**: `001-detection-toggle`

**Organization**: Tasks grouped by user story and phase. Each user story (US1-US4) is independently testable and deliverable. Parallel tasks marked with [P].

## Format Reference

- **[ID]**: Sequential task ID (T001, T002, etc.)
- **[P]**: Can run in parallel (different files, no blocking dependencies)
- **[Story]**: User story label (US1, US2, US3, US4)
- **Description**: Action with exact file path

---

## Phase 1: Setup & Foundation

**Purpose**: Project infrastructure, dependencies, and foundational components

- [X] T001 Install YOLOv8 dependency (ultralytics) in requirements.txt and verify import
  - **File**: `requirements.txt`, `src/vision/detection_engine.py`
  - **Acceptance**: `pip list | grep ultralytics` shows installed version; can run `from ultralytics import YOLO`

- [X] T002 Create detection state enum and management module `src/vision/detection_state.py`
  - **File**: `src/vision/detection_state.py`
  - **Acceptance**: Module exports `DetectionState` enum with states: OFF, LOADING, READY, ACTIVE, ERROR; includes thread-safe state getter/setter

- [X] T003 [P] Set up YOLOv8 detection engine wrapper in `src/vision/detection_engine.py` with stub methods
  - **File**: `src/vision/detection_engine.py`
  - **Acceptance**: Exports `YOLOv8Engine` class with methods: `load_model(path)`, `infer(frame)`, `get_detections()`, `unload_model()`; proper docstrings; no implementation yet

- [X] T004 [P] Create detection panel UI component `src/gui/detection_panel.py` with button placeholder
  - **File**: `src/gui/detection_panel.py`
  - **Acceptance**: Exports `DetectionPanel` QWidget with toggle button, status label; signals for state changes; button initially disabled

- [X] T005 Create logger configuration for detection module in `src/utils/logger.py`
  - **File**: `src/utils/logger.py`
  - **Acceptance**: Detection-specific logger instance available; logs to app log with detection prefix

---

## Phase 2: User Story 1 - Load Model in Background (Priority: P1)

**Goal**: Model loads asynchronously on startup without blocking UI; loading status displayed; button enabled when model ready

**Independent Test**: Launch app → verify camera preview starts immediately → verify "Loading model..." status → verify button enabled after load

- [X] T006 [US1] Implement YOLOv8 model loading in `src/vision/detection_engine.py` with file validation
  - **File**: `src/vision/detection_engine.py`
  - **Acceptance**: `load_model(model_path)` method loads model via ultralytics; validates file exists; handles missing files with exception; returns True on success

- [X] T007 [US1] Create model loader worker thread class in `src/vision/detection_engine.py`
  - **File**: `src/vision/detection_engine.py`
  - **Acceptance**: `ModelLoaderThread` (QThread subclass) loads model asynchronously; emits signals for progress, completion, error; proper cleanup on finish

- [X] T008 [US1] Integrate model loader into main window initialization in `src/gui/main_window.py`
  - **File**: `src/gui/main_window.py`
  - **Acceptance**: On app startup, background thread loads model; status label shows "Loading model..."; no UI freezing during load; detection button disabled during load

- [X] T009 [US1] Update detection panel button state on model load completion in `src/gui/detection_panel.py`
  - **File**: `src/gui/detection_panel.py`
  - **Acceptance**: Button state transitions from disabled (loading) to enabled (ready); label changes to "Start Detection"; button click handler connected

- [ ] T010 [US1] Add model load timeout and progress feedback in `src/gui/main_window.py`
  - **File**: `src/gui/main_window.py`
  - **Acceptance**: If model load takes >5 seconds, display progress percentage; prevent indefinite blocking; log timeout warnings; graceful degradation if load fails

- [ ] T011 [US1] Test model loading with mock YOLOv8 model in tests/test_detection_engine.py
  - **File**: `tests/test_detection_engine.py`
  - **Acceptance**: Unit test verifies model loads correctly; test verifies file validation error handling; test verifies thread cleanup; all tests pass

---

## Phase 3: User Story 2 - Toggle Detection On/Off (Priority: P1)

**Goal**: User clicks button to toggle detection; overlays appear when on, disappear when off; model stays in memory for instant response

**Independent Test**: Load app → enable detection → verify bounding boxes appear → disable detection → verify boxes disappear → re-enable → verify instant response

- [X] T012 [P] [US2] Implement YOLOv8 inference in `src/vision/detection_engine.py` with frame processing
  - **File**: `src/vision/detection_engine.py`
  - **Acceptance**: `infer(frame)` method processes frame; returns list of detections (bounding boxes, class labels, confidence); handles variable input sizes; runs synchronously

- [ ] T012 [P] [US2] Implement detection frame queue and worker thread in `src/vision/detection_engine.py`
  - **File**: `src/vision/detection_engine.py`
  - **Acceptance**: `DetectionWorkerThread` receives frames from queue; runs inference asynchronously; emits detections signal; gracefully handles queue stalls; proper thread sync

- [X] T013 [US2] Connect detection toggle button click to start/stop detection in `src/gui/detection_panel.py`
  - **File**: `src/gui/detection_panel.py`
  - **Acceptance**: Button click toggles `DetectionState` between ACTIVE and OFF; button label updates ("Stop Detection" ↔ "Start Detection"); signal emitted to main window

- [ ] T014 [US2] Integrate detection frame queue into video display in `src/gui/video_display.py`
  - **File**: `src/gui/video_display.py`
  - **Acceptance**: Video display widget sends frames to detection queue when detection is active; stops sending when detection is off; frame queue thread-safe

- [X] T015 [P] [US2] Implement bounding box rendering in `src/gui/video_display.py` with detection results
  - **File**: `src/gui/video_display.py`
  - **Acceptance**: Method `draw_detections(frame, detections)` overlays bounding boxes and labels on frame; handles variable number of detections; renders at frame rate

- [ ] T015 [P] [US2] Implement label text rendering for brick type in `src/gui/video_display.py`
  - **File**: `src/gui/video_display.py`
  - **Acceptance**: Bounding boxes include text labels (e.g., "2×4 Red Brick"); label format matches detected brick type; text readable at video resolution

- [X] T016 [US2] Connect detection results from engine to video display rendering in `src/gui/main_window.py`
  - **File**: `src/gui/main_window.py`
  - **Acceptance**: Detection engine signals emit detection results; main window receives results; video display updates to show bounding boxes; update rate matches frame rate

- [X] T017 [US2] Implement model persistence in memory after toggle off in `src/vision/detection_engine.py`
  - **File**: `src/vision/detection_engine.py`
  - **Acceptance**: Model remains loaded after detection is disabled; re-enabling detection does not reload model; inference response time <100ms on re-enable

- [ ] T018 [US2] Test detection toggle and rendering with sample video in tests/test_detection_toggle.py
  - **File**: `tests/test_detection_toggle.py`
  - **Acceptance**: Integration test toggles detection on/off; verifies overlay state changes; tests model persistence; timing tests verify <100ms response

---

## Phase 4: User Story 3 - Visual Feedback for Detection State (Priority: P2)

**Goal**: Button and status display clear detection state (loading, ready, active, inactive)

**Independent Test**: Observe button throughout app lifecycle; verify state matches expected transitions; users understand readiness at a glance

- [X] T019 [US3] Implement button visual states in `src/gui/detection_panel.py` (disabled, enabled, active)
  - **File**: `src/gui/detection_panel.py`
  - **Acceptance**: Button colors/styles differ by state: disabled (gray), enabled (blue), active (green); state matches `DetectionState` enum

- [X] T020 [P] [US3] Add state label updates to detection panel in `src/gui/detection_panel.py`
  - **File**: `src/gui/detection_panel.py`
  - **Acceptance**: Status label shows: "Loading model...", "Start Detection", "Stop Detection", or error message; label updates immediately on state change

- [X] T020 [P] [US3] Add status bar messages in main window for detection state in `src/gui/main_window.py`
  - **File**: `src/gui/main_window.py`
  - **Acceptance**: Status bar displays current detection state; updates when state changes; provides user feedback on readiness

- [ ] T021 [US3] Test visual state transitions in tests/test_detection_ui.py
  - **File**: `tests/test_detection_ui.py`
  - **Acceptance**: Unit tests verify button state transitions (loading → ready → active → inactive); label text matches state; color changes applied

---

## Phase 5: User Story 4 - Handle Model Loading Errors Gracefully (Priority: P2)

**Goal**: If model fails to load, error message displayed; button stays disabled; other features remain usable

**Independent Test**: Remove model file → launch app → verify error message → verify other features work (camera, screenshot save)

- [X] T022 [US4] Implement error handling in model loader in `src/vision/detection_engine.py`
  - **File**: `src/vision/detection_engine.py`
  - **Acceptance**: `load_model()` catches exceptions (file not found, corrupted, invalid format); emits error signal with message; state set to ERROR

- [X] T023 [US4] Display model loading error message in main window in `src/gui/main_window.py`
  - **File**: `src/gui/main_window.py`
  - **Acceptance**: Error message dialog displays on model load failure; message is user-friendly and actionable (e.g., "Model file not found in models/"); dialog doesn't block app

- [X] T024 [P] [US4] Update detection panel for error state in `src/gui/detection_panel.py`
  - **File**: `src/gui/detection_panel.py`
  - **Acceptance**: Button remains disabled when model fails to load; button label shows "Model Error"; button tooltip shows error details

- [ ] T024 [P] [US4] Verify app stability after model error in manual testing
  - **File**: N/A (manual test)
  - **Acceptance**: After model error, user can still: start/stop camera, save screenshots, load new set, configure camera; no crashes

- [ ] T025 [US4] Test error handling with missing model file in tests/test_error_handling.py
  - **File**: `tests/test_error_handling.py`
  - **Acceptance**: Unit test verifies error handling for missing file; test verifies app remains functional; test verifies error message quality

---

## Phase 6: Polish & Integration

**Purpose**: Final refinement, integration testing, performance validation

- [ ] T026 [P] Implement confidence threshold for bounding box filtering in `src/vision/detection_engine.py`
  - **File**: `src/vision/detection_engine.py`
  - **Acceptance**: Detections with confidence < 0.5 are filtered out; configurable threshold; improves visual clarity by removing low-confidence boxes

- [ ] T026 [P] Add bounding box color configuration in `src/gui/video_display.py`
  - **File**: `src/gui/video_display.py`
  - **Acceptance**: Bounding box color and thickness configurable; default color is bright (e.g., green) for visibility; thickness appropriate for video resolution

- [ ] T027 Update README.md with detection feature usage in `README.md`
  - **File**: `README.md`
  - **Acceptance**: README includes detection feature description, usage instructions (load model, toggle button), and performance expectations

- [ ] T028 [P] Add detection logging for debugging in `src/vision/detection_engine.py`
  - **File**: `src/vision/detection_engine.py`
  - **Acceptance**: Logs model load events, inference times, error conditions; logging level configurable; helps users debug issues

- [ ] T028 [P] Add debug mode toggle in main window for detection visualization
  - **File**: `src/gui/main_window.py`
  - **Acceptance**: Debug mode can be enabled via menu/shortcut; shows inference time overlay, detection count, FPS; helps users understand performance

- [ ] T029 Integration test: Full detection workflow in tests/test_integration.py
  - **File**: `tests/test_integration.py`
  - **Acceptance**: End-to-end test: app startup → model loads → camera starts → toggle detection on → overlays appear → toggle off → overlays disappear; all assertions pass

- [ ] T030 Performance validation: Verify <5s model load, <100ms toggle, 30fps+ rendering
  - **File**: tests/test_performance.py
  - **Acceptance**: Timing tests pass: model load <5s, toggle response <100ms, frame rate maintained at 30fps+ during detection; CPU/GPU usage reasonable

- [ ] T031 Code review and refactoring in src/vision/ and src/gui/
  - **File**: `src/vision/detection_engine.py`, `src/gui/detection_panel.py`, `src/gui/video_display.py`
  - **Acceptance**: Code follows project style guide; docstrings complete; no unused imports; type hints added; pylint/flake8 passing

- [ ] T032 Commit final changes and merge to main branch
  - **File**: All above
  - **Acceptance**: Branch `001-detection-toggle` ready for merge; all tests passing; PR description summarizes feature

---

## Dependency Graph

```
Phase 1 (Setup)
  ↓
Phase 2 (US1: Model Loading)
  ├─ T006-T010 (Parallel: T003, T004 from Phase 1)
  ↓
Phase 3 (US2: Toggle Detection)
  ├─ T012-T018 (Depends on Phase 2 completion)
  ↓
Phase 4 (US3: Visual Feedback)
  ├─ T019-T021 (Depends on Phase 3 UI integration)
  ↓
Phase 5 (US4: Error Handling)
  ├─ T022-T025 (Can run parallel to Phase 3, but phase-gated)
  ↓
Phase 6 (Polish & Integration)
  └─ T026-T032 (Final refinement after all stories complete)
```

## Parallel Execution Strategy

**Phase 2 Parallelization** (US1):
- T006 (engine loading), T007 (worker thread), T003 (stub engine) can start in parallel
- T008 (main window) and T004 (panel) can start in parallel
- Merge point: all Phase 1 tasks complete

**Phase 3 Parallelization** (US2):
- T012 (inference), T013 (toggle), T014 (frame queue) can start in parallel
- T015 (rendering) depends on T012 detections but can start after Phase 2
- Merge point: T014 and T015 complete (both needed for final integration)

**Phase 6 Parallelization** (Polish):
- T026 (confidence filter + colors) can run in parallel
- T028 (logging + debug mode) can run in parallel
- Merge point: before T029 integration test

## MVP Scope

**Minimum Viable Product (Phase 1-2)**: 
- Model loads in background ✓
- Detection toggles on/off ✓
- Bounding boxes render ✓
- Button shows loading/ready states ✓

**Achieves**: User Story 1 (load model) + User Story 2 (toggle detection) = Core feature value

**Can be deployed and tested independently of US3, US4, Phase 6**

---

## Implementation Order Recommendation

1. **Start parallel**: T001 (dependencies), T003 (engine stub), T004 (panel stub)
2. **Then T006-T010**: Complete US1 (model loading)
3. **Parallel US2**: T012-T018 (detection and rendering)
4. **Optional US3-4**: T019-T025 (polish and error handling) if time permits
5. **Final Phase 6**: Integration, testing, performance validation

**Estimated Timeline**:
- Phase 1: 1-2 hours
- Phase 2: 3-4 hours
- Phase 3: 4-5 hours
- Phase 4: 1-2 hours
- Phase 5: 2-3 hours
- Phase 6: 2-3 hours
- **Total**: ~15-20 hours of implementation + testing
