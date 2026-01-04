"""
Brick model for Lego Brick Detection application.
"""

from dataclasses import dataclass
from typing import Tuple

@dataclass
class Brick:
    """Represents an individual Lego brick with its specifications."""
    part_number: str
    color: str
    quantity: int
    found_quantity: int = 0
    dimensions: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # width, length, height in studs
    
    # New properties for brick list interface
    manually_marked: bool = False           # User checked the "found manually" checkbox
    detected_in_current_frame: bool = False  # Currently detected in video frame
    last_detected_timestamp: float = 0.0    # Timestamp of last detection
    original_list_position: int = 0         # Position before reordering

    @property
    def id(self) -> str:
        """Get the brick ID (same as part number)."""
        return self.part_number

    @property
    def name(self) -> str:
        """Get the brick name (combination of color and part number)."""
        return f"{self.color} {self.part_number}"

    def __post_init__(self):
        """Validate brick data after initialization."""
        if self.quantity < 1:
            raise ValueError("Quantity must be positive")
        if self.found_quantity < 0:
            raise ValueError("Found quantity cannot be negative")
        if self.found_quantity > self.quantity:
            raise ValueError("Found quantity cannot exceed total quantity")

    def is_fully_found(self) -> bool:
        """Check if all instances of this brick have been found."""
        return self.found_quantity >= self.quantity

    def get_remaining_quantity(self) -> int:
        """Get the number of this brick still needed."""
        return max(0, self.quantity - self.found_quantity)

    def can_mark_found(self, additional_quantity: int = 1) -> bool:
        """Check if additional quantity can be marked as found."""
        return self.found_quantity + additional_quantity <= self.quantity
    
    def mark_as_manually_found(self) -> None:
        """Mark this brick as manually found (checkbox checked)."""
        self.manually_marked = True
    
    def unmark_manually_found(self) -> None:
        """Remove manual found marking."""
        self.manually_marked = False
    
    def set_detected(self, timestamp: float) -> None:
        """Mark as detected in current frame."""
        self.detected_in_current_frame = True
        self.last_detected_timestamp = timestamp
    
    def clear_detected(self) -> None:
        """Clear detection status."""
        self.detected_in_current_frame = False
    
    def should_be_detected(self) -> bool:
        """Check if this brick should be included in detection."""
        return not self.manually_marked and not self.is_fully_found()