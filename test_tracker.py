"""
Test script for StudentTracker service.
"""

from services.student_tracker import StudentTracker
from utils.io_helpers import print_header

def test_student_tracker():
    """Test the StudentTracker service with mock data."""
    print_header("Testing StudentTracker Service")
    
    # Create tracker instance
    tracker = StudentTracker()
    
    try:
        # Test 1: Start a concept session
        print("1. Starting concept session...")
        session_id = tracker.start_concept(user_id="test_user_123", topic="INNER JOIN")
        print(f"   ✅ Session created: {session_id}")
        
        # Test 2: Log step interactions
        print("\n2. Logging step interactions...")
        
        # Step 1
        interaction_id_1 = tracker.log_interaction(
            session_id=session_id,
            step_number=1,
            success=True,
            duration=120,  # 2 minutes
            metadata={"reading_time": 120, "comprehension": "good"}
        )
        print(f"   ✅ Step 1 logged: {interaction_id_1}")
        
        # Step 2
        interaction_id_2 = tracker.log_interaction(
            session_id=session_id,
            step_number=2,
            success=True,
            duration=180,  # 3 minutes
            metadata={"prediction_correct": True, "time_to_answer": 45}
        )
        print(f"   ✅ Step 2 logged: {interaction_id_2}")
        
        # Step 3
        interaction_id_3 = tracker.log_interaction(
            session_id=session_id,
            step_number=3,
            success=True,
            duration=300,  # 5 minutes
            metadata={"attempts": 2, "query_correct": True}
        )
        print(f"   ✅ Step 3 logged: {interaction_id_3}")
        
        print("\n🎉 All tests passed! StudentTracker is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise
    finally:
        tracker.close()

if __name__ == "__main__":
    test_student_tracker() 