# Lego Brick Detection

A Python project for detecting Lego bricks using machine learning and computer vision.

## Constitution

See [.specify/memory/constitution.md](.specify/memory/constitution.md) for project principles and guidelines.

## Installation

1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`

## Features

### 🆕 YOLO Annotation Tool

**Create high-quality YOLO datasets for LEGO brick detection!**

The project now includes a powerful annotation tool to create and manage YOLO-compatible datasets:

- ✅ **Easy-to-use GUI**: PyQt6 interface with intuitive controls
- ✅ **YOLO export**: Native format support (no external dependencies)
- ✅ **Quick annotation**: Keyboard shortcuts (1-6) for classes, click-and-drag for bboxes
- ✅ **Project management**: Auto-save, validation, train/val split
- ✅ **Pre-defined classes**: 6 common LEGO bricks (customizable)
- ✅ **Statistics**: Real-time visualization of dataset progress

**Launch the annotation tool**:
```bash
python src/annotation/run_annotation_tool.py
```

**Documentation**:
- User Guide: [specs/004-yolo-annotation-tool/USER_GUIDE.md](specs/004-yolo-annotation-tool/USER_GUIDE.md)
- API Documentation: [src/annotation/README.md](src/annotation/README.md)
- Implementation: [specs/004-yolo-annotation-tool/IMPLEMENTATION_SUMMARY.md](specs/004-yolo-annotation-tool/IMPLEMENTATION_SUMMARY.md)

### Core Detection Features

- Real-time video preview with start/stop controls
- Save Preview (JPG) button stores current frame in screenshoot/ with timestamp
- YOLOv8 detection toggle with bounding boxes and labels
- Detection scope control: choose to detect only bricks from the loaded set or all model classes
- Detection menu: quick actions to toggle set-only scope and reset threshold
- **Static frame tuning**: Stop video to freeze the preview and adjust detection parameters (threshold, scope) on a static image without real-time processing overhead

### Automatic Preview Image Downloads

The application now automatically downloads missing brick preview images from BrickLink when you load a set:

- **Smart Prioritization**: Images for bricks in the viewport are downloaded first, providing instant visual feedback
- **Background Processing**: Downloads occur in a separate thread, keeping the UI responsive
- **Graceful Fallback**: If an image cannot be downloaded (network issue, 404), a placeholder with the part number is generated
- **Rate Limiting**: 1-second delay between downloads to respect BrickLink servers
- **Caching**: Downloaded images are saved to `data/preview_images/` for future use

**Usage**: Simply load a Lego set - preview images will appear automatically as they download. No manual intervention needed!
```

3. Start the video preview and toggle detection:

- Click "Start Video" to begin the preview.
- When the model finishes loading, the detection button becomes enabled.
- Click "Start Detection" to overlay bounding boxes and labels on the preview.
- Click again to stop detection and show a clean preview.

4. Control detection scope:

- In the "Detection Scope" section, use the checkbox "Detect only bricks from this set".
- Enabled (default): Filters detections to classes matching bricks in the loaded set (by part number or name).
- Disabled: Shows detections for all classes known by the YOLO model.

5. Detection options menu:

- Use the "Detection" menu to quickly toggle "Detect Only Set Classes" and to "Reset Threshold to 20%".

6. Static frame tuning workflow:

- Click "Stop Video" to freeze the current preview frame.
- The last image remains visible and can be processed by the detection engine.
- Adjust the detection threshold slider or toggle scope; the frozen frame will update immediately.
- Use "Save Preview (JPG)" to save the tuned frame with overlays.
- This allows precise parameter tuning without real-time processing delays.

## Project Structure

- `src/`: Source code
- `tests/`: Unit tests
- `data/`: Dataset and images
- `models/`: Trained models
- `notebooks/`: Jupyter notebooks for experimentation

## Command

python -m src.main --set-file ./data/sample_3005.csv --camera 0

## Screenshots

- Save current preview as JPG: Use the "Save Preview (JPG)" button in the GUI. Files are saved to the `screenshoot/` directory with timestamped names.

##Dataset 

B200 LEGO Detection Dataset
    https://www.kaggle.com/datasets/ronanpickell/b100-lego-detection-dataset/data

    Use this data for training custom LEGO object detection models. This highly realistic data is fully synthetic, and attempts to mimic photo-realism as closely as possible.

    FEATURES ✔ 200 Most Popular LEGO Parts ✔ 4,000 Images Per LEGO Part ✔ 800,000 Total Images ✔ 64x64 RGB Images ✔ In Context Images

    This data was created through a mixed usage of the Blender Python API alongside many other Python packages including Matplotlib, Pillow, and PyAutoGUI.

Brick Architect (https://brickarchitect.com) for knowledge and resources on LEGO parts and colors. LDraw (https://www.ldraw.org/) for 3D part models.
Hex: Lego Computer Vision Dataset 
    https://universe.roboflow.com/craftyblocks/hex-lego-yk2pe


    Overview
    The Hex: Lego Object Detection Model utilizes the YOLOv7 algorithm to accurately identify and classify various sizes and colors of LEGO bricks. This model is designed to perform robustly under diverse lighting conditions, suitable for applications in automated sorting, inventory management, and educational tools.

    Dataset
    This dataset, curated with Roboflow, includes 8,320 images and over 15,000 annotations, capturing LEGO bricks in different configurations and lighting environments. Data augmentation techniques were applied to enhance robustness, covering 28 distinct LEGO brick classes.




## Detection Pipeline (Unstuck Mode)

The inference pipeline supports both local and hosted models:

1. Local `.pt` model via Ultralytics (default)
2. Optional Roboflow hosted inference fallback (used when local model is missing or returns no detections)

### Local model selection

- Set `LEGO_MODEL_PATH` to force a model file (absolute path, or path relative to `models/`).
- If `LEGO_MODEL_PATH` is not set, the app auto-selects the best `.pt` in `models/` using LEGO-oriented filename ranking.
- Default detection threshold is now `20%` (recommended for low-confidence LEGO scenes).

### Roboflow fallback setup (optional)

Set these environment variables before launching:

- `ROBOFLOW_API_KEY=<your_api_key>`
- `ROBOFLOW_MODEL_ID=<workspace/project/version>` (example: `craftyblocks/hex-lego-yk2pe/1`)

Optional tuning:

- `ROBOFLOW_FALLBACK=1` (default enabled)
- `ROBOFLOW_TIMEOUT_SECONDS=10`
- `ROBOFLOW_MIN_INTERVAL_SECONDS=0.4`

### External model catalog

See [MODEL_ZOO.md](MODEL_ZOO.md) for accessible LEGO detection models and links.
