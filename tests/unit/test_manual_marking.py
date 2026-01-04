"""
Unit tests for manual marking functionality.
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


def test_checkbox_marks_brick():
    """Test that checking the checkbox marks the brick as manually found."""
    brick = Brick(
        part_number="3005",
        color="Red",
        quantity=5,
        found_quantity=0
    )
    lego_set = LegoSet(name="Test Set", set_number="12345", total_bricks=1, bricks=[brick])
    
    widget = BrickListWidget()
    widget.load_set(lego_set)
    
    # Get the brick list item
    brick_item = widget._brick_items.get("3005")
    assert brick_item is not None, "Brick item not found in widget"
    
    # Check the checkbox
    brick_item.manual_checkbox.setChecked(True)
    
    # Verify brick is marked as manually found
    assert brick.manually_marked == True, f"Expected manually_marked=True, got {brick.manually_marked}"
    print("✓ test_checkbox_marks_brick passed")


def test_checkbox_unmarks_brick():
    """Test that unchecking the checkbox unmarks the brick."""
    brick = Brick(
        part_number="3005",
        color="Red",
        quantity=5,
        found_quantity=0
    )
    # Mark as manually found initially
    brick.mark_as_manually_found()
    
    lego_set = LegoSet(name="Test Set", set_number="12345", total_bricks=1, bricks=[brick])
    
    widget = BrickListWidget()
    widget.load_set(lego_set)
    
    # Get the brick list item
    brick_item = widget._brick_items.get("3005")
    
    # Set checkbox to match brick state
    brick_item.set_manual_marking(True)
    
    # Uncheck the checkbox
    brick_item.manual_checkbox.setChecked(False)
    
    # Verify brick is unmarked
    assert brick.manually_marked == False, f"Expected manually_marked=False, got {brick.manually_marked}"
    print("✓ test_checkbox_unmarks_brick passed")


def test_manual_marking_signal_emission():
    """Test that manually_marked signal is emitted."""
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
    widget.brick_manually_marked.connect(
        lambda pn, is_marked: signal_received.append((pn, is_marked))
    )
    
    # Get the brick list item and check the checkbox
    brick_item = widget._brick_items.get("3005")
    brick_item.manual_checkbox.setChecked(True)
    
    assert len(signal_received) == 1, f"Expected 1 signal, got {len(signal_received)}"
    assert signal_received[0] == ("3005", True), f"Expected ('3005', True), got {signal_received[0]}"
    print("✓ test_manual_marking_signal_emission passed")


def test_set_manual_marking_programmatically():
    """Test setting manual marking state programmatically."""
    brick = Brick(
        part_number="3005",
        color="Red",
        quantity=5,
        found_quantity=0
    )
    lego_set = LegoSet(name="Test Set", set_number="12345", total_bricks=1, bricks=[brick])
    
    widget = BrickListWidget()
    widget.load_set(lego_set)
    
    # Get the brick list item
    brick_item = widget._brick_items.get("3005")
    
    # Set manual marking programmatically
    brick_item.set_manual_marking(True)
    
    # Verify checkbox is checked
    assert brick_item.manual_checkbox.isChecked() == True, "Checkbox should be checked"
    print("✓ test_set_manual_marking_programmatically passed")


def test_manual_marking_visual_style():
    """Test that manually marked bricks have distinct styling."""
    brick = Brick(
        part_number="3005",
        color="Red",
        quantity=5,
        found_quantity=0
    )
    lego_set = LegoSet(name="Test Set", set_number="12345", total_bricks=1, bricks=[brick])
    
    widget = BrickListWidget()
    widget.load_set(lego_set)
    
    # Get the brick list item
    brick_item = widget._brick_items.get("3005")
    
    # Mark as manual
    brick_item.set_manual_marking(True)
    
    # Verify style is applied (check that stylesheet is not empty)
    stylesheet = brick_item.styleSheet()
    assert "background-color: #f0f0f0" in stylesheet, "Manual marking style not applied"
    print("✓ test_manual_marking_visual_style passed")


def test_manual_marking_with_counter():
    """Test that manual marking works together with counter functionality."""
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
    assert brick.found_quantity == 1, "Counter should be incremented"
    
    # Get the brick list item and mark as manual
    brick_item = widget._brick_items.get("3005")
    brick_item.manual_checkbox.setChecked(True)
    
    # Verify both states are maintained
    assert brick.found_quantity == 1, "Counter should remain at 1"
    assert brick.manually_marked == True, "Should be manually marked"
    print("✓ test_manual_marking_with_counter passed")


def test_unmarking_restores_normal_style():
    """Test that unchecking removes manual marking style."""
    brick = Brick(
        part_number="3005",
        color="Red",
        quantity=5,
        found_quantity=0
    )
    lego_set = LegoSet(name="Test Set", set_number="12345", total_bricks=1, bricks=[brick])
    
    widget = BrickListWidget()
    widget.load_set(lego_set)
    
    # Get the brick list item
    brick_item = widget._brick_items.get("3005")
    
    # Mark and then unmark
    brick_item.set_manual_marking(True)
    assert "#f0f0f0" in brick_item.styleSheet(), "Manual style should be applied"
    
    brick_item.set_manual_marking(False)
    # Style should be removed (empty or no manual style)
    assert "#f0f0f0" not in brick_item.styleSheet(), "Manual style should be removed"
    print("✓ test_unmarking_restores_normal_style passed")


def test_multiple_bricks_manual_marking():
    """Test manual marking multiple bricks independently."""
    bricks = [
        Brick(part_number="3005", color="Red", quantity=5, found_quantity=0),
        Brick(part_number="3004", color="Blue", quantity=3, found_quantity=0),
        Brick(part_number="3003", color="Green", quantity=2, found_quantity=0),
    ]
    lego_set = LegoSet(name="Test Set", set_number="12345", total_bricks=3, bricks=bricks)
    
    widget = BrickListWidget()
    widget.load_set(lego_set)
    
    # Mark first and third bricks
    widget._brick_items.get("3005").manual_checkbox.setChecked(True)
    widget._brick_items.get("3003").manual_checkbox.setChecked(True)
    
    # Verify states
    assert bricks[0].manually_marked == True, "First brick should be marked"
    assert bricks[1].manually_marked == False, "Second brick should not be marked"
    assert bricks[2].manually_marked == True, "Third brick should be marked"
    print("✓ test_multiple_bricks_manual_marking passed")


if __name__ == "__main__":
    print("Running manual marking tests...\n")
    
    test_checkbox_marks_brick()
    test_checkbox_unmarks_brick()
    test_manual_marking_signal_emission()
    test_set_manual_marking_programmatically()
    test_manual_marking_visual_style()
    test_manual_marking_with_counter()
    test_unmarking_restores_normal_style()
    test_multiple_bricks_manual_marking()
    
    print("\n✅ All manual marking tests passed!")
