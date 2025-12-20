# Detection Contracts: Lego Brick Finder Application

## Overview

Defines the interface contracts for detection algorithms and computer vision processing.

## BrickDetector Contract

### Interface: BrickDetector
**Purpose**: Core detection engine for identifying Lego bricks in video frames.

**Methods**:
- `vector<DetectionResult> detectBricks(Mat frame, LegoSet targetSet)` - Detect bricks in frame
  - **Parameters**:
    - frame: Current video frame (BGR format)
    - targetSet: Lego set to search for
  - **Returns**: List of detection results with confidence scores
  - **Performance**: Must complete within 100ms for 30fps operation

- `void setDetectionParameters(DetectionParams params)` - Configure detection settings
  - **Parameters**: Struct with lighting, angle, and sensitivity settings
  - **Postconditions**: Subsequent detections use new parameters

- `bool isBrickFound(Brick brick)` - Check if brick type already found
  - **Returns**: True if sufficient quantity of this brick type located

### Dependencies
- OpenCV for image processing
- Numpy for numerical operations

## SetLoader Contract

### Interface: SetLoader
**Purpose**: Load and parse Lego set data from various formats.

**Methods**:
- `LegoSet loadFromCSV(string filePath)` - Load set from Rebrickable CSV
  - **Parameters**: Path to CSV file
  - **Returns**: Parsed LegoSet object
  - **Throws**: FileNotFoundException, InvalidFormatException
  - **Format**: Expected columns: part_num, color_name, quantity, etc.

- `bool validateSet(LegoSet set)` - Verify set data integrity
  - **Returns**: True if all bricks have valid data
  - **Postconditions**: Error details available if validation fails

## VideoProcessor Contract

### Interface: VideoProcessor
**Purpose**: Handle video capture and preprocessing.

**Methods**:
- `bool initialize(VideoSource source)` - Setup video capture
  - **Parameters**: Video source configuration
  - **Returns**: True if initialization successful
  - **Postconditions**: Ready to capture frames

- `Mat captureFrame()` - Get next video frame
  - **Returns**: Current frame in BGR format
  - **Throws**: CaptureException if device unavailable

- `void release()` - Clean up video resources
  - **Postconditions**: Device released, resources freed

### Supported Formats
- Webcam: Standard USB cameras via OpenCV VideoCapture
- Kinect: RGB stream via libfreenect integration

## DetectionParams Structure

```python
@dataclass
class DetectionParams:
    min_confidence: float = 0.7  # Minimum detection confidence
    lighting_mode: str = "auto"  # "bright", "dim", "auto"
    angle_tolerance: int = 15    # Degrees of rotation tolerance
    color_threshold: int = 30    # Color matching sensitivity
    min_brick_size: int = 20     # Minimum pixel size for detection
    max_brick_size: int = 200    # Maximum pixel size for detection
```

## Error Handling

All detection methods must handle:
- Invalid input frames (wrong dimensions, corrupted data)
- Camera disconnection during operation
- Insufficient lighting conditions
- Memory allocation failures
- Thread interruption requests