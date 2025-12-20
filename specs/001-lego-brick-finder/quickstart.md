# Quick Start Guide: Lego Brick Finder Application

## Prerequisites

- Python 3.11+
- Webcam or Kinect v1
- Lego set data file (Rebrickable CSV format)
- Windows/Linux/Mac OS

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd lego-brick-detection
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install additional packages for Kinect (optional)**
   ```bash
   pip install freenect
   ```

## Getting Lego Set Data

1. Visit [Rebrickable.com](https://rebrickable.com)
2. Find your Lego set
3. Download the CSV inventory file
4. Save to a known location on your computer

## Running the Application

1. **Start the application**
   ```bash
   python src/main.py
   ```

2. **Load your Lego set**
   - Click "Load Set" in the menu
   - Select your downloaded CSV file
   - Verify set information appears

3. **Configure camera**
   - Click "Configure Camera" in the menu
   - Select your webcam or Kinect
   - Click "Test" to verify video stream
   - Click "OK" to confirm

4. **Start detection**
   - Click "Start Detection"
   - Position your Lego brick pile in front of the camera
   - Watch for highlighted bricks

5. **Find bricks**
   - Detected bricks appear with colored bounding boxes
   - Click on a bounding box to mark that brick as found
   - Continue until all bricks are located

## Troubleshooting

### Camera Issues
- **No camera detected**: Ensure camera is connected and not used by other applications
- **Poor video quality**: Check lighting and camera focus
- **Kinect not working**: Install libfreenect drivers and ensure device is recognized

### Detection Issues
- **No bricks detected**: Adjust lighting, ensure bricks are clearly visible
- **False detections**: Use settings menu to adjust detection parameters
- **Slow performance**: Close other applications, check GPU availability

### Set Loading Issues
- **Invalid file format**: Ensure using Rebrickable CSV format
- **File not found**: Check file path and permissions

## Settings

Access the settings menu to adjust:
- Detection confidence threshold
- Lighting conditions
- Color sensitivity
- Minimum/maximum brick sizes

## Keyboard Shortcuts

- `Space`: Start/Stop detection
- `Esc`: Exit application
- `S`: Open settings
- `L`: Load new set

## Tips for Best Results

1. **Lighting**: Use even, bright lighting without harsh shadows
2. **Camera position**: Position camera 12-18 inches above the brick pile
3. **Brick arrangement**: Spread bricks out slightly for better individual detection
4. **Background**: Use a contrasting background color
5. **Stability**: Keep camera and pile steady during detection