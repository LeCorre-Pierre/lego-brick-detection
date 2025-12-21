# Research & Decisions — Model Selection

**Goal**: Improve detection quality by moving to multi‑class per full inventory, reduce false positives, and retain real‑time performance on RTX 4070.

## Decisions
- Model scope: Multi‑class covering full set inventory.
- Hardware: NVIDIA RTX 4070 (GPU) as primary target; CPU fallback acceptable.
- Quality targets: FPR ≤ 5% (non‑Lego), per‑class precision ≥ 80%, recall ≥ 70%, ≥ 30 FPS.

## Alternatives Considered
- Single‑class detector (baseline): Simple but high false positives; rejected.
- Shortlist of common classes: Faster to ship but misaligned with full inventory; rejected given target.
- Classical CV filters only: Helpful for tuning but insufficient without model change; used as adjunct.

## Dataset & Training Considerations
- Expand dataset beyond ~1000 images; include diverse backgrounds and lighting.
- Label per‑class consistent with inventory mapping; ensure small/rare parts present.
- Use validation splits for Lego and non‑Lego scenes; track per‑class metrics.

## Evaluation Harness
- Prepare validation sets (Lego/non‑Lego) and report: precision, recall, F1, FPR.
- Emit timings (per‑frame latency, FPS) on target hardware.
- Provide confusion matrices and per‑class breakdowns.

## Tuning Filters
- Confidence threshold and NMS tuning.
- Size/aspect constraints to reduce spurious detections.
- Color consistency checks to align with expected part colors (optional, as adjunct).

## Risks & Mitigations
- Overfitting to specific scenes → diversify dataset; use augmentation.
- Small parts under‑detected → class‑specific training and thresholds.
- Performance regression → GPU acceleration and model pruning/optimization if needed.

## Measurement Plan
- Log FPR on non‑Lego validation; target ≤ 5%.
- Track per‑class precision/recall thresholds and overall F1.
- Record per‑frame latency and FPS; target ≤ 33ms and ≥ 30 FPS.
