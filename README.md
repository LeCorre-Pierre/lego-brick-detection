# Lego Brick Detection

A Python project for detecting Lego bricks using machine learning and computer vision.

## Constitution

See [.specify/memory/constitution.md](.specify/memory/constitution.md) for project principles and guidelines.

## Installation

1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`

## Features

- Real-time video preview with start/stop controls
- Save Preview (JPG) button stores current frame in screenshoot/ with timestamp
- YOLOv8 detection toggle with bounding boxes and labels
- Detection scope control: choose to detect only bricks from the loaded set or all model classes
 - Detection menu: quick actions to toggle set-only scope and reset threshold
- **Static frame tuning**: Stop video to freeze the preview and adjust detection parameters (threshold, scope) on a static image without real-time processing overhead
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

- Use the "Detection" menu to quickly toggle "Detect Only Set Classes" and to "Reset Threshold to 50%".

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

/speckit.plan

The format of the preview image is png. 
