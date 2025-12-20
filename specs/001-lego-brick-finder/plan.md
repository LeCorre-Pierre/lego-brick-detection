# Implementation Plan: Lego Brick Finder Application

**Branch**: `001-lego-brick-finder` | **Date**: 2025-12-20 | **Spec**: [specs/001-lego-brick-finder/spec.md](specs/001-lego-brick-finder/spec.md)
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a desktop application that allows users to quickly find Lego bricks from their set mixed in a pile using real-time computer vision. The app loads set data from Rebrickable CSV files, configures webcam or Kinect input, and provides an intuitive QT-based GUI for detection and interaction. Uses OpenCV for video processing and object detection to highlight bricks with bounding boxes, allowing users to mark found bricks by clicking.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: PyQt6 (QT GUI), OpenCV (video processing), NumPy (image processing), Pillow (image handling)  
**Storage**: File system for Lego set CSV files, in-memory data structures for detection state and brick tracking  
**Testing**: pytest for unit tests, manual testing for GUI interactions  
**Target Platform**: Windows (primary development), cross-platform support (Linux/Mac via QT)  
**Project Type**: Desktop GUI application  
**Performance Goals**: Real-time video processing at 30 fps, UI response time <1 second, detection accuracy >80% for standard Lego bricks  
**Constraints**: Robust detection in various lighting conditions and viewing angles, offline-capable, intuitive user interface with minimal setup steps  
**Scale/Scope**: Single-user local application, supports Lego sets up to 1000+ bricks, handles video streams up to 1080p

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Does the plan ensure accurate spotting of Lego bricks in piles?
- Is the detection based on predefined set pieces?
- Does it prevent re-detection after pickup?
- Is it designed for real-time video input from Kinect or webcam?
- Does it account for various lighting and angles?

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
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
