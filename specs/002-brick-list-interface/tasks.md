# Tasks: Bricks in Set List Interface

**Feature Branch**: `002-brick-list-interface`  
**Input**: Design documents from `/specs/002-brick-list-interface/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: No specific test requirements in specification - tests are optional

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for brick list interface

- [ ] T001 Create data/brick_images/ directory for brick preview images
- [ ] T002 [P] Create tests/unit/ directory structure if not exists
- [ ] T003 [P] Create tests/integration/ directory structure if not exists

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Extend Brick model with manually_marked, detected_in_current_frame, last_detected_timestamp, original_list_position properties in src/models/brick.py
- [ ] T005 Add mark_as_manually_found(), unmark_manually_found() methods to Brick model in src/models/brick.py
- [ ] T006 Add set_detected(timestamp), clear_detected(), should_be_detected() methods to Brick model in src/models/brick.py
- [ ] T007 [P] Extend LegoSet model with get_bricks_by_detection_status() method in src/models/lego_set.py
- [ ] T008 [P] Add update_detection_status(detected_part_numbers, timestamp) method to LegoSet model in src/models/lego_set.py
- [ ] T009 [P] Add get_detectable_bricks() method to LegoSet model in src/models/lego_set.py
- [ ] T010 [P] Create ImageCache class with LRU caching in src/utils/image_cache.py
- [ ] T011 [P] Implement get_image(part_number), _load_image(), _get_placeholder() methods in src/utils/image_cache.py
- [ ] T012 [P] Create unit tests for Brick model extensions in tests/unit/test_brick_model.py
- [ ] T013 [P] Create unit tests for ImageCache in tests/unit/test_image_cache.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 4 - Brick Identification (Priority: P1) 🎯 MVP Foundation

**Goal**: Display brick list with preview images, IDs, names, and required quantities for easy identification

**Why First**: This is the foundational display layer that all other user stories build upon. Users need to see and identify bricks before they can interact with counters, checkboxes, or detection feedback.

**Independent Test**: Load a set (e.g., rebrickable_parts_60122-1-volcano-crawler.csv) and verify each brick displays preview image, ID, name, and required quantity in a consistent layout

### Implementation for User Story 4

- [ ] T014 [P] [US4] Create BrickListItem widget class in src/gui/brick_list_item.py
- [ ] T015 [US4] Implement BrickListItem layout with preview image (QLabel 48x48) in src/gui/brick_list_item.py
- [ ] T016 [US4] Add brick ID label (QLabel) to BrickListItem layout in src/gui/brick_list_item.py
- [ ] T017 [US4] Add brick name label (QLabel) with text overflow handling to BrickListItem layout in src/gui/brick_list_item.py
- [ ] T018 [US4] Add required quantity label to BrickListItem layout in src/gui/brick_list_item.py
- [ ] T019 [US4] Implement set_brick(brick) method in BrickListItem in src/gui/brick_list_item.py
- [ ] T020 [US4] Add image loading from ImageCache in BrickListItem in src/gui/brick_list_item.py
- [ ] T021 [P] [US4] Create BrickListWidget class (QListWidget subclass) in src/gui/brick_list_widget.py
- [ ] T022 [US4] Create internal BrickListState class for state management in src/gui/brick_list_widget.py
- [ ] T023 [US4] Implement load_set(lego_set) method to populate list in src/gui/brick_list_widget.py
- [ ] T024 [US4] Implement _add_brick_item(brick) helper method in src/gui/brick_list_widget.py
- [ ] T025 [US4] Implement clear_list() method in src/gui/brick_list_widget.py
- [ ] T026 [US4] Add consistent styling and spacing for list items in src/gui/brick_list_widget.py

**Checkpoint**: User Story 4 complete - Users can view and identify all bricks in the loaded set

---

## Phase 4: User Story 1 - Track Brick Collection Progress (Priority: P1) 🎯 MVP Core

**Goal**: Enable counter interaction (left-click increment, right-click decrement) and green highlighting when complete

**Why Second**: This provides the core tracking functionality that makes the list interactive and useful for physical brick sorting.

**Independent Test**: Load a set, left-click brick entries to increment counters, right-click to decrement, verify green highlight appears when count reaches required quantity

### Implementation for User Story 1

- [ ] T027 [US1] Add counter display label (format: "X/Y") to BrickListItem in src/gui/brick_list_item.py
- [ ] T028 [US1] Override mousePressEvent in BrickListItem for left/right click handling in src/gui/brick_list_item.py
- [ ] T029 [US1] Add counter_incremented signal to BrickListItem in src/gui/brick_list_item.py
- [ ] T030 [US1] Add counter_decremented signal to BrickListItem in src/gui/brick_list_item.py
- [ ] T031 [US1] Implement update_counter_display(found_count, required_count) method in src/gui/brick_list_item.py
- [ ] T032 [US1] Implement _apply_completion_highlight() method for green background in src/gui/brick_list_item.py
- [ ] T033 [US1] Implement _remove_completion_highlight() method in src/gui/brick_list_item.py
- [ ] T034 [US1] Add brick_counter_changed signal to BrickListWidget in src/gui/brick_list_widget.py
- [ ] T035 [US1] Implement increment_brick_counter(part_number) method in src/gui/brick_list_widget.py
- [ ] T036 [US1] Implement decrement_brick_counter(part_number) method in src/gui/brick_list_widget.py
- [ ] T037 [US1] Connect BrickListItem counter signals to BrickListWidget handlers in src/gui/brick_list_widget.py
- [ ] T038 [US1] Add counter validation (min 0, max required quantity) in src/gui/brick_list_widget.py
- [ ] T039 [US1] Update Brick model found_quantity when counter changes in src/gui/brick_list_widget.py
- [ ] T040 [US1] Implement get_current_progress() method returning (found, total) in src/gui/brick_list_widget.py
- [ ] T041 [P] [US1] Create unit tests for counter logic in tests/unit/test_brick_list_logic.py

**Checkpoint**: User Story 1 complete - Users can manually track brick collection progress with visual feedback

---

## Phase 5: User Story 2 - Manual Brick Marking (Priority: P2)

**Goal**: Add checkbox to manually mark bricks as found and exclude them from detection

**Why Third**: This enhances the tracking workflow but is not essential for basic functionality (P2 priority).

**Independent Test**: Check/uncheck brick checkboxes and verify that manually marked bricks are visually distinct and excluded from detection processing

### Implementation for User Story 2

- [ ] T042 [P] [US2] Add checkbox (QCheckBox) to BrickListItem layout in src/gui/brick_list_item.py
- [ ] T043 [US2] Add manually_marked_changed signal to BrickListItem in src/gui/brick_list_item.py
- [ ] T044 [US2] Connect checkbox toggled signal to manually_marked_changed in src/gui/brick_list_item.py
- [ ] T045 [US2] Implement set_manual_marking(is_marked) method in src/gui/brick_list_item.py
- [ ] T046 [US2] Add visual styling for manually marked bricks in src/gui/brick_list_item.py
- [ ] T047 [US2] Add brick_manually_marked signal to BrickListWidget in src/gui/brick_list_widget.py
- [ ] T048 [US2] Implement _on_manual_marked(part_number, is_marked) handler in src/gui/brick_list_widget.py
- [ ] T049 [US2] Update Brick.manually_marked property when checkbox changes in src/gui/brick_list_widget.py
- [ ] T050 [US2] Connect BrickListItem manually_marked signal to BrickListWidget handler in src/gui/brick_list_widget.py

**Checkpoint**: User Story 2 complete - Users can manually mark bricks and exclude them from detection

---

## Phase 6: User Story 3 - Visual Detection Feedback (Priority: P1) 🎯 MVP Polish

**Goal**: Display detection pictogram and dynamically reorder list with detected bricks at top

**Why Fourth**: This integrates the AI detection system with the list interface, providing real-time feedback.

**Independent Test**: Run detection on video frames, verify detected bricks show icon and move to top of list, then verify they return to original position when no longer detected

### Implementation for User Story 3

- [ ] T051 [P] [US3] Add detection icon label (QLabel with icon) to BrickListItem layout in src/gui/brick_list_item.py
- [ ] T052 [US3] Implement set_detection_status(is_detected) method in src/gui/brick_list_item.py
- [ ] T053 [US3] Add detection icon visibility toggle logic in src/gui/brick_list_item.py
- [ ] T054 [US3] Initialize QTimer for detection update batching (100ms) in src/gui/brick_list_widget.py
- [ ] T055 [US3] Implement update_detection_status(detected_part_numbers) method in src/gui/brick_list_widget.py
- [ ] T056 [US3] Implement _apply_detection_updates() method for batched updates in src/gui/brick_list_widget.py
- [ ] T057 [US3] Implement _reorder_list() method to move detected bricks to top in src/gui/brick_list_widget.py
- [ ] T058 [US3] Add setUpdatesEnabled(False/True) to prevent flicker during reorder in src/gui/brick_list_widget.py
- [ ] T059 [US3] Implement _update_detection_icons() helper method in src/gui/brick_list_widget.py
- [ ] T060 [US3] Store and restore original list positions in BrickListState in src/gui/brick_list_widget.py
- [ ] T061 [US3] Add frame_processed signal to DetectionEngine in src/vision/detection_engine.py
- [ ] T062 [US3] Emit detected_part_numbers set after frame processing in src/vision/detection_engine.py
- [ ] T063 [US3] Connect DetectionEngine.frame_processed to BrickListWidget.update_detection_status in src/gui/main_window.py

**Checkpoint**: User Story 3 complete - Users receive real-time visual feedback for detected bricks

---

## Phase 7: Integration & Refactoring

**Purpose**: Integrate BrickListWidget into existing SetInfoPanel and wire all connections

- [ ] T064 Replace existing brick display in SetInfoPanel with BrickListWidget in src/gui/set_info_panel.py
- [ ] T065 Update SetInfoPanel.load_set() to call brick_list_widget.load_set() in src/gui/set_info_panel.py
- [ ] T066 Connect BrickListWidget.brick_counter_changed to progress update in src/gui/set_info_panel.py
- [ ] T067 Connect BrickListWidget.brick_manually_marked to existing handlers in src/gui/set_info_panel.py
- [ ] T068 Update ProgressTracker to track manual vs detected finds in src/utils/progress_tracker.py
- [ ] T069 Verify detection scope filtering respects manually marked bricks in src/gui/set_info_panel.py

---

## Phase 8: Testing & Polish

**Purpose**: Comprehensive testing and final refinements

- [ ] T070 [P] Create integration tests for brick list with detection in tests/integration/test_brick_list_integration.py
- [ ] T071 [P] Test with large set (rebrickable_parts_60122-1-volcano-crawler.csv, 140+ bricks)
- [ ] T072 [P] Test counter increment/decrement edge cases (at 0, at max)
- [ ] T073 [P] Test right-click behavior and context menu suppression
- [ ] T074 [P] Test detection update batching and performance
- [ ] T075 [P] Test list reordering smoothness and flicker prevention
- [ ] T076 [P] Test image loading with missing images (verify placeholders)
- [ ] T077 [P] Test layout with very long brick names (verify text truncation)
- [ ] T078 [P] Test manual marking interaction with detection (manual marking precedence)
- [ ] T079 Add tooltips for detection icon, checkbox, and counter in src/gui/brick_list_item.py
- [ ] T080 Fine-tune colors, fonts, and spacing for readability in src/gui/brick_list_item.py
- [ ] T081 Add logging for key operations (load set, counter changes, detection updates) in src/gui/brick_list_widget.py
- [ ] T082 [P] Performance test with 200+ brick set (verify smooth scrolling)
- [ ] T083 [P] Memory profiling (verify image cache stays within bounds)
- [ ] T084 [P] Verify detection latency < 500ms from frame to UI update

---

## Dependencies Between User Stories

```
┌──────────────────────────────────────────────────────┐
│ Phase 2: Foundational (T004-T013)                   │
│ - Brick model extensions                             │
│ - LegoSet model extensions                           │
│ - ImageCache implementation                          │
└──────────┬───────────────────────────────────────────┘
           │ (BLOCKING - must complete first)
           │
    ┌──────▼──────────────────────────┐
    │ US4: Brick Identification (T014-T026) │ ← START HERE (MVP Foundation)
    │ Priority: P1                     │
    │ - BrickListItem display         │
    │ - BrickListWidget container     │
    │ - Preview images, IDs, names    │
    └──────┬───────────────────────────┘
           │ (Foundation for all other stories)
           │
    ┌──────▼──────────────────────────┐
    │ US1: Track Progress (T027-T041)      │ ← MVP Core Functionality
    │ Priority: P1                     │
    │ - Counter interaction            │
    │ - Green highlighting             │
    └──────┬───────────────────────────┘
           │
    ┌──────▼──────────────────────────┐
    │ US2: Manual Marking (T042-T050) │
    │ Priority: P2                     │
    │ - Checkbox for manual found     │
    │ - Exclude from detection        │
    └──────┬───────────────────────────┘
           │
    ┌──────▼──────────────────────────┐
    │ US3: Detection Feedback (T051-T063)│ ← MVP Polish
    │ Priority: P1                     │
    │ - Detection pictograms           │
    │ - Dynamic list reordering        │
    └──────┬───────────────────────────┘
           │
    ┌──────▼──────────────────────────┐
    │ Integration & Testing (T064-T084) │
    │ - Wire all components            │
    │ - Comprehensive testing          │
    └──────────────────────────────────┘
