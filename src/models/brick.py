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