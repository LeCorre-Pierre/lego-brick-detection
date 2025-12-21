# Contracts — Detection Tuning

## Config Persistence
- `QualityConfig` saved via `src/utils/config_manager.py`.
- Fields: `confidence`, `nms_iou`, `min_size_px`, `aspect_ratio_range`, `color_consistency_enabled`.

## App Integration
- UI allows adjusting these fields and applies to detector runtime.
- Detector reads config on startup; updates live at runtime via settings dialog.

## Output Indicators
- Display quality indicators: current thresholds + last evaluation summary.
- Persisted changes reflected across sessions.
