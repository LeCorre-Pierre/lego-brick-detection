# Lego Brick Detection — AI Assistant Guidelines

## Project Purpose

PyQt6 desktop app that detects Lego bricks in a live camera feed using YOLOv8, guided by a set inventory loaded from CSV. The user points a camera at a pile of bricks; the app identifies which pieces belong to their target set and tracks progress.

## Run Command

```bash
python -m src.main --set-file ./data/sample_3005.csv --camera 0
```

Both arguments are optional.

## Stack

- Python 3.11
- PyQt6 (GUI)
- OpenCV (camera and image processing)
- Ultralytics YOLOv8 (detection)
- NumPy

## Source Layout

```
src/
  main.py              # Entry point, argument parsing, QApplication setup
  gui/
    main_window.py     # Top-level window, orchestrates all panels
    video_display.py   # Camera feed widget
    brick_list_widget.py / brick_list_item.py  # Set inventory list
    detection_panel.py # Threshold slider, scope toggle
    set_info_panel.py  # Set metadata display
    camera_config_dialog.py
  models/
    brick.py           # Brick data class
    lego_set.py        # LegoSet: collection of bricks with counts
    video_source.py    # Camera abstraction
  loaders/
    set_loader.py      # CSV → LegoSet
  vision/
    detection_engine.py  # YOLO inference, Roboflow fallback
    model_loader.py      # .pt file selection logic
    detection_state.py   # Per-brick detection state, "picked up" logic
    color_matcher.py     # Color filtering helpers
    contour_analyzer.py
    video_utils.py
    video_tester.py
    camera_scanner.py    # Enumerate available cameras
```

## Key Behaviours

- **Set loading**: CSV → `LegoSet` model → populates `BrickListWidget`
- **Preview images**: Auto-downloaded from BrickLink on set load; cached in `data/preview_images/`; generated placeholder if unavailable
- **Detection scope**: "Set only" mode filters YOLO classes to bricks present in the loaded set
- **Static frame tuning**: Stopping video freezes the last frame; detection still runs on it so parameters can be tuned without camera overhead
- **No re-detection after pickup**: Once a brick is marked (manually or by detection), it is excluded from future detection frames

## Model Selection

1. Checks `LEGO_MODEL_PATH` env var first
2. Falls back to best `.pt` in `models/` (LEGO-oriented filename ranking)
3. Optional Roboflow hosted fallback: set `ROBOFLOW_API_KEY` + `ROBOFLOW_MODEL_ID`

## Constitution

Core project principles are in [.specify/memory/constitution.md](.specify/memory/constitution.md). They govern all design decisions; simplicity and ease of use are paramount.

## What Does NOT Exist

- No annotation tool (`src/annotation/` does not exist; specs/004 was never implemented)
- No web interface
- No database — state is in-memory only, set reloaded from CSV each session

## Testing

```bash
pytest
```

Tests are in `tests/`. Use `ruff check .` for linting.

## Data

- `data/` — CSV set files, cached preview images
- `models/` — YOLO `.pt` model files (not committed; download separately)
- `screenshoot/` — frames saved by the user during a session

See [MODEL_ZOO.md](MODEL_ZOO.md) for available pre-trained models.
