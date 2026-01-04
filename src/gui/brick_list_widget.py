"""
Custom list widget for displaying bricks in a set with interactive features.
Manages brick display, counter tracking, manual marking, and detection feedback.
"""

from pathlib import Path
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Optional, Set, Dict
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont
from ..models.brick import Brick
from ..models.lego_set import LegoSet
from ..utils.image_cache import ImageCache
from ..utils.logger import get_logger
from .brick_list_item import BrickListItem


@dataclass
class BrickListState:
    """Manages state for brick list display."""
    # Original ordering (before detection-based reordering)
    original_order: list[str] = field(default_factory=list)  # part_numbers
    
    # Currently detected bricks (at top of list)
    detected_bricks: Set[str] = field(default_factory=set)  # part_numbers
    
    # Pending detection updates (batched)
    pending_detections: Set[str] = field(default_factory=set)
    
    # Scroll position (to preserve during updates)
    scroll_position: int = 0


class BrickListWidget(QListWidget):
    """
    Custom list widget for displaying and interacting with bricks in a set.
    
    Features:
    - Display brick preview images, IDs, names, quantities
    - Track collection progress with counters
    - Manual marking with checkboxes
    - Detection feedback with visual indicators
    - Dynamic reordering (detected bricks at top)
    """
    
    # Signals
    brick_counter_changed = pyqtSignal(str, int)  # part_number, new_count
    brick_manually_marked = pyqtSignal(str, bool)  # part_number, is_marked
    brick_selected = pyqtSignal(str)  # part_number
    
    def __init__(self, parent=None):
        """Initialize the brick list widget."""
        super().__init__(parent)
        
        self.logger = get_logger("brick_list_widget")
        self.current_set: Optional[LegoSet] = None
        self._state = BrickListState()
        
        # Initialize image cache
        image_dir = Path("data/brick_images")
        self._image_cache = ImageCache(image_dir, max_size=100, image_size=(48, 48))
        
        # Brick items lookup (part_number -> BrickListItem)
        self._brick_items: Dict[str, BrickListItem] = {}
        
        # Setup update batching timer (for detection updates)
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self._apply_detection_updates)
        self._update_timer.start(100)  # 100ms batching interval
        
        self._setup_ui()
        self.logger.info("Brick list widget initialized")
    
    def _setup_ui(self):
        """Setup the list widget appearance."""
        # Set uniform item sizes
        self.setUniformItemSizes(True)
        
        # Enable smooth scrolling
        self.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        
        # Set selection behavior
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        
        # Style
        self.setStyleSheet("""
            QListWidget {
                border: 1px solid #cccccc;
                background-color: white;
            }
            QListWidget::item {
                border-bottom: 1px solid #eeeeee;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
    
    def load_set(self, lego_set: LegoSet) -> None:
        """
        Load a Lego set and populate the list with its bricks.
        
        Args:
            lego_set: The LegoSet object containing bricks to display
        """
        self.logger.info(f"Loading set: {lego_set.name} with {len(lego_set.bricks)} bricks")
        
        self.current_set = lego_set
        self.clear_list()
        
        # Store original order
        self._state.original_order = [brick.part_number for brick in lego_set.bricks]
        
        # Set original list positions
        for idx, brick in enumerate(lego_set.bricks):
            brick.original_list_position = idx
        
        # Add brick items
        for brick in lego_set.bricks:
            self._add_brick_item(brick)
        
        # Preload images in background
        part_numbers = [brick.part_number for brick in lego_set.bricks]
        self._image_cache.preload_images(part_numbers)
        
        self.logger.info(f"Loaded {len(lego_set.bricks)} bricks into list")
    
    def _add_brick_item(self, brick: Brick) -> None:
        """
        Create and add a BrickListItem to the list.
        
        Args:
            brick: The Brick object to display
        """
        # Create list item
        item = QListWidgetItem(self)
        item.setSizeHint(QSize(0, 60))
        
        # Create custom widget
        widget = BrickListItem(brick, self._image_cache, self)
        
        # Store reference
        self._brick_items[brick.part_number] = widget
        
        # Set widget for item
        self.setItemWidget(item, widget)
        
        # Connect signals (will be extended in later phases)
        widget.counter_incremented.connect(
            lambda pn=brick.part_number: self._on_counter_increment(pn)
        )
        widget.counter_decremented.connect(
            lambda pn=brick.part_number: self._on_counter_decrement(pn)
        )
    
    def clear_list(self) -> None:
        """Clear all items from the list."""
        self.clear()
        self._brick_items.clear()
        self._state = BrickListState()
        self.logger.info("Brick list cleared")
    
    def get_current_progress(self) -> tuple[int, int]:
        """
        Get current collection progress.
        
        Returns:
            Tuple of (found_count, total_required)
        """
        if not self.current_set:
            return (0, 0)
        
        found = self.current_set.get_found_bricks_count()
        total = sum(brick.quantity for brick in self.current_set.bricks)
        
        return (found, total)
    
    def _on_counter_increment(self, part_number: str) -> None:
        """
        Handle counter increment signal.
        
        Args:
            part_number: The brick part number
        """
        self.increment_brick_counter(part_number)
    
    def _on_counter_decrement(self, part_number: str) -> None:
        """
        Handle counter decrement signal.
        
        Args:
            part_number: The brick part number
        """
        self.decrement_brick_counter(part_number)
    
    def increment_brick_counter(self, part_number: str) -> None:
        """
        Increment the found counter for a brick.
        
        Args:
            part_number: The brick part number
        """
        if not self.current_set:
            return
        
        # Find the brick
        brick = next((b for b in self.current_set.bricks if b.part_number == part_number), None)
        if not brick:
            self.logger.warning(f"Brick {part_number} not found in current set")
            return
        
        # Validate counter (max = required quantity)
        if brick.found_quantity >= brick.quantity:
            self.logger.debug(f"Brick {part_number} already at maximum count")
            return
        
        # Increment counter
        brick.found_quantity += 1
        self.logger.debug(f"Incremented {part_number}: {brick.found_quantity}/{brick.quantity}")
        
        # Update display
        widget = self._brick_items.get(part_number)
        if widget:
            widget.update_counter_display(brick.found_quantity, brick.quantity)
        
        # Emit signal
        self.brick_counter_changed.emit(part_number, brick.found_quantity)
    
    def decrement_brick_counter(self, part_number: str) -> None:
        """
        Decrement the found counter for a brick.
        
        Args:
            part_number: The brick part number
        """
        if not self.current_set:
            return
        
        # Find the brick
        brick = next((b for b in self.current_set.bricks if b.part_number == part_number), None)
        if not brick:
            self.logger.warning(f"Brick {part_number} not found in current set")
            return
        
        # Validate counter (min = 0)
        if brick.found_quantity <= 0:
            self.logger.debug(f"Brick {part_number} already at minimum count")
            return
        
        # Decrement counter
        brick.found_quantity -= 1
        self.logger.debug(f"Decremented {part_number}: {brick.found_quantity}/{brick.quantity}")
        
        # Update display
        widget = self._brick_items.get(part_number)
        if widget:
            widget.update_counter_display(brick.found_quantity, brick.quantity)
        
        # Emit signal
        self.brick_counter_changed.emit(part_number, brick.found_quantity)
    
    def update_detection_status(self, detected_part_numbers: Set[str]) -> None:
        """
        Update which bricks are currently detected (placeholder for Phase 6).
        
        Args:
            detected_part_numbers: Set of part numbers currently detected
        """
        self._state.pending_detections = detected_part_numbers
        # Actual update will be applied by timer in Phase 6 (US3)
    
    def _apply_detection_updates(self) -> None:
        """Apply batched detection updates (placeholder for Phase 6)."""
        # Will be implemented in Phase 6 (US3)
        pass
