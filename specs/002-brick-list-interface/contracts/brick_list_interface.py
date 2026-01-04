"""
Component Interface Contracts for Brick List Widget
This file defines the public interfaces for the brick list components.
"""

from typing import Protocol, List, Set, Optional
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget
from src.models.brick import Brick
from src.models.lego_set import LegoSet


class IBrickListWidget(Protocol):
    """
    Interface for the main brick list widget component.
    
    Responsibilities:
    - Display list of bricks from a loaded set
    - Handle user interactions (clicks, checkbox toggles)
    - Update display based on detection events
    - Maintain list ordering (detected bricks at top)
    - Emit signals for state changes
    """
    
    # Signals
    brick_counter_changed: pyqtSignal  # (part_number: str, new_count: int)
    brick_manually_marked: pyqtSignal  # (part_number: str, is_marked: bool)
    brick_selected: pyqtSignal  # (part_number: str)
    
    def load_set(self, lego_set: LegoSet) -> None:
        """
        Load a Lego set and populate the list with its bricks.
        
        Args:
            lego_set: The LegoSet object containing bricks to display
            
        Post-conditions:
            - List is populated with one item per brick
            - Items display preview images, checkboxes, counters
            - Original order is preserved
            - Images are loaded (or placeholders shown)
        """
        ...
    
    def clear_list(self) -> None:
        """
        Clear all items from the list.
        
        Post-conditions:
            - List is empty
            - All cached state is reset
        """
        ...
    
    def update_detection_status(self, detected_part_numbers: Set[str]) -> None:
        """
        Update which bricks are currently detected in the video frame.
        
        Args:
            detected_part_numbers: Set of part numbers currently detected
            
        Post-conditions:
            - Detected bricks show detection icon
            - Detected bricks are moved to top of list
            - Previously detected but now undetected bricks return to original position
            - Update is batched (may not be immediate)
        """
        ...
    
    def increment_brick_counter(self, part_number: str) -> bool:
        """
        Increment the found counter for a specific brick.
        
        Args:
            part_number: The brick part number to increment
            
        Returns:
            True if successful, False if brick not found or already at max
            
        Post-conditions:
            - Brick's found_quantity increases by 1
            - Display updates to show new count
            - Green highlight applied if count reaches required quantity
            - brick_counter_changed signal emitted
        """
        ...
    
    def decrement_brick_counter(self, part_number: str) -> bool:
        """
        Decrement the found counter for a specific brick.
        
        Args:
            part_number: The brick part number to decrement
            
        Returns:
            True if successful, False if brick not found or already at 0
            
        Post-conditions:
            - Brick's found_quantity decreases by 1
            - Display updates to show new count
            - Green highlight removed if count drops below required quantity
            - brick_counter_changed signal emitted
        """
        ...
    
    def get_current_progress(self) -> tuple[int, int]:
        """
        Get current collection progress.
        
        Returns:
            Tuple of (found_count, total_required)
        """
        ...


class IBrickListItem(Protocol):
    """
    Interface for individual brick list item widgets.
    
    Responsibilities:
    - Display brick information (image, ID, name, counter)
    - Handle user clicks (left/right) for counter updates
    - Show detection status via icon
    - Display manual marking checkbox
    - Apply completion highlighting
    """
    
    # Signals
    counter_incremented: pyqtSignal  # ()
    counter_decremented: pyqtSignal  # ()
    manually_marked_changed: pyqtSignal  # (is_marked: bool)
    
    def set_brick(self, brick: Brick) -> None:
        """
        Set the brick data for this list item.
        
        Args:
            brick: The Brick object to display
            
        Post-conditions:
            - All UI elements updated to reflect brick data
            - Preview image loaded (or placeholder shown)
            - Counter shows current/required quantities
            - Checkbox reflects manual marking status
        """
        ...
    
    def update_counter_display(self, found_count: int, required_count: int) -> None:
        """
        Update the counter display.
        
        Args:
            found_count: Current number found
            required_count: Total number required
            
        Post-conditions:
            - Counter shows "found_count/required_count"
            - Green highlight applied if found_count == required_count
        """
        ...
    
    def set_detection_status(self, is_detected: bool) -> None:
        """
        Update the detection status indicator.
        
        Args:
            is_detected: Whether brick is currently detected
            
        Post-conditions:
            - Detection icon visible if is_detected=True
            - Detection icon hidden if is_detected=False
        """
        ...
    
    def set_manual_marking(self, is_marked: bool) -> None:
        """
        Update the manual marking checkbox.
        
        Args:
            is_marked: Whether brick is manually marked as found
            
        Post-conditions:
            - Checkbox checked if is_marked=True
            - Checkbox unchecked if is_marked=False
        """
        ...
    
    def get_brick_id(self) -> str:
        """
        Get the part number of this brick.
        
        Returns:
            The brick's part number
        """
        ...


