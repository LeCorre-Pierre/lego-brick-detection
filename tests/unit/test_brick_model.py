"""
Unit tests for Brick model extensions.
"""

import pytest
from src.models.brick import Brick


class TestBrickModelExtensions:
    """Test new properties and methods added for brick list interface."""
    
    def test_brick_initialization_with_new_properties(self):
        """Test that new properties initialize correctly."""
        brick = Brick(part_number="3005", color="Red", quantity=5)
        
        assert brick.manually_marked is False
        assert brick.detected_in_current_frame is False
        assert brick.last_detected_timestamp == 0.0
        assert brick.original_list_position == 0
    
    def test_mark_as_manually_found(self):
        """Test marking brick as manually found."""
        brick = Brick(part_number="3005", color="Red", quantity=5)
        
        brick.mark_as_manually_found()
        
        assert brick.manually_marked is True
    
    def test_unmark_manually_found(self):
        """Test unmarking brick as manually found."""
        brick = Brick(part_number="3005", color="Red", quantity=5)
        brick.mark_as_manually_found()
        
        brick.unmark_manually_found()
        
        assert brick.manually_marked is False
    
    def test_set_detected(self):
        """Test setting detection status."""
        brick = Brick(part_number="3005", color="Red", quantity=5)
        timestamp = 1234567890.5
        
        brick.set_detected(timestamp)
        
        assert brick.detected_in_current_frame is True
        assert brick.last_detected_timestamp == timestamp
    
    def test_clear_detected(self):
        """Test clearing detection status."""
        brick = Brick(part_number="3005", color="Red", quantity=5)
        brick.set_detected(1234567890.5)
        
        brick.clear_detected()
        
        assert brick.detected_in_current_frame is False
        # Note: timestamp is not cleared, only the flag
    
    def test_should_be_detected_when_not_marked_and_not_complete(self):
        """Test should_be_detected returns True when brick not marked and not complete."""
        brick = Brick(part_number="3005", color="Red", quantity=5, found_quantity=2)
        
        assert brick.should_be_detected() is True
    
    def test_should_be_detected_when_manually_marked(self):
        """Test should_be_detected returns False when manually marked."""
        brick = Brick(part_number="3005", color="Red", quantity=5, found_quantity=2)
        brick.mark_as_manually_found()
        
        assert brick.should_be_detected() is False
    
    def test_should_be_detected_when_fully_found(self):
        """Test should_be_detected returns False when fully found."""
        brick = Brick(part_number="3005", color="Red", quantity=5, found_quantity=5)
        
        assert brick.should_be_detected() is False
        assert brick.is_fully_found() is True
    
    def test_should_be_detected_when_marked_and_complete(self):
        """Test should_be_detected returns False when both marked and complete."""
        brick = Brick(part_number="3005", color="Red", quantity=5, found_quantity=5)
        brick.mark_as_manually_found()
        
        assert brick.should_be_detected() is False
    
    def test_detection_workflow(self):
        """Test complete detection workflow."""
        brick = Brick(part_number="3005", color="Red", quantity=5)
        
        # Initially should be detectable
        assert brick.should_be_detected() is True
        
        # Detect brick
        brick.set_detected(100.0)
        assert brick.detected_in_current_frame is True
        assert brick.should_be_detected() is True  # Still detectable while not marked
        
        # Clear detection
        brick.clear_detected()
        assert brick.detected_in_current_frame is False
        
        # Mark as manually found
        brick.mark_as_manually_found()
        assert brick.should_be_detected() is False  # No longer detectable
    
    def test_original_list_position_tracking(self):
        """Test original list position can be tracked."""
        brick = Brick(part_number="3005", color="Red", quantity=5)
        
        brick.original_list_position = 10
        
        assert brick.original_list_position == 10
