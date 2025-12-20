"""
Data models for Lego Brick Detection application.
"""

from typing import List, Optional
from dataclasses import dataclass, field
from .brick import Brick

@dataclass
class LegoSet:
    """Represents a complete Lego set with its component bricks."""
    name: str
    set_number: str
    total_bricks: int
    bricks: List[Brick] = field(default_factory=list)

    def __post_init__(self):
        """Validate set data after initialization."""
        if self.total_bricks != len(self.bricks):
            raise ValueError(f"Total bricks ({self.total_bricks}) doesn't match brick list length ({len(self.bricks)})")

    def get_brick_by_part_number(self, part_number: str) -> Optional[Brick]:
        """Find a brick by its part number."""
        for brick in self.bricks:
            if brick.part_number == part_number:
                return brick
        return None

    def get_found_bricks_count(self) -> int:
        """Get the number of bricks that have been found."""
        return sum(brick.found_quantity for brick in self.bricks)

    def is_complete(self) -> bool:
        """Check if all bricks in the set have been found."""
        return all(brick.is_fully_found() for brick in self.bricks)

    def mark_brick_found(self, part_number: str, quantity: int = 1) -> bool:
        """Mark a quantity of a specific brick as found."""
        brick = self.get_brick_by_part_number(part_number)
        if brick and brick.found_quantity + quantity <= brick.quantity:
            brick.found_quantity += quantity
            return True
        return False

    def mark_brick_found_by_click(self, part_number: str) -> bool:
        """Mark one instance of a brick as found (for manual clicking)."""
        return self.mark_brick_found(part_number, 1)

    def unmark_brick_found(self, part_number: str, quantity: int = 1) -> bool:
        """Unmark a quantity of a specific brick as found."""
        brick = self.get_brick_by_part_number(part_number)
        if brick and brick.found_quantity - quantity >= 0:
            brick.found_quantity -= quantity
            return True
        return False