"""
Unit tests for detection feedback functionality.
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


def test_detection_icon_shows_when_detected():
    """Test that detection icon appears when brick is detected."""
    brick = Brick(
        part_number="3005",
        color="Red",
        quantity=5,
        found_quantity=0
    )
    lego_set = LegoSet(name="Test Set", set_number="12345", total_bricks=1, bricks=[brick])
    
    widget = BrickListWidget()
    widget.load_set(lego_set)
    widget.show()  # Show widget to enable visibility checks
    
    # Get the brick list item
    brick_item = widget._brick_items.get("3005")
    assert brick_item is not None, "Brick item not found"
    
    # Initially icon should be hidden
    assert brick_item._is_detected == False, "Initially should not be detected"
    
    # Set as detected
    brick_item.set_detection_status(True)
    
    # Check internal state and visibility
    assert brick_item._is_detected == True, "Should be marked as detected"
    assert brick_item.detection_icon.isVisible() == True, "Icon should be visible when detected"
    print("[OK] test_detection_icon_shows_when_detected passed")


def test_detection_icon_hides_when_not_detected():
    """Test that detection icon hides when brick is no longer detected."""
    brick = Brick(
        part_number="3005",
        color="Red",
        quantity=5,
        found_quantity=0
    )
    lego_set = LegoSet(name="Test Set", set_number="12345", total_bricks=1, bricks=[brick])
    
    widget = BrickListWidget()
    widget.load_set(lego_set)
    widget.show()
    
    brick_item = widget._brick_items.get("3005")
    
    # Set as detected then undetected
    brick_item.set_detection_status(True)
    assert brick_item._is_detected == True, "Should be detected"
    assert brick_item.detection_icon.isVisible() == True, "Icon should be visible"
    
    brick_item.set_detection_status(False)
    assert brick_item._is_detected == False, "Should not be detected"
    assert brick_item.detection_icon.isVisible() == False, "Icon should be hidden"
    print("[OK] test_detection_icon_hides_when_not_detected passed")


def test_update_detection_status():
    """Test updating detection status via widget method."""
    bricks = [
        Brick(part_number="3005", color="Red", quantity=5, found_quantity=0),
        Brick(part_number="3004", color="Blue", quantity=3, found_quantity=0),
    ]
    lego_set = LegoSet(name="Test Set", set_number="12345", total_bricks=2, bricks=bricks)
    
    widget = BrickListWidget()
    widget.load_set(lego_set)
    widget.show()
    
    # Update detection status
    widget.update_detection_status({"3005"})
    
    # Manually trigger the batched update
    widget._apply_detection_updates()
    
    # Get fresh references after reordering (items are recreated)
    brick_item_3005 = widget._brick_items.get("3005")
    brick_item_3004 = widget._brick_items.get("3004")
    
    assert brick_item_3005._is_detected == True, "3005 should be detected"
    assert brick_item_3004._is_detected == False, "3004 should not be detected"
    print("[OK] test_update_detection_status passed")


def test_list_reordering_detected_to_top():
    """Test that detected bricks move to top of list."""
    bricks = [
        Brick(part_number="3005", color="Red", quantity=5, found_quantity=0),
        Brick(part_number="3004", color="Blue", quantity=3, found_quantity=0),
        Brick(part_number="3003", color="Green", quantity=2, found_quantity=0),
    ]
    lego_set = LegoSet(name="Test Set", set_number="12345", total_bricks=3, bricks=bricks)
    
    widget = BrickListWidget()
    widget.load_set(lego_set)
    widget.show()
    
    # Detect middle brick (3004)
    widget.update_detection_status({"3004"})
    widget._apply_detection_updates()
    
    # Check order: first item should now be 3004
    first_item = widget.item(0)
    first_widget = widget.itemWidget(first_item)
    assert first_widget.get_brick_id() == "3004", f"Expected 3004 at top, got {first_widget.get_brick_id()}"
    print("[OK] test_list_reordering_detected_to_top passed")


def test_multiple_detections_reordering():
    """Test reordering with multiple detected bricks."""
    bricks = [
        Brick(part_number="3005", color="Red", quantity=5, found_quantity=0),
        Brick(part_number="3004", color="Blue", quantity=3, found_quantity=0),
        Brick(part_number="3003", color="Green", quantity=2, found_quantity=0),
        Brick(part_number="3002", color="Yellow", quantity=1, found_quantity=0),
    ]
    lego_set = LegoSet(name="Test Set", set_number="12345", total_bricks=4, bricks=bricks)
    
    widget = BrickListWidget()
    widget.load_set(lego_set)
    widget.show()
    
    # Detect first and third bricks
    widget.update_detection_status({"3005", "3003"})
    widget._apply_detection_updates()
    
    # Get first two items
    first_item = widget.item(0)
    second_item = widget.item(1)
    first_widget = widget.itemWidget(first_item)
    second_widget = widget.itemWidget(second_item)
    
    # First two should be detected bricks (in original order: 3005, 3003)
    detected_at_top = {first_widget.get_brick_id(), second_widget.get_brick_id()}
    assert detected_at_top == {"3005", "3003"}, f"Expected 3005 and 3003 at top, got {detected_at_top}"
    print("[OK] test_multiple_detections_reordering passed")


def test_detection_cleared_restores_order():
    """Test that clearing detections restores original order."""
    bricks = [
        Brick(part_number="3005", color="Red", quantity=5, found_quantity=0),
        Brick(part_number="3004", color="Blue", quantity=3, found_quantity=0),
        Brick(part_number="3003", color="Green", quantity=2, found_quantity=0),
    ]
    lego_set = LegoSet(name="Test Set", set_number="12345", total_bricks=3, bricks=bricks)
    
    widget = BrickListWidget()
    widget.load_set(lego_set)
    widget.show()
    
    # Detect then clear
    widget.update_detection_status({"3004"})
    widget._apply_detection_updates()
    
    widget.update_detection_status(set())  # Clear detections
    widget._apply_detection_updates()
    
    # Check order restored: 3005, 3004, 3003
    first_item = widget.item(0)
    first_widget = widget.itemWidget(first_item)
    assert first_widget.get_brick_id() == "3005", f"Expected 3005 first, got {first_widget.get_brick_id()}"
    print("[OK] test_detection_cleared_restores_order passed")


def test_batched_updates_prevent_flicker():
    """Test that detection updates are batched via timer."""
    brick = Brick(
        part_number="3005",
        color="Red",
        quantity=5,
        found_quantity=0
    )
    lego_set = LegoSet(name="Test Set", set_number="12345", total_bricks=1, bricks=[brick])
    
    widget = BrickListWidget()
    widget.load_set(lego_set)
    widget.show()
    
    # Update detection status (should be pending)
    widget.update_detection_status({"3005"})
    
    # Check that it's in pending state
    assert "3005" in widget._state.pending_detections, "Should be in pending detections"
    
    # Note: In real usage, timer would trigger _apply_detection_updates()
    # For testing, we manually call it
    widget._apply_detection_updates()
    
    # Get fresh reference after reordering
    brick_item = widget._brick_items.get("3005")
    assert brick_item._is_detected == True, "Should be detected after update applied"
    print("[OK] test_batched_updates_prevent_flicker passed")


def test_detection_state_persistence():
    """Test that detection state persists correctly."""
    brick = Brick(
        part_number="3005",
        color="Red",
        quantity=5,
        found_quantity=0
    )
    lego_set = LegoSet(name="Test Set", set_number="12345", total_bricks=1, bricks=[brick])
    
    widget = BrickListWidget()
    widget.load_set(lego_set)
    widget.show()
    
    # Set detection and apply
    widget.update_detection_status({"3005"})
    widget._apply_detection_updates()
    
    # Verify state is stored
    assert "3005" in widget._state.detected_bricks, "Detection state should be stored"
    
    # Update with same detection (should not cause changes)
    widget.update_detection_status({"3005"})
    widget._apply_detection_updates()
    
    # State should remain
    assert "3005" in widget._state.detected_bricks, "Detection state should persist"
    print("[OK] test_detection_state_persistence passed")


def test_detection_with_manual_marking():
    """Test that detection works alongside manual marking."""
    brick = Brick(
        part_number="3005",
        color="Red",
        quantity=5,
        found_quantity=0
    )
    lego_set = LegoSet(name="Test Set", set_number="12345", total_bricks=1, bricks=[brick])
    
    widget = BrickListWidget()
    widget.load_set(lego_set)
    widget.show()
    
    brick_item = widget._brick_items.get("3005")
    
    # Mark manually
    brick_item.manual_checkbox.setChecked(True)
    assert brick.manually_marked == True, "Should be manually marked"
    
    # Also detect
    widget.update_detection_status({"3005"})
    widget._apply_detection_updates()
    
    # Get fresh reference after reordering
    brick_item = widget._brick_items.get("3005")
    
    # Both states should coexist
    assert brick.manually_marked == True, "Should still be manually marked"
    assert brick_item._is_detected == True, "Should be detected"
    print("[OK] test_detection_with_manual_marking passed")


def test_empty_detection_set():
    """Test handling of empty detection set."""
    brick = Brick(
        part_number="3005",
        color="Red",
        quantity=5,
        found_quantity=0
    )
    lego_set = LegoSet(name="Test Set", set_number="12345", total_bricks=1, bricks=[brick])
    
    widget = BrickListWidget()
    widget.load_set(lego_set)
    widget.show()
    
    # Update with empty set (should not crash)
    widget.update_detection_status(set())
    widget._apply_detection_updates()
    
    brick_item = widget._brick_items.get("3005")
    assert brick_item._is_detected == False, "No brick should be detected"
    print("[OK] test_empty_detection_set passed")


if __name__ == "__main__":
    print("Running detection feedback tests...\n")
    
    test_detection_icon_shows_when_detected()
    test_detection_icon_hides_when_not_detected()
    test_update_detection_status()
    test_list_reordering_detected_to_top()
    test_multiple_detections_reordering()
    test_detection_cleared_restores_order()
    test_batched_updates_prevent_flicker()
    test_detection_state_persistence()
    test_detection_with_manual_marking()
    test_empty_detection_set()
    
    print("\n[SUCCESS] All detection feedback tests passed!")