class IImageCache(Protocol):
    """
    Interface for brick image caching component.
    
    Responsibilities:
    - Load brick preview images from disk
    - Cache images in memory (LRU)
    - Generate placeholders for missing images
    - Provide scaled images for display
    """
    
    def get_image(self, part_number: str) -> 'QPixmap':
        """
        Get a brick preview image by part number.
        
        Args:
            part_number: The brick part number
            
        Returns:
            QPixmap containing the brick image or a placeholder
            
        Post-conditions:
            - Image is cached for future requests
            - Placeholder returned if image file not found
            - Image scaled to target size (48x48 by default)
        """
        ...
    
    def preload_images(self, part_numbers: List[str]) -> None:
        """
        Preload images for the given part numbers (background operation).
        
        Args:
            part_numbers: List of part numbers to preload
            
        Post-conditions:
            - Images loaded asynchronously
            - Cache populated for future get_image() calls
        """
        ...
    
    def clear_cache(self) -> None:
        """
        Clear all cached images.
        
        Post-conditions:
            - All cached images removed from memory
            - Cache size reset to 0
        """
        ...
    
    def get_cache_size(self) -> int:
        """
        Get the number of images currently cached.
        
        Returns:
            Number of cached images
        """
        ...


# Detection Event Data Structures

class DetectionEvent:
    """
    Represents a single brick detection event from the vision system.
    
    Attributes:
        part_number: The detected brick's part number
        confidence: Detection confidence score (0.0 to 1.0)
        timestamp: Detection timestamp (seconds since epoch)
        bounding_box: Optional (x, y, width, height) of detection region
    """
    part_number: str
    confidence: float
    timestamp: float
    bounding_box: Optional[tuple[int, int, int, int]]


# Configuration

class BrickListConfig:
    """
    Configuration for brick list widget appearance and behavior.
    
    Attributes:
        item_height: Height of each list item in pixels (default: 60)
        image_size: Size of preview images in pixels (default: (48, 48))
        update_batch_interval: Detection update batching interval in ms (default: 100)
        max_image_cache_size: Maximum number of cached images (default: 100)
        completion_highlight_color: RGB color for completed bricks (default: (212, 237, 218))
        detection_icon_path: Path to detection indicator icon
        enable_animations: Whether to animate list reordering (default: False)
    """
    item_height: int = 60
    image_size: tuple[int, int] = (48, 48)
    update_batch_interval: int = 100
    max_image_cache_size: int = 100
    completion_highlight_color: tuple[int, int, int] = (212, 237, 218)
    detection_icon_path: str = "assets/icons/detected.png"
    enable_animations: bool = False


# Usage Example (for documentation purposes)

"""
Example: Integrating BrickListWidget into the main window

from src.gui.brick_list_widget import BrickListWidget
from src.models.lego_set import LegoSet

# In MainWindow.__init__
self.brick_list = BrickListWidget(config=BrickListConfig())
self.layout.addWidget(self.brick_list)

# Connect signals
self.brick_list.brick_counter_changed.connect(self._on_counter_changed)
self.brick_list.brick_manually_marked.connect(self._on_manual_marked)

# Load a set
lego_set = load_set_from_csv("data/sample_3005.csv")
self.brick_list.load_set(lego_set)

# Wire detection updates
self.detection_engine.brick_detected.connect(
    lambda part_num: self.brick_list.update_detection_status({part_num})
)
"""
