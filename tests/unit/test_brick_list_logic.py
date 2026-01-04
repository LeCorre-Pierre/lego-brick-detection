"""
Unit tests for BrickListWidget counter logic.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from src.models.brick import Brick
from src.models.lego_set import LegoSet
from src.gui.brick_list_widget import BrickListWidget


# Create QApplication instance (required for Qt widgets)
app = QApplication(sys.argv)


def test_increment_counter_basic():
    """Test basic counter increment functionality."""
    brick = Brick(
        part_number="3005",
        color="Red",
        quantity=5,
        found_quantity=0
    )
    lego_set = LegoSet(name="Test Set", set_number="12345", total_bricks=1, bricks=[brick])
    
    widget = BrickListWidget()
    widget.load_set(lego_set)
    
    # Increment counter
    widget.increment_brick_counter("3005")
    
    assert brick.found_quantity == 1, f"Expected found_quantity=1, got {brick.found_quantity}"
    print("✓ test_increment_counter_basic passed")


def test_increment_counter_max_limit():
    """Test that counter cannot exceed required quantity."""
    brick = Brick(
        part_number="3005",
        color="Red",
        quantity=2,
        found_quantity=2  # Already at max
    )
    lego_set = LegoSet(name="Test Set", set_number="12345", total_bricks=1, bricks=[brick])
    
    widget = BrickListWidget()
    widget.load_set(lego_set)
    
    # Try to increment beyond max
    widget.increment_brick_counter("3005")
    
    assert brick.found_quantity == 2, f"Expected found_quantity=2 (max), got {brick.found_quantity}"
    print("✓ test_increment_counter_max_limit passed")


def test_decrement_counter_basic():
    """Test basic counter decrement functionality."""
    brick = Brick(
        part_number="3005",
        color="Red",
        quantity=5,
        found_quantity=3
    )
    lego_set = LegoSet(name="Test Set", set_number="12345", total_bricks=1, bricks=[brick])
    
    widget = BrickListWidget()
    widget.load_set(lego_set)
    
    # Decrement counter
    widget.decrement_brick_counter("3005")
    
    assert brick.found_quantity == 2, f"Expected found_quantity=2, got {brick.found_quantity}"
    print("✓ test_decrement_counter_basic passed")


def test_decrement_counter_min_limit():
    """Test that counter cannot go below zero."""
    brick = Brick(
        part_number="3005",
        color="Red",
        quantity=5,
        found_quantity=0  # Already at min
    )
    lego_set = LegoSet(name="Test Set", set_number="12345", total_bricks=1, bricks=[brick])
    
    widget = BrickListWidget()
    widget.load_set(lego_set)
    
    # Try to decrement below zero
    widget.decrement_brick_counter("3005")
    
    assert brick.found_quantity == 0, f"Expected found_quantity=0 (min), got {brick.found_quantity}"
    print("✓ test_decrement_counter_min_limit passed")


def test_counter_signal_emission():
    """Test that brick_counter_changed signal is emitted."""
    brick = Brick(
        part_number="3005",
        color="Red",
        quantity=5,
        found_quantity=0
    )
    lego_set = LegoSet(name="Test Set", set_number="12345", total_bricks=1, bricks=[brick])
    
    widget = BrickListWidget()
    widget.load_set(lego_set)
    
    # Track signal emissions
    signal_received = []
    widget.brick_counter_changed.connect(
        lambda pn, count: signal_received.append((pn, count))
    )
    
    # Increment and check signal
    widget.increment_brick_counter("3005")
    
    assert len(signal_received) == 1, f"Expected 1 signal, got {len(signal_received)}"
    assert signal_received[0] == ("3005", 1), f"Expected ('3005', 1), got {signal_received[0]}"
    print("✓ test_counter_signal_emission passed")


def test_get_current_progress():
    """Test progress tracking calculation."""
    bricks = [
        Brick(part_number="3005", color="Red", quantity=5, found_quantity=3),
        Brick(part_number="3004", color="Blue", quantity=10, found_quantity=7),
        Brick(part_number="3003", color="Green", quantity=3, found_quantity=0),
    ]
    lego_set = LegoSet(name="Test Set", set_number="12345", total_bricks=3, bricks=bricks)
    
    widget = BrickListWidget()
    widget.load_set(lego_set)
    
    found, total = widget.get_current_progress()
    
    assert found == 10, f"Expected found=10, got {found}"
    assert total == 18, f"Expected total=18, got {total}"
    print("✓ test_get_current_progress passed")


def test_multiple_increments():
    """Test multiple increments on same brick."""
    brick = Brick(
        part_number="3005",
        color="Red",
        quantity=5,
        found_quantity=0
    )
    lego_set = LegoSet(name="Test Set", set_number="12345", total_bricks=1, bricks=[brick])
    
    widget = BrickListWidget()
    widget.load_set(lego_set)
    
    # Increment multiple times
    for i in range(3):
        widget.increment_brick_counter("3005")
    
    assert brick.found_quantity == 3, f"Expected found_quantity=3, got {brick.found_quantity}"
    print("✓ test_multiple_increments passed")


def test_increment_decrement_sequence():
    """Test alternating increment and decrement operations."""
    brick = Brick(
        part_number="3005",
        color="Red",
        quantity=5,
        found_quantity=2
    )
    lego_set = LegoSet(name="Test Set", set_number="12345", total_bricks=1, bricks=[brick])
    
    widget = BrickListWidget()
    widget.load_set(lego_set)
    
    # Sequence: +1, +1, -1, +1, -1
    widget.increment_brick_counter("3005")  # 2 -> 3
    widget.increment_brick_counter("3005")  # 3 -> 4
    widget.decrement_brick_counter("3005")  # 4 -> 3
    widget.increment_brick_counter("3005")  # 3 -> 4
    widget.decrement_brick_counter("3005")  # 4 -> 3
    
    assert brick.found_quantity == 3, f"Expected found_quantity=3, got {brick.found_quantity}"
    print("✓ test_increment_decrement_sequence passed")


def test_nonexistent_brick():
    """Test handling of nonexistent brick part number."""
    brick = Brick(
        part_number="3005",
        color="Red",
        quantity=5,
        found_quantity=0
    )
    lego_set = LegoSet(name="Test Set", set_number="12345", total_bricks=1, bricks=[brick])
    
    widget = BrickListWidget()
    widget.load_set(lego_set)
    
    # Try to increment nonexistent brick
    widget.increment_brick_counter("9999")
    
    # Original brick should be unchanged
    assert brick.found_quantity == 0, f"Expected found_quantity=0, got {brick.found_quantity}"
    print("✓ test_nonexistent_brick passed")


def test_counter_with_empty_set():
    """Test counter operations with no set loaded."""
    widget = BrickListWidget()
    
    # Should not crash with no set loaded
    widget.increment_brick_counter("3005")
    widget.decrement_brick_counter("3005")
    
    found, total = widget.get_current_progress()
    assert found == 0 and total == 0, "Expected (0, 0) for empty set"
    print("✓ test_counter_with_empty_set passed")


if __name__ == "__main__":
    print("Running BrickListWidget counter logic tests...\n")
    
    test_increment_counter_basic()
    test_increment_counter_max_limit()
    test_decrement_counter_basic()
    test_decrement_counter_min_limit()
    test_counter_signal_emission()
    test_get_current_progress()
    test_multiple_increments()
    test_increment_decrement_sequence()
    test_nonexistent_brick()
    test_counter_with_empty_set()
    
    print("\n✅ All tests passed!")
