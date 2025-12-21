# Implementation Plan: Lego Brick Finder Application

**Branch**: `001-lego-brick-finder` | **Date**: 2025-12-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-lego-brick-finder/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a desktop application that enables Lego builders to quickly identify and locate specific bricks from their Lego sets within a mixed pile of bricks. The application loads Lego set data from provider formats (focusing on Rebrickable CSV), configures video input from webcam or Kinect, and provides real-time computer vision-based brick detection with interactive marking of found bricks.

Technical approach: Python desktop application using PyQt6 for GUI, OpenCV for computer vision, with modular architecture separating detection logic, video processing, and user interface components.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: PyQt6 (GUI), OpenCV (computer vision), NumPy (image processing)  
**Storage**: File-based (CSV set files, local configuration)  
**Testing**: pytest (unit tests), manual integration testing  
**Target Platform**: Cross-platform desktop (Windows/Linux/macOS)  
**Project Type**: Desktop GUI application  
**Performance Goals**: Real-time video processing (30+ FPS), >80% detection accuracy  
**Constraints**: Real-time detection, robust to various lighting/angles, intuitive GUI  
**Scale/Scope**: Single-user desktop application, handles 1000+ brick sets

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ Does the plan ensure accurate spotting of Lego bricks in piles? **YES** - Real-time computer vision detection with bounding boxes
- ✅ Is the detection based on predefined set pieces? **YES** - Loads brick definitions from Lego set files (Rebrickable CSV)
- ✅ Does it prevent re-detection after pickup? **YES** - Interactive marking system allows users to mark bricks as picked
- ✅ Is it designed for real-time video input from Kinect or webcam? **YES** - Supports both webcam and Kinect video sources
- ✅ Does it account for various lighting and angles? **YES** - Adjustable detection settings for different environments

**Post-Phase 1 Re-evaluation**: All constitution principles satisfied. Design includes robust computer vision pipeline, set-based detection, interactive marking, multi-source video input, and environmental adaptation features.

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

## Project Structure

### Documentation (this feature)

```text
specs/001-lego-brick-finder/
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
├── main.py             # Application entry point
├── detect.py           # Legacy detection script
├── gui/                # PyQt6 GUI components
│   ├── main_window.py      # Main application window
│   ├── video_display.py    # Video stream display widget
│   ├── set_info_panel.py   # Set information display
│   └── camera_config_dialog.py  # Camera configuration
├── loaders/            # Data loading components
│   └── set_loader.py       # Lego set file loader
├── models/             # Data models
│   ├── brick.py            # Brick data model
│   ├── lego_set.py         # Lego set data model
│   ├── detection_result.py # Detection result model
│   └── video_source.py     # Video source configuration
├── utils/              # Utility modules
│   ├── logger.py           # Logging configuration
│   └── progress_tracker.py # Detection progress tracking
└── vision/             # Computer vision components
    ├── brick_detector.py   # Main detection logic
    ├── camera_scanner.py   # Camera device detection
    ├── color_matcher.py    # Color matching algorithms
    ├── contour_analyzer.py # Shape/contour analysis
    ├── video_utils.py      # Video processing utilities
    └── video_tester.py     # Video stream testing

tests/                  # Test suite
├── unit/               # Unit tests
├── integration/        # Integration tests
└── fixtures/           # Test data

data/                   # Sample data files
├── sample_3005.csv     # Sample Lego set data
└── import_sample.csv   # Additional sample data

models/                 # Trained ML models (future)
logs/                   # Application logs
notebooks/              # Jupyter notebooks for experimentation
```

**Structure Decision**: Single Python project structure with modular organization separating GUI, vision processing, data models, and utilities. Current structure matches the established codebase and follows Python packaging best practices.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
