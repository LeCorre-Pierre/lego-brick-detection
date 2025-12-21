# Quickstart — Model Selection

## Evaluate Baseline
1. Ensure baseline model exists: `models/zero-shot-1000-single-class.pt`.
2. Prepare validation datasets under `data/validation/lego` and `data/validation/non_lego`.
3. Run evaluation (example CLI in contracts/model_evaluation.md) and save `logs/metrics.json`.

## Transition to Multi‑Class
1. Define inventory classes from the loaded set; map labels accordingly.
2. Train/prepare multi‑class model (implementation detail deferred in spec/plan).
3. Re‑evaluate and compare metrics to targets (FPR, precision/recall, FPS).

## Tune Detection
1. Use the settings dialog to adjust confidence/NMS/size/aspect filters.
2. Verify changes via evaluation harness and in live app preview.
3. Persist settings via config manager.

## Targets
- FPR ≤ 5% (non‑Lego); per‑class precision ≥ 80%, recall ≥ 70%; ≥ 30 FPS on RTX 4070.
