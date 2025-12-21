# Data Model — Initialisation parallèle (Qt)

## UI/Init State
- `InitProgress` (UI-thread owned):
  - `set_loaded: bool`
  - `camera_configured: bool`
  - `model_loaded: bool`
  - `last_error: Optional[str]` (non-fatal info)
- `DetectionParams`: thresholds, color/contour tuning; loaded via ConfigManager; applied to `BrickDetector` post-load.
- `UI Flags`: `is_detecting`, `model_loading`, `config_loaded` (UI-thread booleans for gating buttons/auto-start).

## Workers & Signals
- `SetCSVLoader(QThread)`: inputs `csv_path`; emits `finished(lego_set)`, `error(str)`, `progress(str)`.
- `VideoSourceConfigurator(QThread)`: inputs `camera_index`; emits `finished(video_source)`, `error(str)`, `progress(str)`.
- `ModelLoader(QThread)`: loads AI model; emits `finished(brick_detector)`, `error(str)`, `progress(str)`.
- `BrickDetector`: accepts `set_lego_set`, `set_detection_params`, `detect_bricks(frame)`, `get_stable_detections`.

## UI Components (relevant to init)
- `MainWindow`: owns init flags, starts workers, handles signals, gates auto-start detection.
- `VideoDisplayWidget`: shows preview, overlays detection, exposes status text & loading indicators.
- `SetInfoPanel` + `QListWidget` brick list: displays set contents; updated post-load.

## State Transitions (high level)
1) `MainWindow.__init__`: UI shown; init flags false; timers schedule deferred init.
2) `_start_parallel_initialization`: kicks off set/camera/model workers (if inputs provided).
3) Signals mutate `InitProgress` on UI thread; update UI status; call `_check_auto_start_detection`.
4) Auto-start condition: `set_loaded && camera_configured && model_loaded` (or detection-only gate for preview-first flow).
5) Errors: captured per worker; surface status text; do not block UI; allow retry.

## Data Files
- Set CSV inputs (user-provided) parsed into `LegoSet` with `Brick` entries.
- No persistent DB; optional config file via `ConfigManager`.
