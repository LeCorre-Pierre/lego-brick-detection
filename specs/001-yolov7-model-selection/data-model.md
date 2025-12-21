# Data Model — Model Selection

## Entities
- `DetectionModelConfig`: mode (single/multi‑class), classes list (from inventory), confidence/NMS thresholds, size/aspect filters.
- `InventoryClasses`: mapping from set inventory to detector class labels.
- `ValidationDataset`: Lego/non‑Lego images with labels; splits and metadata.
- `MetricsReport`: precision/recall/F1 per class, FPR for non‑Lego, latency/FPS.
- `QualityConfig`: user‑editable tuning persisted via config manager.

## Relationships
- `DetectionModelConfig` uses `InventoryClasses` to constrain model outputs.
- `ValidationDataset` produces `MetricsReport` via evaluation harness.
- `QualityConfig` updates detector thresholds and post‑processing.

## State Transitions
1) Configure model (multi‑class, inventory).
2) Run evaluation → produce `MetricsReport`.
3) Apply `QualityConfig` tuning → re‑evaluate.

## Files
- Models: stored under `models/`.
- Datasets: stored under `data/`.
- Reports: stored under `logs/` (CSV/JSON).
