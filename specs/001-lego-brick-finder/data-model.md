# Data Model: Lego Brick Finder Application

## Overview

The application manages Lego set data, brick detection results, and video source configurations. Data is primarily stored in memory during runtime with optional persistence for user preferences.

## Entities

### LegoSet
Represents a complete Lego set with its component bricks.

**Attributes**:
- `name`: String - Official set name (e.g., "Millennium Falcon")
- `set_number`: String - Unique set identifier (e.g., "75192")
- `total_bricks`: Integer - Total number of bricks in the set
- `bricks`: List[Brick] - Collection of all bricks in the set

**Relationships**:
- Contains multiple Brick entities
- Referenced by DetectionResult for matching

**Validation Rules**:
- `set_number` must be unique and non-empty
- `total_bricks` must equal length of `bricks` list
- All bricks must have valid part numbers

### Brick
Represents an individual Lego brick with its specifications.

**Attributes**:
- `part_number`: String - Official Lego part number (e.g., "3001")
- `color`: String - Brick color name (e.g., "Red", "Blue")
- `quantity`: Integer - Number of this brick needed in the set
- `found_quantity`: Integer - Number of this brick already found (default 0)
- `dimensions`: Tuple[float, float, float] - Physical dimensions in studs (width, length, height)

**Relationships**:
- Belongs to LegoSet
- Referenced by DetectionResult for identification

**Validation Rules**:
- `quantity` must be positive integer
- `found_quantity` cannot exceed `quantity`
- `part_number` must be valid Lego part identifier
- `color` must be from standard Lego color palette

### DetectionResult
Represents a detected brick instance in the video stream.

**Attributes**:
- `brick`: Brick - Reference to the matched brick type
- `bounding_box`: Tuple[int, int, int, int] - Rectangle coordinates (x, y, width, height)
- `confidence`: Float - Detection confidence score (0.0-1.0)
- `timestamp`: DateTime - When the detection occurred
- `marked_as_found`: Boolean - Whether user has confirmed this brick as found

**Relationships**:
- References Brick for identification
- Associated with VideoSource that captured it

**Validation Rules**:
- `confidence` must be between 0.0 and 1.0
- `bounding_box` coordinates must be within video frame dimensions
- `brick` must exist in current LegoSet

### VideoSource
Represents a camera or video input device configuration.

**Attributes**:
- `type`: Enum - Device type ("webcam", "kinect")
- `device_id`: Integer - OpenCV device index
- `resolution`: Tuple[int, int] - Capture resolution (width, height)
- `frame_rate`: Integer - Target frames per second
- `calibration_data`: Dict - Camera calibration parameters (optional)

**Relationships**:
- Produces DetectionResult instances

**Validation Rules**:
- `device_id` must be non-negative integer
- `resolution` dimensions must be positive
- `frame_rate` must be between 1-60 FPS

## Data Flow

1. **Set Loading**: CSV file → LegoSet + Brick entities
2. **Video Capture**: VideoSource → raw frames
3. **Detection**: frames + LegoSet → DetectionResult instances
4. **User Interaction**: DetectionResult → update Brick.found_quantity
5. **Progress Tracking**: Aggregate Brick states for completion status

## Persistence

- **Runtime**: All entities stored in memory
- **Optional**: VideoSource settings saved to user config file
- **Future**: Detection history could be logged for analytics