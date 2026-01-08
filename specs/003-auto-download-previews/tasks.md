# Tasks: Automatic Preview Image Downloads

**Input**: Design documents from `/specs/003-auto-download-previews/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are NOT included as they were not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Single project structure: `src/`, `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency setup

- [ ] T001 Add `requests` library to requirements.txt and install via pip
- [ ] T002 Create data/preview_images/ directory structure (auto-created on first use)
- [ ] T003 [P] Create src/utils/image_downloader.py module skeleton with imports and class definitions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Extend ImageCacheEntry in src/utils/image_cache.py with status field (ImageStatus enum), last_updated, error_message
- [ ] T005 [P] Define ImageStatus enum (MISSING, DOWNLOADING, CACHED, FAILED) in src/utils/image_cache.py
- [ ] T006 [P] Create DownloadRequest data class in src/utils/image_downloader.py with part_number, priority, color_code, timestamp fields
- [ ] T007 [P] Create DownloadSignals QObject in src/utils/image_downloader.py with download_started, download_complete, download_failed signals
- [ ] T008 Implement DownloadQueue class in src/utils/image_downloader.py with PriorityQueue, enqueue/dequeue methods, thread safety
- [ ] T009 Implement ImageDownloadWorker thread class in src/utils/image_downloader.py with run loop, stop flag, rate limiting

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Brick List with Missing Images (Priority: P1) 🎯 MVP

**Goal**: Auto-download missing preview images when brick list loads, display them as they arrive

**Independent Test**: Delete data/preview_images/, load a set, verify viewport images appear first and UI remains responsive

### Implementation for User Story 1

- [X] T010 [P] [US1] Implement _download_with_color_fallback() method in src/utils/image_downloader.py (try color 3, then 0-9)
- [X] T011 [P] [US1] Implement _construct_url() method in src/utils/image_downloader.py using BrickLink URL pattern
- [X] T012 [US1] Implement _download_image() method in src/utils/image_downloader.py with HTTP request, save to disk, error handling
- [X] T013 [US1] Implement _enforce_rate_limit() method in src/utils/image_downloader.py (1-second delay between requests)
- [X] T014 [US1] Complete ImageDownloadWorker.run() loop in src/utils/image_downloader.py (dequeue, download, emit signals, rate limit)
- [X] T015 [US1] Implement ImageDownloader.request_image() public method in src/utils/image_downloader.py (check cache, queue download, return status)
- [X] T016 [US1] Implement ImageDownloader.get_image_path() method in src/utils/image_downloader.py
- [X] T017 [US1] Implement ImageDownloader.get_status() method in src/utils/image_downloader.py
- [X] T018 [US1] Implement ImageDownloader.is_cached() method in src/utils/image_downloader.py
- [X] T019 [US1] Add ImageDownloader initialization in BrickListWidget.__init__() in src/gui/brick_list_widget.py
- [X] T020 [US1] Connect download_complete and download_failed signals to slot handlers in src/gui/brick_list_widget.py
- [X] T021 [US1] Update BrickListWidget.load_set() to check cache and request downloads in src/gui/brick_list_widget.py
- [X] T022 [US1] Implement viewport detection logic in src/gui/brick_list_widget.py for priority assignment
- [X] T023 [US1] Implement _on_image_downloaded() slot handler in src/gui/brick_list_widget.py to update UI
- [ ] T024 [US1] Add loading state support to BrickListItem in src/gui/brick_list_item.py (QMovie spinner or progress indicator)
- [X] T025 [US1] Update BrickListItem to display downloaded image when signal received in src/gui/brick_list_item.py
- [X] T026 [US1] Add logging for download events (started, completed, failed) in src/utils/image_downloader.py

**Checkpoint**: At this point, User Story 1 should be fully functional - images download automatically, viewport prioritized, UI responsive

---

## Phase 4: User Story 2 - Handle Download Failures Gracefully (Priority: P2)

**Goal**: Display placeholder images when downloads fail, allow UI to function without crashing

**Independent Test**: Disconnect network, load set, verify placeholders appear with part numbers and UI remains usable

### Implementation for User Story 2