```

**Note**: User Stories 1, 2, and 3 depend on US4 being complete, but can proceed in parallel after US4 if resources allow.

---

## Parallel Execution Examples

### After Phase 2 (Foundational) completes:

**Parallel Group A** - User Story 4 (Foundation)
- T014-T026 (All US4 tasks - single developer focus)

### After User Story 4 completes:

**Parallel Group B** - Core Features (if multiple developers available)
- Developer 1: T027-T041 (User Story 1 - Track Progress)
- Developer 2: T042-T050 (User Story 2 - Manual Marking)

### After US1 and US2 complete:

**Parallel Group C** - Detection Integration
- T051-T063 (User Story 3 - Detection Feedback)

### During Testing Phase:

**Parallel Group D** - All testing tasks can run simultaneously
- T070-T084 (Multiple testers/developers)

---

## Implementation Strategy

### MVP Delivery Approach

**MVP Phase 1** (Minimal Viable Product - ~60% of tasks):
- Phase 2: Foundational (T004-T013)
- US4: Brick Identification (T014-T026)
- US1: Track Progress (T027-T041)

**Deliverable**: Users can view bricks and manually track collection progress  
**Value**: Immediate utility as a digital checklist

**MVP Phase 2** (Enhanced - ~85% of tasks):
- Add US3: Detection Feedback (T051-T063)
- Integration (T064-T069)

**Deliverable**: Full AI-powered detection with list interaction  
**Value**: Complete feature as specified

**Polish Phase** (Complete - 100% of tasks):
- Add US2: Manual Marking (T042-T050)
- Complete testing (T070-T084)

**Deliverable**: Production-ready with all edge cases handled  
**Value**: Robust, polished user experience

---

## Task Summary

| Phase | Task Count | Parallelizable | Est. Hours |
|-------|------------|----------------|------------|
| Phase 1: Setup | 3 | 2 | 0.5 |
| Phase 2: Foundational | 10 | 6 | 4-6 |
| Phase 3: US4 (P1) | 13 | 2 | 5-7 |
| Phase 4: US1 (P1) | 15 | 1 | 5-7 |
| Phase 5: US2 (P2) | 9 | 1 | 3-4 |
| Phase 6: US3 (P1) | 13 | 1 | 5-7 |
| Phase 7: Integration | 6 | 0 | 2-3 |
| Phase 8: Testing | 15 | 13 | 3-5 |
| **Total** | **84 tasks** | **26 parallel** | **27-39 hours** |

**Estimated Timeline**: 4-6 days for single developer, 2-3 days with 2-3 developers (parallel execution)

---

## Success Criteria Verification

Upon completion of all tasks, verify:

- ✅ **SC-001**: Users can identify any brick in a loaded set within 3 seconds (US4)
- ✅ **SC-002**: Users can track collection progress by incrementing/decrementing counters (US1)
- ✅ **SC-003**: Detected bricks appear at top of list within 500ms (US3)
- ✅ **SC-004**: Visual indicators clearly distinguish manual marking from detection (US2, US3)
- ✅ **SC-005**: Users can complete inventory without help documentation (all US)
- ✅ **SC-006**: List remains responsive with 100+ brick types (Testing)
- ✅ **SC-007**: Users report 40% efficiency improvement (User acceptance testing)

---

**Generated**: January 4, 2026  
**Ready for Implementation**: ✅ All 84 tasks defined with clear file paths and dependencies
