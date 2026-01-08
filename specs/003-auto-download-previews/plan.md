# Implementation Plan: Automatic Preview Image Downloads

**Branch**: `003-auto-download-previews` | **Date**: January 7, 2026 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-auto-download-previews/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Automatically download and cache preview images for Lego bricks from BrickLink when they're missing from the local repository. Images download in the background using a prioritized queue (viewport-first, then top-to-bottom), with fallback color codes (3, then 0-9) and rate limiting (1s delay between requests). The UI remains responsive with loading indicators and placeholder images on failures.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: PyQt6 (GUI), requests (HTTP downloads), Pillow (image handling), threading (background downloads)  
**Storage**: Local filesystem (`data/preview_images/`), organized by part number  
**Testing**: pytest (unit tests), manual integration testing via UI  
**Target Platform**: Desktop (Windows, Linux, macOS)  
**Project Type**: Single desktop application with PyQt6 GUI  
**Performance Goals**: Images load within 10s for full set, UI remains responsive during downloads  
**Constraints**: 1-second delay between downloads, no retry on failure, viewport-priority download queue  
**Scale/Scope**: Handle 100+ brick sets, support typical set sizes (50-500 bricks)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Does the plan ensure accurate spotting of Lego bricks in piles?**  
N/A - This feature handles image downloading, not detection. Does not affect detection accuracy.

✅ **Is the detection based on predefined set pieces?**  
N/A - This feature downloads preview images for set pieces already defined. Maintains existing set-based approach.

✅ **Does it prevent re-detection after pickup?**  
N/A - This feature only handles preview images, not detection logic.

✅ **Is it designed for real-time video input from Kinect or webcam?**  
N/A - This feature enhances the brick list UI, separate from video input.

✅ **Does it account for various lighting and angles?**  
N/A - Preview images are reference images, not detection input. Detection logic unchanged.

**Constitution Status**: PASS - Feature is orthogonal to detection principles; enhances UI/UX without affecting core detection functionality.

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

```text
src/
├── gui/
│   ├── brick_list_widget.py       # Update: integrate ImageDownloader
│   ├── brick_list_item.py         # Update: add loading/placeholder states
│   └── main_window.py
├── models/
│   ├── brick.py                   # Existing: Brick data model
│   └── lego_set.py
├── utils/
│   ├── image_cache.py             # Existing: extend for download status
│   ├── image_downloader.py        # NEW: background download manager
│   └── config_manager.py
├── loaders/
│   └── set_loader.py
└── vision/
    └── detection_engine.py

data/
└── preview_images/                # NEW: auto-created directory for cached images

tests/
├── unit/
│   ├── test_image_downloader.py   # NEW: download logic tests
│   └── test_image_cache.py        # Update: download integration tests
└── integration/
    └── test_preview_download_integration.py  # NEW: end-to-end tests
```

**Structure Decision**: Single desktop application (Option 1). New `ImageDownloader` utility handles background downloads with prioritization. Existing `ImageCache` extended to track download status. GUI components updated to display loading/placeholder states.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
