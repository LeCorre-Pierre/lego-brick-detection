# Tasks: Model Selection — Improve Lego Detection Quality

**Input**: spec.md, plan.md in specs/001-yolov7-model-selection/
**Prerequisites**: research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`
- [P]: Parallel-safe (different files, no dependencies)
- [Story]: US1, US2, US3 (only in story phases)
- Include exact file paths

---

## Phase 1: Setup (Shared Infrastructure)
**Purpose**: Prepare evaluation datasets and reporting scaffolding
- [X] T001 Create validation folders for Lego/non‑Lego in data/validation/{lego,non_lego}
- [ ] T002 [P] Add metrics report schema description in specs/001-yolov7-model-selection/contracts/model_evaluation.md
- [ ] T003 [P] Add inventory classes mapping stub in specs/001-yolov7-model-selection/contracts/detection_tuning.md

---

## Phase 2: Foundational (Blocking Prerequisites)
**Purpose**: Core evaluation/tuning infrastructure before user stories
- [X] T004 Scaffold evaluation harness script in tests/perf/eval_model.py to emit logs/metrics.json
- [X] T005 [P] Define metrics loader/report generator in tests/perf/report_metrics.py
- [X] T006 [P] Ensure QualityConfig persistence in src/utils/config_manager.py (fields: confidence, nms_iou, min_size_px, aspect_ratio_range)
- [X] T007 [P] Add runtime hooks to apply QualityConfig in src/vision/brick_detector.py

**Checkpoint**: Foundation ready — can evaluate baseline and apply tuning in app

---

## Phase 3: User Story 1 — Reduce false positives (Priority: P1) 🎯 MVP
**Goal**: Achieve FPR ≤ 5% on non‑Lego validation
**Independent Test**: Run tests/perf/eval_model.py on data/validation/non_lego and verify FPR threshold

### Tests for User Story 1
- [ ] T008 [P] [US1] Add non‑Lego evaluation case in tests/perf/eval_model.py
- [ ] T009 [P] [US1] Add assertion for FPR ≤ 5% in tests/perf/report_metrics.py

### Implementation for User Story 1
- [ ] T010 [P] [US1] Add threshold controls surface in src/gui/settings_dialog.py (confidence, NMS)
- [ ] T011 [US1] Wire detector to apply thresholds and reduce spurious detections in src/vision/brick_detector.py
- [ ] T012 [US1] Log evaluation summary to logs/metrics.json and display brief indicators in src/gui/main_window.py

**Checkpoint**: FPR ≤ 5% on non‑Lego validation; indicators visible in app

---

## Phase 4: User Story 2 — Per‑class detection from inventory (Priority: P2)
**Goal**: Detect and label classes aligned to full set inventory
**Independent Test**: Evaluate per‑class precision ≥ 80% and recall ≥ 70%

### Tests for User Story 2
- [ ] T013 [P] [US2] Add per‑class evaluation suite in tests/perf/eval_model.py (lego dataset)
- [ ] T014 [P] [US2] Add per‑class metrics summary in tests/perf/report_metrics.py

### Implementation for User Story 2
- [ ] T015 [P] [US2] Implement inventory→label mapping utility in src/utils/inventory_mapper.py
- [ ] T016 [US2] Integrate mapped class labels into detector outputs in src/vision/brick_detector.py
- [ ] T017 [US2] Display class labels in overlays and UI list in src/gui/video_display.py

**Checkpoint**: Per‑class metrics meet thresholds and labels appear in UI

---

## Phase 5: User Story 3 — Configurable filtering (Priority: P3)
**Goal**: User can tune size/aspect/color consistency filters; settings persist
**Independent Test**: Adjust filters and verify predictable metric shifts; restart preserves settings

### Tests for User Story 3
- [ ] T018 [P] [US3] Add integration test for settings persistence in tests/integration/test_settings_persistence.py
- [ ] T019 [P] [US3] Add perf test to verify precision/recall response to threshold changes in tests/perf/test_tuning_effects.py

### Implementation for User Story 3
- [ ] T020 [P] [US3] Extend settings dialog for size/aspect/color options in src/gui/settings_dialog.py
- [ ] T021 [US3] Apply filters in post‑processing step in src/vision/brick_detector.py
- [ ] T022 [US3] Persist/load filters in src/utils/config_manager.py

**Checkpoint**: Settings persist and tuning demonstrates expected trade‑offs

---

## Phase 6: Polish & Cross‑Cutting Concerns
**Purpose**: Documentation, performance traces, and hardening
- [ ] T023 [P] Update research with evaluation outcomes in specs/001-yolov7-model-selection/research.md
- [ ] T024 [P] Add consolidated metrics CSV in logs/metrics_report.csv via tests/perf/report_metrics.py
- [ ] T025 Validate quickstart scenarios and record results in specs/001-yolov7-model-selection/quickstart.md

---

## Dependencies & Execution Order
- Setup → Foundational → User Stories → Polish
- Story order by priority: US1 (P1) → US2 (P2) → US3 (P3)
- Tests per story should fail before implementation tasks in the same story

## User Story Dependency Graph
- US1 has no story prerequisites (quality baseline)
- US2 depends on Foundational; independent of US1 but may reuse its controls
- US3 depends on Foundational; can run after US1/US2 for tuning persistence

## Parallel Execution Examples
- US1: T008 and T009 in parallel; T010 alongside T011 wiring
- US2: T013 and T014 in parallel; T015 mapper can proceed while T016 integration is prepared
- US3: T018 and T019 in parallel; T020 can be built while T021/T022 hooks are implemented

## Implementation Strategy
- MVP first: Complete Setup + Foundational + US1, validate FPR ≤ 5%
- Incremental: Add US2 per‑class labeling; then US3 tuning persistence
- At each story checkpoint, run evaluation and update quickstart with outcomes