- [X] T027 [P] [US2] Implement _generate_placeholder() method in src/utils/image_downloader.py using Pillow (gray background, part number text)
- [X] T028 [US2] Update _download_image() to catch network errors and mark status as FAILED in src/utils/image_downloader.py
- [X] T029 [US2] Generate and save placeholder image on FAILED status in src/utils/image_downloader.py
- [X] T030 [US2] Implement _on_download_failed() slot handler in src/gui/brick_list_widget.py
- [X] T031 [US2] Add show_placeholder() method to BrickListItem in src/gui/brick_list_item.py
- [X] T032 [US2] Update BrickListItem to display placeholder when download_failed signal received in src/gui/brick_list_item.py
- [X] T033 [US2] Add error logging with specific error messages (404, timeout, connection error) in src/utils/image_downloader.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - graceful failure handling with placeholders

---

## Phase 5: User Story 3 - Organize Downloaded Images Efficiently (Priority: P3)

**Goal**: Ensure consistent file organization, auto-create directories, sanitize filenames

**Independent Test**: Download images, verify files in data/preview_images/ with correct naming, test with special character part numbers

### Implementation for User Story 3

- [X] T034 [P] [US3] Implement _sanitize_filename() method in src/utils/image_downloader.py (replace special chars with underscores)
- [X] T035 [US3] Update _download_image() to use sanitized filenames when saving in src/utils/image_downloader.py
- [X] T036 [US3] Add directory auto-creation logic using os.makedirs(exist_ok=True) in src/utils/image_downloader.py
- [X] T037 [US3] Implement get_cache_size() method in ImageCache in src/utils/image_cache.py
- [X] T038 [US3] Implement get_cache_size_bytes() method in ImageCache in src/utils/image_cache.py
- [X] T039 [US3] Implement get_failed_parts() method in ImageCache in src/utils/image_cache.py
- [X] T040 [US3] Implement get_download_statistics() method in ImageCache in src/utils/image_cache.py

**Checkpoint**: All user stories should now be independently functional - complete feature set delivered

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T041 [P] Implement ImageDownloader.clear_cache() method in src/utils/image_downloader.py
- [X] T042 [P] Implement ImageDownloader.shutdown() method for graceful cleanup in src/utils/image_downloader.py
- [X] T043 Connect shutdown() to application quit signal in src/gui/main_window.py
- [X] T044 Add configuration constants (RATE_LIMIT_DELAY, REQUEST_TIMEOUT, CACHE_DIR) in src/utils/image_downloader.py
- [X] T045 [P] Update README.md with feature description and usage instructions
- [X] T046 Code review and refactoring for clarity
- [X] T047 Validate implementation against quickstart.md scenarios

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion (T001-T003) - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion (T004-T009)
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Foundational (T004-T009) - No dependencies on other stories
- **User Story 2 (P2)**: Depends on Foundational (T004-T009) + builds on US1 download logic (T012) but can run in parallel
- **User Story 3 (P3)**: Depends on Foundational (T004-T009) - Can start after Foundational, independently testable

### Within Each User Story

#### User Story 1 (P1) - Critical Path:
1. T010-T011 (parallel) → T012 (download logic) → T013-T014 (worker thread)
2. T015-T018 (public API methods, can be parallel)
3. T019-T023 (GUI integration sequence)
4. T024-T026 (UI updates, can overlap with T019-T023)

#### User Story 2 (P2):
- T027 (placeholder generation) can start immediately after foundational
- T028-T029 require T012 (download logic) from US1
- T030-T033 can proceed once T027-T029 complete

#### User Story 3 (P3):
- T034-T036 can start after foundational (independent of US1/US2)
- T037-T040 (cache statistics) can run in parallel

### Parallel Opportunities

**Setup Phase (Phase 1)**:
- T001, T002, T003 can all run in parallel (different concerns)

**Foundational Phase (Phase 2)**:
- T005, T006, T007 can run in parallel (different classes/files)
- T004 (ImageCache extension) can run parallel with T005-T007
- T008-T009 must be sequential (DownloadQueue before Worker)

