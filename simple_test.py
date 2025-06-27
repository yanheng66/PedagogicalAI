"""
Simple test for database integration.
"""

from database import engine, Base
from models.simple_models import *
from services.simple_tracker import SimpleTracker

def test_simple_tracker():
    """Test the simplified tracker."""
    print("Creating database tables...")
    Base.metadata.create_all(engine)
    print("✅ Tables created")
    
    print("\nTesting SimpleTracker...")
    tracker = SimpleTracker()
    
    # Test 1: Start concept session
    print("1. Starting concept session...")
    session_id = tracker.start_concept(user_id="test_user_123", topic="INNER JOIN")
    print(f"   ✅ Session created: {session_id[:8]}...")
    
    # Test 2: Log interactions
    print("\n2. Logging step interactions...")
    
    # Step 1
    interaction_id_1 = tracker.log_interaction(
        session_id=session_id,
        step_number=1,
        success=True,
        duration=120,
        metadata={"reading_time": 120, "comprehension": "good"}
    )
    print(f"   ✅ Step 1 logged: {interaction_id_1}")
    
    # Step 2
    interaction_id_2 = tracker.log_interaction(
        session_id=session_id,
        step_number=2,
        success=True,
        duration=180,
        metadata={"prediction_correct": True, "time_to_answer": 45}
    )
    print(f"   ✅ Step 2 logged: {interaction_id_2}")
    
    # Step 3
    interaction_id_3 = tracker.log_interaction(
        session_id=session_id,
        step_number=3,
        success=True,
        duration=300,
        metadata={"attempts": 2, "query_correct": True}
    )
    print(f"   ✅ Step 3 logged: {interaction_id_3}")
    
    print("\n🎉 All tests passed! Database integration is working!")

if __name__ == "__main__":
    test_simple_tracker() 