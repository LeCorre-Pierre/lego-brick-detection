# Feature Specification: Bricks in Set List Interface

**Feature Branch**: `002-brick-list-interface`  
**Created**: January 4, 2026  
**Status**: Draft  
**Input**: User description: "The interface containing the list of bricks 'Bricks in Set' permits to easily identify the bricks from the loaded set with preview images, checkboxes for manual marking, detection pictograms, counters for tracking progress, and dynamic sorting"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Track Brick Collection Progress (Priority: P1)

As a user building a Lego set, I want to track which bricks I've collected so that I can see my progress and know which bricks I still need to find.

**Why this priority**: This is the core functionality that delivers immediate value - allowing users to track their progress in completing a Lego set. Without this, the list would be just static information without interaction.

**Independent Test**: Can be fully tested by loading a set, clicking on brick entries to increment counters, and verifying that bricks turn green when the required count is reached. Delivers immediate value as a progress tracker even without detection features.

**Acceptance Scenarios**:

1. **Given** a Lego set is loaded with required brick quantities, **When** the user views the "Bricks in Set" list, **Then** each brick displays with a counter initialized to 0 and shows the total required quantity
2. **Given** a brick entry in the list, **When** the user left-clicks on the entry, **Then** the counter increments by one
3. **Given** a brick counter has reached the required quantity, **When** the user views the list, **Then** that brick entry is highlighted in green to indicate completion
4. **Given** a brick entry with a counter greater than zero, **When** the user right-clicks on the entry, **Then** the counter decrements by one (minimum value is zero)
5. **Given** multiple bricks with various counter values, **When** the user views the list, **Then** each brick shows its current count versus required count (e.g., "3/5")

---

### User Story 2 - Manual Brick Marking (Priority: P2)

As a user physically sorting bricks, I want to manually mark bricks as found so that the detection system doesn't need to look for them and I can focus on finding remaining pieces.

**Why this priority**: This provides flexibility for mixed workflows where users might manually sort some bricks while relying on detection for others. It enhances usability but the core tracking (P1) is still valuable without it.

**Independent Test**: Can be tested by loading a set, checking/unchecking brick checkboxes, and verifying that checked bricks are excluded from detection attempts. Provides independent value as a manual inventory management tool.

**Acceptance Scenarios**:

1. **Given** a brick entry in the list, **When** the user clicks the checkbox next to the brick, **Then** the checkbox becomes checked and the brick is marked as "found manually"
2. **Given** a brick is marked as found manually, **When** the detection system processes video frames, **Then** that brick is excluded from detection attempts
3. **Given** a checked brick, **When** the user clicks the checkbox again, **Then** the checkbox becomes unchecked and the brick returns to normal detection mode
4. **Given** a brick is manually marked as found, **When** the user views the list, **Then** there is clear visual indication that this brick was manually marked (distinct from detection-based marking)

---

### User Story 3 - Visual Detection Feedback (Priority: P1)

As a user pointing my camera at bricks, I want to see immediate visual feedback when a brick is detected so that I know the system is working and can quickly identify which bricks have been found.

**Why this priority**: This is essential for the AI-powered detection workflow and provides real-time feedback that makes the system feel responsive and useful. It's critical for user confidence in the system.

**Independent Test**: Can be tested by running detection on video frames containing known bricks and verifying that detected bricks show the detection pictogram and move to the top of the list. Delivers immediate value as a real-time detection indicator.

**Acceptance Scenarios**:

1. **Given** the detection system is running on a video frame, **When** a brick in the current set is detected, **Then** the corresponding brick entry displays a detection pictogram indicating active detection
2. **Given** a brick is detected in the current video frame, **When** the user views the list, **Then** that brick entry is moved to the top of the list for increased visibility
3. **Given** multiple bricks are detected simultaneously, **When** the user views the list, **Then** all detected bricks appear at the top of the list (order among detected bricks can follow detection confidence or original list order)
4. **Given** a brick was previously detected but is no longer in the current frame, **When** the user views the list, **Then** the detection pictogram is removed and the brick returns to its original position in the list
5. **Given** a brick is detected multiple times across frames, **When** the user views the list, **Then** the brick remains at the top with the detection pictogram consistently displayed

---

### User Story 4 - Brick Identification (Priority: P1)

As a user working with many similar-looking bricks, I want to see preview images, IDs, and names for each brick so that I can quickly identify which brick I'm looking for.

**Why this priority**: This is fundamental information display that makes the list usable. Without it, users cannot identify which bricks they need to find. This is a prerequisite for all other functionality.

**Independent Test**: Can be tested by loading a set and verifying that each brick displays its preview image, ID, name, and required quantity. Delivers value as a reference guide even without any interactive features.

**Acceptance Scenarios**:

1. **Given** a Lego set is loaded, **When** the user views the "Bricks in Set" list, **Then** each brick entry displays a preview image on the left side
2. **Given** a brick entry in the list, **When** the user views the entry, **Then** the preview image height matches the line height for a compact layout
3. **Given** a brick entry, **When** the user views the entry, **Then** the brick ID is displayed prominently for identification
4. **Given** a brick entry, **When** the user views the entry, **Then** the brick name/description is displayed for easy recognition
5. **Given** multiple brick entries, **When** the user views the list, **Then** all entries maintain consistent spacing and alignment for easy scanning

---

### Edge Cases

