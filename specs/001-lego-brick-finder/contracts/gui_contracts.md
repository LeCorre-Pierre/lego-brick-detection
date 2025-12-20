# GUI Contracts: Lego Brick Finder Application

## Overview

Defines the interface contracts for GUI components, ensuring consistent interaction between UI elements and business logic.

## MainWindow Contract

### Interface: MainWindow
**Purpose**: Primary application window managing all UI components.

**Methods**:
- `void loadSet(string filePath)` - Load Lego set from file
  - **Preconditions**: Valid file path to supported format
  - **Postconditions**: Set data displayed, detection enabled
  - **Error Handling**: Display error dialog for invalid files

- `void configureCamera()` - Open camera configuration dialog
  - **Preconditions**: None
  - **Postconditions**: Video source configured and tested
  - **Error Handling**: Display error for unavailable devices

- `void startDetection()` - Begin real-time brick detection
  - **Preconditions**: Set loaded and camera configured
  - **Postconditions**: Video stream displayed with detections
  - **Error Handling**: Display error if prerequisites not met

- `void stopDetection()` - Halt detection process
  - **Preconditions**: Detection active
  - **Postconditions**: Video stream stopped, final results displayed

- `void onBrickClicked(Point clickPosition)` - Handle user click on detected brick
  - **Parameters**: clickPosition - coordinates in video frame
  - **Postconditions**: Corresponding brick marked as found, UI updated

### Signals
- `setLoaded(LegoSet set)` - Emitted when set successfully loaded
- `detectionStarted()` - Emitted when detection begins
- `detectionStopped()` - Emitted when detection ends
- `brickFound(Brick brick)` - Emitted when brick marked as found

## VideoDisplay Contract

### Interface: VideoDisplay
**Purpose**: Widget for displaying video stream with detection overlays.

**Methods**:
- `void updateFrame(Mat frame, vector<DetectionResult> detections)` - Update display with new frame
  - **Parameters**:
    - frame: Current video frame
    - detections: Current detection results
  - **Postconditions**: Frame displayed with bounding boxes and labels

- `void setOverlayEnabled(bool enabled)` - Toggle detection overlays
  - **Postconditions**: Overlays shown/hidden accordingly

- `Point getClickPosition(QMouseEvent event)` - Convert mouse event to frame coordinates
  - **Returns**: Click position relative to video frame

### Signals
- `brickClicked(Point position)` - Emitted when user clicks on detection

## SetInfoPanel Contract

### Interface: SetInfoPanel
**Purpose**: Display current set information and progress.

**Methods**:
- `void updateSetInfo(LegoSet set)` - Display set details
  - **Postconditions**: Name, set number, total bricks shown

- `void updateProgress(map<string, int> brickProgress)` - Update found brick counts
  - **Parameters**: Map of brick part numbers to found quantities
  - **Postconditions**: Progress bars and counts updated

- `void highlightBrick(string partNumber)` - Highlight specific brick in list
  - **Postconditions**: Specified brick visually highlighted

## CameraConfigDialog Contract

### Interface: CameraConfigDialog
**Purpose**: Dialog for camera selection and configuration.

**Methods**:
- `vector<VideoDevice> scanDevices()` - Discover available video devices
  - **Returns**: List of available cameras/Kinect devices

- `bool testDevice(VideoDevice device)` - Test selected device
  - **Returns**: True if device accessible and streaming
  - **Error Handling**: Display specific error messages

- `VideoSource getConfiguration()` - Get configured video source
  - **Returns**: Complete video source configuration