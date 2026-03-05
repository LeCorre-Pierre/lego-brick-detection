# Lego Brick Detection

A PyQt6 desktop application that uses YOLOv8 to detect Lego bricks in a live camera feed, guided by a Lego set inventory.

## Concept

Point your camera at a pile of Lego bricks. The app detects pieces that belong to the set you are building and tracks which ones you have already picked up.

Core principles are in [.specify/memory/constitution.md](.specify/memory/constitution.md).

## Quick Start

```bash
pip install -r requirements.txt
python -m src.main --set-file ./data/sample_3005.csv --camera 0
```

`--set-file` and `--camera` are optional. The set can also be loaded from the GUI.

## Features

### Brick List

Loaded from a Lego set CSV file. Each row shows the brick's preview image, ID, name, count (`current/required`), a manual checkbox, and a detection indicator.

**Interactions:**
- Left-click a row: increment its counter
- Right-click a row: decrement its counter (min 0)
- Counter turns the row green when it reaches the required quantity
- Checkbox: manually mark a brick as found — excludes it from auto-detection

**Dynamic sorting:** when detection is running, bricks currently visible in the camera frame float to the top with a detection indicator. They return to their original position when no longer detected.

**Preview images** are fetched automatically from BrickLink on set load and cached in `data/preview_images/<part_number>.<ext>`. Viewport-visible bricks are prioritised; a placeholder showing the part number is generated if a download fails. Downloads are rate-limited (1 s between requests) and run in a background thread.

### YOLO Detection

- Detects bricks via a local `.pt` model (YOLOv8)
- Optional Roboflow hosted-inference fallback
- **Detection scope**: filter detections to only the bricks in the loaded set, or detect all model classes
- **Static frame tuning**: stop the video feed to freeze a frame and adjust threshold/scope without real-time overhead
- Default confidence threshold: 20%

### Camera

- Works with any webcam or Kinect v1
- Start/stop video independently of detection
- Save current frame as JPG to `screenshoot/`

## Model Setup

### Local model (default)

Place a YOLOv8 `.pt` file in `models/`. The app auto-selects the best one based on filename ranking.

Override with an environment variable:
```bash
LEGO_MODEL_PATH=models/my_model.pt python -m src.main
```

### Roboflow fallback (optional)

```bash
ROBOFLOW_API_KEY=<key>
ROBOFLOW_MODEL_ID=craftyblocks/hex-lego-yk2pe/1
```

See [MODEL_ZOO.md](MODEL_ZOO.md) for available models.

## Set File Format

A CSV file with Lego set inventory. Example: `data/sample_3005.csv`.

## Project Structure

```
src/
  main.py              # Entry point
  gui/                 # PyQt6 windows and widgets
  models/              # Data models (Brick, LegoSet, VideoSource)
  loaders/             # Set CSV loader
  vision/              # Detection engine, model loader, video utilities
data/
  preview_images/      # Cached BrickLink preview images
models/                # YOLO .pt model files
screenshoot/           # Saved frames
```

## Dependencies

- Python 3.11
- PyQt6
- OpenCV
- Ultralytics (YOLOv8)
- NumPy

Install: `pip install -r requirements.txt`

## Datasets

- **B200 LEGO Detection**: [Kaggle](https://www.kaggle.com/datasets/ronanpickell/b100-lego-detection-dataset/data) — 200 parts, 800k synthetic images
- **Hex LEGO (Roboflow)**: [roboflow.com](https://universe.roboflow.com/craftyblocks/hex-lego-yk2pe) — 8,320 images, 28 classes