- What happens when a user left-clicks to increment a counter that is already at the required quantity? (Counter should stop at required quantity or optionally allow overcounting to track excess pieces)
- What happens when a brick is detected but the user has already manually marked it as found? (Manual marking should take precedence - no detection pictogram shown)
- What happens when the detection system detects a brick that already has its required count completed? (Detection pictogram should still show, but the green highlight indicates completion)
- How does the system handle bricks with very long names that might overflow the layout? (Text should truncate with ellipsis or wrap to maintain layout integrity)
- What happens when multiple bricks are detected simultaneously and need to move to the top? (All detected bricks move to top, maintaining relative order or sorting by detection confidence)
- What happens if a user right-clicks on a brick entry with a counter at zero? (Counter stays at zero - cannot go negative)
- What happens when preview images fail to load or are unavailable? (Display a placeholder icon or the brick ID as fallback)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a list of all bricks required for the currently loaded Lego set
- **FR-002**: Each brick entry MUST display a preview image sized to match the line height for compact layout
- **FR-003**: Each brick entry MUST display a checkbox for manual marking as found
- **FR-004**: Each brick entry MUST display the brick ID for identification
- **FR-005**: Each brick entry MUST display the brick name/description
- **FR-006**: Each brick entry MUST display a counter showing current count versus required quantity (format: "X/Y" where X is current and Y is required)
- **FR-007**: Each brick entry MUST display a detection pictogram that indicates whether the brick is currently detected in the video frame
- **FR-008**: Counter MUST initialize to zero when a set is first loaded
- **FR-009**: System MUST increment a brick's counter by one when the user left-clicks on the brick entry
- **FR-010**: System MUST decrement a brick's counter by one when the user right-clicks on the brick entry (minimum value is zero)
- **FR-011**: System MUST highlight brick entries in green when the counter reaches the required quantity
- **FR-012**: System MUST allow users to check/uncheck the checkbox to mark bricks as manually found
- **FR-013**: System MUST exclude manually marked bricks from automatic detection processing
- **FR-014**: System MUST display a detection pictogram on brick entries when the corresponding brick is detected in the current video frame
- **FR-015**: System MUST move detected brick entries to the top of the list for increased visibility
- **FR-016**: System MUST remove the detection pictogram and return bricks to their original position when they are no longer detected in the current frame
- **FR-017**: System MUST maintain consistent layout and spacing across all brick entries for easy scanning
- **FR-018**: System MUST handle text overflow appropriately (truncate or wrap) to maintain layout integrity

### Key Entities *(include if feature involves data)*

- **Brick**: Represents an individual Lego piece with properties including ID, name, preview image reference, required quantity for the set, current collected count, manual marking status, and current detection status
- **Lego Set**: Contains a collection of Bricks with their required quantities, set name, and set ID
- **Detection Event**: Represents a brick detection occurrence in a video frame, including brick ID, timestamp, and detection confidence
- **List Entry State**: Maintains the display state for each brick including position in list, highlighting status, checkbox state, counter value, and detection pictogram visibility

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can identify any brick in a loaded set within 3 seconds by viewing the list with preview images, IDs, and names
- **SC-002**: Users can track collection progress for a 50-brick set by incrementing/decrementing counters in under 1 minute
- **SC-003**: Detected bricks appear at the top of the list within 500 milliseconds of detection to provide real-time feedback
- **SC-004**: 95% of users successfully understand the difference between manually marked bricks and detected bricks based on visual indicators alone
- **SC-005**: Users can complete a full set inventory (marking all bricks as found either manually or through detection) without requiring any help documentation
- **SC-006**: The list remains responsive and updates smoothly even with sets containing 100+ brick types
- **SC-007**: Users report improved efficiency in brick sorting tasks by at least 40% compared to manual checking against printed instructions

## Assumptions *(mandatory)*

- Brick preview images are available in a standard image format (PNG, JPG) from the set data source
- The detection system provides real-time brick identification with brick IDs that match the loaded set data
- Users have sufficient screen space to display the brick list alongside video feed (minimum screen width: 1024px or responsive mobile layout)
- Set data includes brick IDs, names, and required quantities in a structured format
- The detection system can process video frames and identify multiple bricks per frame
- Users interact with the list using standard mouse/touch input (left-click, right-click, or equivalent touch gestures)
- Brick IDs from the detection system are consistent with brick IDs in the loaded set data
- The application maintains state across user sessions so progress is not lost

## Out of Scope *(optional)*

- Editing set data (adding/removing bricks, changing required quantities) - users work with pre-defined sets only
- Exporting or sharing progress data with other users
- Undo/redo functionality for counter changes
- Keyboard navigation or accessibility features (will be addressed in a separate feature)
- Advanced filtering or searching within the brick list
- Custom sorting options beyond detection-based reordering
- Detailed history of when/how bricks were marked as found
- Integration with online Lego databases or automatic set loading by set number
- Multi-set management or switching between sets
- Brick substitution suggestions when specific bricks are unavailable

## Dependencies *(optional)*

- Set data loading functionality must be implemented to provide brick information
- Detection engine must be operational and capable of identifying bricks from video frames
- Video capture/processing pipeline must be active to provide frames for detection
- Image loading system must be able to fetch and display brick preview images
- UI framework must support list rendering, event handling (click, right-click), and dynamic reordering

## Technical Constraints *(optional)*

- List must render efficiently for sets with up to 200 unique brick types
- Detection updates must not cause visible lag or stuttering in the UI (target: 30fps minimum)
- Preview images should be cached to avoid repeated loading from disk/network
- The list component should work on both desktop (mouse) and mobile (touch) interfaces
- Layout must be responsive to accommodate different screen sizes while maintaining usability

## Open Questions *(optional)*

None at this time. All key aspects of the feature are clearly defined.
