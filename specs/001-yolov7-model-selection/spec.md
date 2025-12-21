# Feature Specification: Model Selection — Improve Lego Detection Quality

**Feature Branch**: `001-yolov7-model-selection`  
**Created**: 2025-12-21  
**Status**: Draft  
**Input**: Focus on the detection model. Baseline: models/zero-shot-1000-single-class.pt (trained with ~1000 images from dreamfactor/biggest-lego-dataset-600-parts using a YOLO pipeline). Limitation: single-class causes many false positives on non‑Lego; move to multi-class aligned with full set inventory and larger training data.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reduce false positives on non‑Lego (Priority: P1)

As a user, I want the detector to avoid flagging non‑Lego objects so I can trust the results without wasting time.

**Why this priority**: High confidence is essential; excessive false positives break user trust.

**Independent Test**: Evaluate on a non‑Lego validation set; measure false positive rate (FPR) and confirm it meets the target.

**Acceptance Scenarios**:

1. **Given** a set of non‑Lego images, **When** the detector runs, **Then** fewer than 5% of images report Lego detections.
2. **Given** a mixed scene, **When** the detector runs, **Then** non‑Lego items are ignored while true Lego pieces are detected.

---

### User Story 2 - Detect per‑class pieces from set inventory (Priority: P2)

As a user, I want the detector to recognize specific Lego part types relevant to my loaded set so I can find exact pieces.

**Why this priority**: Per‑class detection aligns results to the user’s set and reduces ambiguity.

**Independent Test**: Evaluate on a labeled Lego validation set covering common classes; measure per‑class precision/recall.

**Acceptance Scenarios**:

1. **Given** a set inventory, **When** detection runs, **Then** results include class labels mapped to parts in the inventory.
2. **Given** small/rare parts, **When** detection runs, **Then** per‑class metrics meet minimum thresholds.

---

### User Story 3 - Configurable confidence and filtering (Priority: P3)

As a user, I want to adjust detection confidence and filtering rules (size, aspect, color consistency) to balance recall and precision for my environment.

**Why this priority**: Different setups (lighting, clutter) require tuning to maintain quality.

**Independent Test**: Adjust thresholds; confirm metrics change predictably and settings persist.

**Acceptance Scenarios**:

1. **Given** confidence set to a higher value, **When** detection runs, **Then** precision increases and recall decreases within expected bounds.
2. **Given** saved settings, **When** the app restarts, **Then** the same thresholds apply without reconfiguration.

---

### Edge Cases

- Scenes with many red/blue plastic objects that resemble Lego
- Very small parts partially occluded or overlapping
- Reflective surfaces causing spurious detections
- Domain shift from training data (new backgrounds or lighting)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The detector MUST achieve an overall false positive rate on non‑Lego scenes ≤ 5%.
- **FR-002**: The detector MUST support per‑class recognition covering the full loaded set inventory.
- **FR-003**: The system MUST provide configurable thresholds and filters (confidence, size, aspect, color consistency) with persistence.
- **FR-004**: The evaluation harness MUST provide a labeled validation set and report precision/recall, F1, and FPR.
- **FR-005**: The system MUST allow switching between single‑class and multi‑class modes.
- **FR-006**: The detector MUST maintain real‑time inference suitable for live video ($\leq$ 33ms per frame target).
- **FR-007**: The system MUST expose summary metrics to users (e.g., “quality indicators”) without technical jargon.
- **FR-008**: The system MUST avoid technology lock‑in in the specification; implementation details are deferred to planning.

### Key Entities

- **DetectionModel**: conceptual model producing bounding boxes and class scores.
- **ValidationDataset**: curated Lego and non‑Lego images with labels for evaluation.
- **SetInventory**: parts to consider for multi‑class mapping.
- **QualityConfig**: user‑set thresholds and filters for tuning detection.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: False positive rate on non‑Lego validation ≤ 5%.
- **SC-002**: Per‑class precision ≥ 80% and recall ≥ 70% on common parts.
- **SC-003**: Users report improved trust (≥ 80% satisfaction in a simple survey after tuning).
- **SC-004**: Real‑time inference maintained (≥ 30 FPS on target hardware in typical scenes).

## Assumptions

- Baseline model path exists and can be evaluated; implementation may switch to multi‑class as needed.
- Hardware target confirmed: NVIDIA RTX 4070 GPU available; CPU fallback acceptable with lower FPS.
- Datasets can be expanded beyond 1000 images to improve generalization.

## Dependencies

- Labeled validation data for Lego/non‑Lego; per‑class mapping aligned to inventory.
- Model training/evaluation scripts (implementation detail deferred).

## Clarifications

- Multi‑class scope: Full inventory coverage (user confirmed).
- Primary hardware target: Optimize metrics for GPU (RTX 4070 confirmed).
- Target quality thresholds: Use MVP defaults unless revised — FPR ≤ 5%, precision ≥ 80%, recall ≥ 70%.
