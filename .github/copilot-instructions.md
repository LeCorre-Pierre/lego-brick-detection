# lego-brick-detection — Development Guidelines

## Stack

- Python 3.11, PyQt6, OpenCV, Ultralytics (YOLOv8), NumPy

## Commands

```bash
# Run the app
python -m src.main --set-file ./data/sample_3005.csv --camera 0

# Tests
pytest

# Lint
ruff check .
```

## Code Style

- Follow PEP 8 / standard Python 3.11 conventions
- PyQt6 signals/slots for GUI communication between components
- Keep GUI logic in `src/gui/`, data models in `src/models/`, vision/detection in `src/vision/`

## Architecture Notes

- `MainWindow` orchestrates all panels and owns the Qt signal connections
- Detection runs in a background `QThread`; never call UI methods directly from detection threads
- `LegoSet` is the central data model; it is rebuilt from CSV on each set load
- Preview image downloads run in a separate thread; use signals to update the brick list
- `detection_state.py` tracks per-brick detection history and "picked up" status

## What Does Not Exist

- `src/annotation/` — annotation tool was never implemented; do not reference it
- `specs/004` — planned but not implemented
