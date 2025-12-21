# Tasks: Plan d'architecture — Initialisation parallèle (Qt)
\n> Status: Closed on 2025-12-21. Phase 1 docs completed; remaining tasks not pursued per closure.\n

**Input**: spec.md, plan.md in specs/001-parallel-init-qt/
**Prerequisites**: Create research/data-model/quickstart docs; align contracts if needed

## Format: `[ID] [P?] [Story] Description`
- [P]: Parallel-safe (different files, no blocking deps)
- [Story]: US1, US2, US3, US4 (only in story phases)
- Include exact file paths

---

## Phase 1: Setup (Shared Infrastructure)
**Purpose**: Author missing design docs to ground implementation
- [X] T001 Create research baseline with perf targets and risks in specs/001-parallel-init-qt/research.md
- [X] T002 [P] Capture init-state entities (UIState, thread workers) in specs/001-parallel-init-qt/data-model.md
- [X] T003 [P] Write quickstart scenarios to validate startup/init flows in specs/001-parallel-init-qt/quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)
**Purpose**: Core threading/state/telemetry needed before any story
- [ ] T004 Add init timing probes (UI show, menu build, status bar) with logger in src/gui/main_window.py
- [ ] T005 [P] Centralize init state tracker (set/camera/model flags, errors) with signal-safe updates in src/gui/main_window.py
- [ ] T006 [P] Harden worker error/timeout handling for set and camera threads in src/loaders/set_loader.py and src/vision/camera_scanner.py
- [ ] T007 [P] Show loading/disabled states during init in src/gui/video_display.py

---

## Phase 3: User Story 1 - Démarrage rapide de l'application (Priority: P1) 🎯 MVP
**Goal**: UI appears in <2s and stays responsive while init runs
**Independent Test**: Launch app; window visible <2s and menus/buttons clickable instantly

### Tests for User Story 1
- [ ] T008 [P] [US1] Add pytest-qt startup timing test in tests/integration/test_ui_startup.py

### Implementation for User Story 1
- [ ] T009 [US1] Replace placeholder init logs with real duration reporting in src/gui/main_window.py
- [ ] T010 [P] [US1] Defer config load via QTimer and set initial widget enabled states on show in src/gui/main_window.py
- [ ] T011 [US1] Surface non-blocking startup progress text in status bar/video overlay in src/gui/video_display.py

**Checkpoint**: UI starts <2s; controls responsive during init

---

## Phase 4: User Story 2 - Chargement rapide du set Lego (Priority: P2)
**Goal**: Set loads <1s and brick list is responsive
**Independent Test**: Load sample CSV; brick list appears <1s and scrolls smoothly

### Tests for User Story 2
- [ ] T012 [P] [US2] Add integration timing test for set load in tests/integration/test_set_loading.py

### Implementation for User Story 2
- [ ] T013 [P] [US2] Optimize SetCSVLoader for fast parse/validation and early rejects in src/loaders/set_loader.py
- [ ] T014 [P] [US2] Refresh SetInfoPanel/brick list asynchronously on load in src/gui/main_window.py
- [ ] T015 [US2] Show non-blocking error/large-file warnings during load in src/gui/main_window.py

**Checkpoint**: Set loads <1s; UI remains responsive

---

## Phase 5: User Story 3 - Preview caméra automatique (Priority: P2)
**Goal**: Camera preview shows <3s after configure, even if model pending
**Independent Test**: Configure camera; preview starts <3s and updates live

### Tests for User Story 3
- [ ] T016 [P] [US3] Add preview-start test with fake camera source in tests/integration/test_camera_preview.py

### Implementation for User Story 3
- [ ] T017 [P] [US3] Add timeout handling and preview-ready signals in src/vision/camera_scanner.py
- [ ] T018 [P] [US3] Auto-start preview when camera ready (even without model) in src/gui/main_window.py and src/gui/video_display.py
- [ ] T019 [US3] Provide retry/feedback UI for preview failures without blocking in src/gui/main_window.py

**Checkpoint**: Preview auto-starts <3s; graceful retries on errors

---

## Phase 6: User Story 4 - Détection automatique (Priority: P3)
**Goal**: Detection auto-starts when set + camera + model are ready
**Independent Test**: With set and camera configured, model load completes and detection starts without manual action

### Tests for User Story 4
- [ ] T020 [P] [US4] Add auto-start integration test with stub workers in tests/integration/test_auto_start_detection.py

### Implementation for User Story 4
- [ ] T021 [P] [US4] Gate auto-start on set/camera/model flags and prevent double starts in src/gui/main_window.py
- [ ] T022 [P] [US4] Apply detection params to BrickDetector immediately after load before start in src/vision/brick_detector.py
- [ ] T023 [US4] Add UI toggle to enable/disable auto-start and display current state in src/gui/main_window.py

**Checkpoint**: Detection starts automatically when all components ready; can be toggled by user

---

## Phase 7: Polish & Cross-Cutting Concerns
**Purpose**: Documentation, performance traces, and hardening
- [ ] T024 [P] Update init flow diagrams and decisions in specs/001-parallel-init-qt/research.md
- [ ] T025 [P] Add perf/init benchmark script in tests/perf/test_init_timings.py to log startup metrics
- [ ] T026 Validate quickstart scenarios and record results in specs/001-parallel-init-qt/quickstart.md

---

## Dependencies & Execution Order
- Setup → Foundational → User Stories → Polish
- Story order by priority: US1 (P1) → US2 (P2) and US3 (P2) in parallel → US4 (P3)
- Tests per story should fail before implementation tasks in the same story

## User Story Dependency Graph
- US1 has no story prerequisites (blocks basic UX)
- US2 depends on Foundational; independent of US1 logic
- US3 depends on Foundational; can run parallel with US2
- US4 depends on US2 and US3 completing (needs set + camera + model readiness) and Foundational

## Parallel Execution Examples
- US1: Run T008 while implementing T009/T010; T011 parallel to T010
- US2: T013 and T014 in parallel; T012 runs alongside once harness ready
- US3: T017 and T018 in parallel; T016 runs with mocks while UI wiring proceeds
- US4: T021 and T022 in parallel; T020 runs with stub workers while UI toggle (T023) is built

## Implementation Strategy
- MVP first: Complete Setup + Foundational + US1, validate startup responsiveness
- Incremental: Add US2 and US3 in parallel once foundation is done; then US4 auto-start
- At each story checkpoint, run quickstart scenarios and integration tests; log timings
