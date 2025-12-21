# Contracts — Model Evaluation

## Evaluation Inputs
- `ValidationDataset`: paths to Lego/non‑Lego images; labels.
- `DetectionModelConfig`: model path, classes, thresholds.

## Evaluation Outputs
- `MetricsReport` JSON:
  - `overall`: { `precision`, `recall`, `f1`, `fps`, `latency_ms` }
  - `non_lego_fpr`: number
  - `per_class`: [ { `class`, `precision`, `recall`, `f1` } ]
  - `confusion`: stored as CSV/PNG in `logs/`.

## CLI Contract (example)
- Evaluate:
  - `python -m tools.eval --model models/<name>.pt --dataset data/validation --inventory specs/<feature>/inventory.json --out logs/metrics.json`
- Report:
  - `python -m tools.report --metrics logs/metrics.json --out logs/metrics_report.csv`
