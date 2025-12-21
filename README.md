# Lego Brick Detection

A Python project for detecting Lego bricks using machine learning and computer vision.

## Constitution

See [.specify/memory/constitution.md](.specify/memory/constitution.md) for project principles and guidelines.

## Installation

1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`

## Usage

Run the detection script: `python src/detect.py`

## Project Structure

- `src/`: Source code
- `tests/`: Unit tests
- `data/`: Dataset and images
- `models/`: Trained models
- `notebooks/`: Jupyter notebooks for experimentation


/speckit.specify

## Focus on start of the application

The application starts very rapidly and is responsible immediatly.
The user can then load a Lego set file and configure the video source before starting real-time detection from command line. This must not prevent the applicaiton from starting quickly.
The loading of the models and other heavy initialization should be deferred to the background after the UI is responsive. This must not prevent the UI from being responsive.
Once loaded, the model should not be unloaded until the application exits. This permits to the user to start/stop detection multiple times without reloading the model each time, leading to a very reactive interface.