**User Story 1 (Phase 3)**:
- T010, T011 can run in parallel (different methods)
- T015, T016, T017, T018 can run in parallel (different public methods)
- T024, T025 can run in parallel (different aspects of BrickListItem)

**User Story 2 (Phase 4)**:
- T027, T033 can run in parallel (placeholder gen + logging)
- T030, T031, T032 can run in parallel (different UI components)

**User Story 3 (Phase 5)**:
- T034, T036 can run in parallel (different utility functions)
- T037, T038, T039, T040 can all run in parallel (different cache methods)

**Polish Phase (Phase 6)**:
- T041, T042, T044, T045 can all run in parallel (different files/concerns)

**Across User Stories** (if team capacity allows):
Once Foundational complete, US1, US2, US3 can ALL start in parallel by different developers.

---

## Parallel Example: User Story 1

```bash
# Launch foundational work in parallel:
Task: "Define ImageStatus enum in src/utils/image_cache.py"
Task: "Create DownloadRequest data class in src/utils/image_downloader.py"
Task: "Create DownloadSignals QObject in src/utils/image_downloader.py"

# Launch US1 initial methods in parallel:
Task: "Implement _download_with_color_fallback() in src/utils/image_downloader.py"
Task: "Implement _construct_url() in src/utils/image_downloader.py"

# Launch US1 public API methods in parallel:
Task: "Implement ImageDownloader.get_image_path() in src/utils/image_downloader.py"
Task: "Implement ImageDownloader.get_status() in src/utils/image_downloader.py"
Task: "Implement ImageDownloader.is_cached() in src/utils/image_downloader.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T009) - CRITICAL
3. Complete Phase 3: User Story 1 (T010-T026)
4. **STOP and VALIDATE**: 
   - Delete cache
   - Load a set
   - Verify images download automatically
   - Verify viewport priority works
   - Verify UI stays responsive
5. Deploy/demo if ready - this is a complete MVP!

### Incremental Delivery

1. Setup + Foundational → Foundation ready (T001-T009)
2. Add User Story 1 → Test independently → Deploy/Demo (T010-T026) **MVP!**
3. Add User Story 2 → Test independently → Deploy/Demo (T027-T033) - Now with error handling
4. Add User Story 3 → Test independently → Deploy/Demo (T034-T040) - Now with file organization
5. Polish → Final production release (T041-T047)

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T009)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (T010-T026)
   - **Developer B**: User Story 2 (T027-T033) - can start T027 immediately, rest after T012
   - **Developer C**: User Story 3 (T034-T040) - fully independent after T004-T009
3. Stories complete and integrate independently

---

## Success Validation

After completing each user story, validate against spec.md acceptance scenarios:

### User Story 1 Validation:
- ✅ Missing images detected and downloads initiated automatically
- ✅ Downloaded images appear in list without page refresh
- ✅ Subsequent loads use cached images (no re-download)

### User Story 2 Validation:
- ✅ Failed downloads show placeholder with part number
- ✅ Network unavailable: cached images display, missing show placeholders
- ✅ Network restored: failed images can be manually retried (if retry implemented)

### User Story 3 Validation:
- ✅ Files stored in data/preview_images/
- ✅ Filename format: {part_number}.png
- ✅ Directory auto-created on first use

---

## Notes

- **[P] tasks**: Different files, no dependencies - safe to parallelize
- **[Story] label**: Maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests not included per spec (not explicitly requested)
- Follow research.md decisions on URL construction, rate limiting, color fallback
- Reference contracts/image_downloader_interface.py for API specifications
- Use quickstart.md for implementation guidance and troubleshooting

---

## Task Count Summary

- **Setup**: 3 tasks
- **Foundational**: 6 tasks (BLOCKS all stories)
- **User Story 1 (P1)**: 17 tasks - MVP
- **User Story 2 (P2)**: 7 tasks - Error handling
- **User Story 3 (P3)**: 7 tasks - File organization
- **Polish**: 7 tasks - Production ready

**Total**: 47 tasks

**Parallel Opportunities**: 20+ tasks can run in parallel (marked with [P])

**Estimated MVP**: 26 tasks (Setup + Foundational + US1)
