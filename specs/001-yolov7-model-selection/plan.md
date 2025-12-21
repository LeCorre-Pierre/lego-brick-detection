# Implementation Plan: Model Selection — Improve Lego Detection Quality

**Branch**: `001-yolov7-model-selection` | **Date**: 2025-12-21 | **Spec**: [specs/001-yolov7-model-selection/spec.md](specs/001-yolov7-model-selection/spec.md)
**Input**: Feature specification from `/specs/001-yolov7-model-selection/spec.md`

## Summary

Elevate detection quality by moving from single‑class to multi‑class aligned to full set inventory, reduce false positives on non‑Lego, and provide tunable thresholds while sustaining real‑time performance on RTX 4070. Research compares dataset expansion and multi‑class training, evaluation harness, and tuning filters.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11  
**Primary Dependencies**: PyTorch/YOLO training pipeline (implementation detail deferred), PyQt6 app runtime, OpenCV/NumPy for vision I/O  
**Storage**: Local datasets and models (files)  
**Testing**: pytest + pytest‑qt for integration; evaluation scripts for metrics  
**Target Platform**: Desktop, Windows (RTX 4070), Webcam/Kinect  
**Project Type**: Single desktop app + evaluation harness  
**Performance Goals**: Real‑time inference ≥ 30 FPS; detector per‑frame latency ≤ 33ms  
**Constraints**: Minimize false positives (FPR ≤ 5%); keep UI responsive; GPU primary, CPU fallback acceptable with lower FPS  
**Scale/Scope**: Full set inventory multi‑class coverage; validation on mixed non‑Lego scenes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Accurate spotting in piles: Yes — multi‑class + improved dataset + tuning.
- Set‑based definition: Yes — full inventory mapping to labels.
- No re‑detection after pickup: Yes — app logic preserves this; model plan doesn’t violate.
- Real‑time video input: Yes — GPU target RTX 4070 maintains ≥ 30 FPS.
- Robust environments: Yes — filters and configurable thresholds support varied lighting/angles.

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
src/
├── vision/                # Detector runtime and tuning hooks
├── gui/                   # UI for detection and settings
├── utils/                 # Config, logging, metrics I/O
└── main.py                # App entry

specs/001-yolov7-model-selection/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/

tests/
├── integration/           # startup/perf/integration tests
└── perf/                  # evaluation timings and reports
```

**Structure Decision**: Single desktop app with evaluation harness documents; contracts specify evaluation interfaces and tuning outputs.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
