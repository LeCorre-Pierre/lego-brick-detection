"""
Quick validation test for brick list interface integration.
Tests basic loading and interaction without GUI display.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.brick import Brick
from src.models.lego_set import LegoSet
from src.utils.progress_tracker import ProgressTracker

def test_basic_functionality():
    """Test basic brick list functionality."""
    print("Testing Brick List Interface Integration...")
    print("-" * 50)
    
    # Test 1: Create bricks with all required properties
    print("\n[TEST 1] Creating bricks with detection properties...")
    brick1 = Brick(part_number="3005", color="red", quantity=5)
    brick2 = Brick(part_number="3004", color="blue", quantity=3)
    brick3 = Brick(part_number="3003", color="yellow", quantity=2)
    
    # Verify detection properties exist
    assert hasattr(brick1, 'manually_marked'), "Brick missing manually_marked property"
    assert hasattr(brick1, 'detected_in_current_frame'), "Brick missing detected_in_current_frame property"
    print("   [OK] Bricks have all required detection properties")
    
    # Test 2: Create LegoSet and verify methods
    print("\n[TEST 2] Creating LegoSet with detection methods...")
    lego_set = LegoSet(
        set_number="60122-1",
        name="Volcano Crawler",
        total_bricks=3,
        bricks=[brick1, brick2, brick3]
    )
    
    assert hasattr(lego_set, 'get_bricks_by_detection_status'), "LegoSet missing detection status method"
    assert hasattr(lego_set, 'update_detection_status'), "LegoSet missing update detection status method"
    print("   [OK] LegoSet has all required detection methods")
    
    # Test 3: Test manual marking
    print("\n[TEST 3] Testing manual marking...")
    brick1.mark_as_manually_found()
    assert brick1.manually_marked == True, "Manual marking failed"
    brick1.unmark_manually_found()
    assert brick1.manually_marked == False, "Manual unmarking failed"
    print("   [OK] Manual marking works correctly")
    
    # Test 4: Test detection marking
    print("\n[TEST 4] Testing detection marking...")
    brick1.set_detected(timestamp=1234567890)
    assert brick1.detected_in_current_frame == True, "Detection marking failed"
    assert brick1.last_detected_timestamp == 1234567890, "Detection timestamp not set"
    brick1.clear_detected()
    assert brick1.detected_in_current_frame == False, "Detection clearing failed"
    print("   [OK] Detection marking works correctly")
    
    # Test 5: Test counter tracking
    print("\n[TEST 5] Testing counter tracking...")
    initial_count = brick1.found_quantity
    brick1.found_quantity = 2
    assert brick1.found_quantity == 2, "Counter update failed"
    assert brick1.get_remaining_quantity() == 3, "Remaining quantity calculation wrong"
    print("   [OK] Counter tracking works correctly")
    
    # Test 6: Test ProgressTracker with manual/detected differentiation
    print("\n[TEST 6] Testing ProgressTracker...")
    tracker = ProgressTracker()
    tracker.start_tracking(lego_set)
    
    # Record finds with different methods
    tracker.record_brick_found("3005", method='manual')
    tracker.record_brick_found("3004", method='detected')
    tracker.record_brick_found("3003", method='manual')
    
    stats = tracker.get_progress_stats()
    assert 'manual_finds' in stats, "ProgressTracker missing manual_finds stat"
    assert 'detected_finds' in stats, "ProgressTracker missing detected_finds stat"
    assert stats['manual_finds'] == 2, f"Expected 2 manual finds, got {stats['manual_finds']}"
    assert stats['detected_finds'] == 1, f"Expected 1 detected find, got {stats['detected_finds']}"
    print(f"   [OK] ProgressTracker: {stats['manual_finds']} manual, {stats['detected_finds']} detected")
    
    # Test 7: Test recent activity tracking
    print("\n[TEST 7] Testing recent activity...")
    activity = tracker.get_recent_activity()
    assert len(activity) == 3, f"Expected 3 activities, got {len(activity)}"
    assert all('method' in a for a in activity), "Activity missing method field"
    print(f"   [OK] Activity tracking: {len(activity)} events recorded")
    
    print("\n" + "=" * 50)
    print("All tests passed! [SUCCESS]")
    print("=" * 50)

if __name__ == "__main__":
    try:
        test_basic_functionality()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n[FAIL] Assertion failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
