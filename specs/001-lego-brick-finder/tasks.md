---

description: "Task list for Lego Brick Finder Application implementation"
---

# Tasks: Lego Brick Finder Application

**Input**: Design documents from `/specs/001-lego-brick-finder/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No test tasks included (TDD approach not requested)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/` at repository root
- Paths shown assume single project structure

## Dependencies & Parallel Execution

**Story Dependencies**:
- US1 (Load Lego Set) → US3 (Real-Time Detection)
- US2 (Configure Video) → US3 (Real-Time Detection)
- US3 (Real-Time Detection) → US4 (Mark Bricks)
- US5 (Settings) can run in parallel with other stories

**Parallel Opportunities**:
- Model/entity creation tasks across stories
- GUI component implementation
- Independent utility functions

**MVP Scope**: US1 + US2 + US3 + US4 (core detection workflow)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create Python package structure in src/
- [x] T002 Install PyQt6, OpenCV, and NumPy dependencies
- [x] T003 [P] Configure Python project with pyproject.toml
- [x] T004 [P] Setup basic logging configuration in src/utils/logger.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create base data models (LegoSet, Brick, DetectionResult, VideoSource) in src/models/
- [x] T006 [P] Implement SetLoader class for CSV parsing in src/loaders/set_loader.py
- [x] T007 [P] Setup basic PyQt6 application framework in src/gui/main_window.py
- [x] T008 [P] Create video processing utilities in src/vision/video_utils.py
- [x] T009 [P] Implement basic OpenCV-QT integration in src/gui/video_display.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Load Lego Set (Priority: P1) 🎯 MVP

**Goal**: Enable users to load Lego set data from Rebrickable CSV files and display set information

**Independent Test**: Load a CSV file and verify set name, brick count, and brick list are displayed correctly

### Implementation for User Story 1

- [x] T010 [P] [US1] Implement LegoSet and Brick model classes in src/models/lego_set.py and src/models/brick.py
- [x] T011 [US1] Complete SetLoader CSV parsing functionality in src/loaders/set_loader.py
- [x] T012 [US1] Create set information display panel in src/gui/set_info_panel.py
- [x] T013 [US1] Add file dialog and load menu action in src/gui/main_window.py
- [x] T014 [US1] Integrate set loading with UI updates and error handling

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Configure Video Source (Priority: P1) 🎯 MVP

**Goal**: Allow users to select and configure webcam or Kinect video sources with stream testing

**Independent Test**: Select a camera device, test the stream, and verify video preview works

### Implementation for User Story 2

- [x] T015 [P] [US2] Implement VideoSource model in src/models/video_source.py
- [x] T016 [US2] Create camera device scanning functionality in src/vision/camera_scanner.py
- [x] T017 [US2] Build camera configuration dialog in src/gui/camera_config_dialog.py
- [x] T018 [US2] Implement video stream testing in src/vision/video_tester.py
- [x] T019 [US2] Integrate camera configuration with main window menu

**Checkpoint**: At this point, User Story 2 should be fully functional and testable independently

---

## Phase 5: User Story 3 - Real-Time Brick Detection (Priority: P1) 🎯 MVP

**Goal**: Process video stream in real-time to detect and highlight Lego bricks from the loaded set

**Independent Test**: Start detection with a loaded set and camera, verify bricks are highlighted with bounding boxes

### Implementation for User Story 3

- [x] T020 [P] [US3] Implement DetectionResult model in src/models/detection_result.py
- [x] T021 [US3] Create BrickDetector core detection engine in src/vision/brick_detector.py
- [x] T022 [US3] Implement contour detection and shape analysis in src/vision/contour_analyzer.py
- [x] T023 [US3] Add color matching and brick identification in src/vision/color_matcher.py
- [x] T024 [US3] Integrate detection with video display overlays in src/gui/video_display.py
- [x] T025 [US3] Connect detection pipeline with main window controls

**Checkpoint**: At this point, User Story 3 should be fully functional and testable independently

---

## Phase 6: User Story 4 - Mark Bricks as Picked (Priority: P1) 🎯 MVP

**Goal**: Enable users to easily mark detected bricks as found by clicking on them

**Independent Test**: Detect bricks, click on bounding boxes, verify bricks are marked as found and no longer detected

### Implementation for User Story 4

- [x] T026 [US4] Implement click detection on video display in src/gui/video_display.py
- [x] T027 [US4] Add brick marking logic in src/models/lego_set.py
- [x] T028 [US4] Create progress tracking system in src/utils/progress_tracker.py
- [x] T029 [US4] Update set info panel with found brick indicators in src/gui/set_info_panel.py
- [x] T030 [US4] Integrate marking with detection pipeline to prevent re-detection

**Checkpoint**: At this point, User Story 4 should be fully functional and testable independently

---

## Phase 7: User Story 5 - Adjust Detection Settings (Priority: P2)

**Goal**: Provide configurable detection parameters for different lighting and angle conditions

**Independent Test**: Open settings dialog, adjust parameters, verify detection adapts to new settings

### Implementation for User Story 5

- [ ] T031 [P] [US5] Create DetectionParams configuration structure in src/models/detection_params.py
- [ ] T032 [US5] Build settings dialog UI in src/gui/settings_dialog.py
- [ ] T033 [US5] Implement parameter persistence in src/utils/config_manager.py
- [ ] T034 [US5] Connect settings to detection engine in src/vision/brick_detector.py
- [ ] T035 [US5] Add settings menu integration in src/gui/main_window.py

**Checkpoint**: At this point, User Story 5 should be fully functional and testable independently

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Final enhancements, performance optimization, and quality improvements

- [ ] T036 Add application icon and branding
- [ ] T037 Implement keyboard shortcuts for common actions
- [ ] T038 Add help documentation and tooltips
- [ ] T039 Performance optimization for real-time detection
- [ ] T040 Add error recovery and graceful failure handling
- [ ] T041 Create user preferences persistence
- [ ] T042 Add logging and diagnostics
- [ ] T043 Final UI/UX polish and accessibility improvements

**Final Checkpoint**: Application ready for release with all features functional