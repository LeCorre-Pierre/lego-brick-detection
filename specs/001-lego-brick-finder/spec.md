# Feature Specification: Lego Brick Finder Application

**Feature Branch**: `001-lego-brick-finder`  
**Created**: 2025-12-20  
**Status**: Draft  
**Input**: User description: "Build an application permitting me to find very fast the bricks of my lego set which are mixed within a huge pile of random other bricks.

 The application permits to load a set of Lego bricks coming from the formats of the majors brick providers: Rebrickable, Brickset, BrickLink, Peeron, BrickOwl, Brickstore.
   The retrieval of the set file is manual. You are not requested to create a connexion to those site.
   You are requested to select the most suitable format among existing one and support its opening and processing.
   Once loaded, basic information are displayed like model name, number of bricks and any information pertinent for the end user present in the file.

 The application permits to connect to the end user webcam or kinect indiferently.
   A dedicated menu permits to select the video source and make the necessary configuration.
   At this stage, a simple test is performed to verify the video stream is correctly received.

Once those 2 elements are configured, the application is ready to use.
 The end user just has to put the bricks pile in front of the camera and start the detection.
 The application will display in real time the video stream with detected bricks highlighted.
 For each detected brick, a bounding box is drawn around it.
 The end user can pick up the detected bricks from the pile.
 Once a brick is picked up, the user can indicate to the application that the brick has been picked up (e.g., by clicking on it or pressing a key, or activating/deactivating the element from the list of the pieces of the set). This must be particularly easy to do.
 The application continues to detect bricks until all bricks from the set are found or the end user stops the process.

 The application should work in various lighting conditions and angles. If required, some settings can be adjusted to improve detection in specific environments but in separated menus.
 
 The detection should be robust enough to handle different scenarios and environments.

 The application should be easy to use and configure, with a simple and intuitive interface."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Load Lego Set (Priority: P1)

As a Lego builder, I want to load a Lego set file from supported providers so that I can define the bricks to find.

**Why this priority**: Essential first step to define what bricks to detect, enabling the core functionality.

**Independent Test**: Can be fully tested by loading a sample file and verifying information display, delivering value as a set viewer.

**Acceptance Scenarios**:

1. **Given** no set is loaded, **When** user selects "Load Set" from menu, **Then** a file dialog opens for selecting set files.
2. **Given** a valid Rebrickable CSV file is selected, **When** loaded, **Then** set name, total brick count, and brick list are displayed.

---

### User Story 2 - Configure Video Source (Priority: P1)

As a Lego builder, I want to select and configure webcam or Kinect as video source so that detection can work.

**Why this priority**: Required for video input, fundamental to detection process.

**Independent Test**: Can be fully tested by selecting source and verifying stream test, delivering value as a camera tester.

**Acceptance Scenarios**:

1. **Given** configuration menu is open, **When** user selects webcam, **Then** available webcams are listed and stream test succeeds.
2. **Given** Kinect is selected, **When** test button pressed, **Then** video stream is verified and displayed briefly.

---

### User Story 3 - Real-Time Brick Detection (Priority: P1)

As a Lego builder, I want to see bricks from my set detected and highlighted in real-time video so that I can identify them quickly.

**Why this priority**: Core detection functionality, primary user value.

**Independent Test**: Can be fully tested by starting detection with a pile and verifying bounding boxes appear, delivering value as a basic detector.

**Acceptance Scenarios**:

1. **Given** set loaded and camera configured, **When** user starts detection, **Then** video stream displays with real-time updates.
2. **Given** a brick from the set is in view, **When** detected, **Then** a bounding box is drawn around it with brick identifier.

---

### User Story 4 - Mark Bricks as Picked (Priority: P1)

As a Lego builder, I want to easily mark detected bricks as picked up so that they are not re-detected.

**Why this priority**: Enables progress tracking and prevents confusion during building.

**Independent Test**: Can be fully tested by detecting a brick, clicking its box, and verifying it's no longer detected, delivering value as interactive finder.

**Acceptance Scenarios**:

1. **Given** a brick is detected with bounding box, **When** user clicks on the box, **Then** the brick is marked as picked and removed from detection.
2. **Given** multiple bricks detected, **When** user clicks each box, **Then** each is individually marked without affecting others.

---

### User Story 5 - Adjust Detection Settings (Priority: P2)

As a Lego builder, I want to adjust settings for lighting and angles so that detection works better in my environment.

**Why this priority**: Improves robustness and user experience in varied conditions.

**Independent Test**: Can be fully tested by changing settings and observing detection changes, delivering value as customizable detector.

**Acceptance Scenarios**:

1. **Given** settings menu is open, **When** user adjusts lighting parameters, **Then** detection adapts to new conditions.
2. **Given** angle settings changed, **When** bricks viewed from different angles, **Then** detection accuracy improves.

### Edge Cases

- What happens when an invalid or corrupted set file is loaded? System should display error message and allow retry.
- How does system handle no available cameras? Display error and suggest checking connections.
- What if no bricks from the set are detected in the pile? Continue scanning and show "No matches found" status.
- What if multiple identical bricks are present? Detect all instances and allow individual marking.
- What if user picks up brick but forgets to mark it? System may re-detect, but user can mark later.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support loading and parsing Rebrickable CSV format set files.
- **FR-002**: System MUST display set name, total brick count, and detailed brick list with quantities.
- **FR-003**: System MUST provide menu to select between webcam and Kinect video sources.
- **FR-004**: System MUST perform connectivity test for selected video source and display stream preview.
- **FR-005**: System MUST process video stream in real-time for brick detection.
- **FR-006**: System MUST draw colored bounding boxes around detected bricks with brick identifiers.
- **FR-007**: System MUST allow users to mark bricks as picked by clicking on their bounding boxes.
- **FR-008**: System MUST track found bricks and stop detection when all set bricks are located or user manually stops.
- **FR-009**: System MUST provide separate settings menu for adjusting detection parameters (lighting, angles).
- **FR-010**: System MUST maintain intuitive interface with clear menus and minimal steps for setup.

### Key Entities *(include if feature involves data)*

- **LegoSet**: Represents a Lego set with name, set number, and collection of required bricks.
- **Brick**: Represents individual brick with part number, color, quantity needed, and detection status.
- **DetectionResult**: Represents a detected brick instance with position coordinates, confidence score, and associated brick info.
- **VideoSource**: Represents camera configuration with type (webcam/Kinect), device ID, and stream settings.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can load and display a Lego set file in under 5 seconds on standard hardware.
- **SC-002**: Detection achieves >80% accuracy for standard Lego bricks in good lighting conditions.
- **SC-003**: User interface responds to all actions (clicks, menu selections) in under 1 second.
- **SC-004**: System maintains detection functionality in 90% of tested lighting and viewing angle variations.
- **SC-005**: 95% of users complete initial setup (load set + configure camera) without requiring external help.
