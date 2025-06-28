"""
New 5-step teaching system runner using TeachingControllerV2
SQL AI Teaching System - 5-Step Dynamic Learning Flow
"""

from models import UserProfile, UserModel
from controllers.teaching_controller_v2 import TeachingControllerV2
from utils.io_helpers import get_user_input, print_header
import json


def main():
    print_header("SQL AI Teaching System - 5-Step Learning Flow")
    
    print("""
🎯 Welcome to the New SQL AI Teaching System!

Key Features:
✨ Concept Understanding Confirmation Loop
✨ MCQ Retry Mechanism
✨ Dual Scoring System (Query + Explanation)
✨ Adaptive Difficulty and Hint System
✨ AI-Generated Personalized Reflection Poem
✨ Intelligent User Modeling Analysis

Let's start your SQL learning journey!
    """)
    
    # Initialize user and controller
    user_name = get_user_input("Enter your name (press Enter for default 'Student'): ").strip()
    user_name = user_name if user_name else "Student"
    
    print("\nSelect your current level:")
    print("  1. Beginner")
    print("  2. Intermediate") 
    print("  3. Advanced")
    
    level_choice = get_user_input("Choose (1-3, default 1): ").strip()
    level_map = {"1": "Beginner", "2": "Intermediate", "3": "Advanced"}
    user_level = level_map.get(level_choice, "Beginner")
    
    user_profile = UserProfile(user_name, user_level)
    controller = TeachingControllerV2()
    
    print(f"\n👋 Hello {user_name}! Current level: {user_level}")
    
    # Choose learning concept
    print("\n📚 Available SQL concepts:")
    concepts = [
        "INNER JOIN", "LEFT JOIN", "RIGHT JOIN", 
        "GROUP BY", "WHERE", "ORDER BY",
        "HAVING", "SUBQUERIES", "COUNT/SUM/AVG"
    ]
    
    for i, concept in enumerate(concepts, 1):
        print(f"  {i}. {concept}")
    
    choice = get_user_input(f"\nSelect concept to learn (1-{len(concepts)}): ").strip()
    try:
        topic = concepts[int(choice) - 1]
    except (ValueError, IndexError):
        topic = "INNER JOIN"  # Default concept
        print(f"Using default concept: {topic}")
    
    print(f"\n🎯 Starting to learn: {topic}")
    print("=" * 60)
    print("💡 Tip: You can type 'quit' or 'exit' at any step to exit")
    print("=" * 60)
    
    try:
        # Step 1: Concept Introduction
        print_header("Step 1: Concept Introduction & Understanding Confirmation")
        step1_result = controller.run_step_1_concept_introduction(topic, user_profile)
        
        if step1_result:
            get_user_input("\n✅ Step 1 completed! Press Enter to continue to Step 2...")
        else:
            print("❌ Step 1 failed to complete, exiting program")
            return
        
        # Step 2: Example Prediction
        print_header("Step 2: Example Prediction Exercise")
        step2_result = controller.run_step_2_example_prediction(topic, user_profile)
        
        if step2_result:
            get_user_input("\n✅ Step 2 completed! Press Enter to continue to Step 3...")
        else:
            print("⚠️  Step 2 not fully completed, but continuing...")
        
        # Step 3: Conceptual Assessment
        print_header("Step 3: Conceptual Assessment - Query Writing & Explanation")
        step3_result = controller.run_step_3_conceptual_assessment(topic, user_profile)
        
        if step3_result:
            get_user_input("\n✅ Step 3 completed! Press Enter to continue to Step 4...")
        else:
            print("⚠️  Step 3 not fully completed, but continuing...")
        
        # Step 4: Guided Practice
        print_header("Step 4: Guided Practice - Adaptive Challenge")
        step4_result = controller.run_step_4_guided_practice(topic, user_profile)
        
        if step4_result:
            get_user_input("\n✅ Step 4 completed! Press Enter to continue to final step...")
        else:
            print("⚠️  Step 4 not fully completed, but continuing...")
        
        # Step 5: Reflection Poem
        print_header("Step 5: AI Reflection Poem - Creative Learning Summary")
        step5_result = controller.run_step_5_reflection_poem(topic, user_profile)
        
        # Generate chapter data and final analysis
        print_header("🎊 Learning Complete - Intelligent Analysis Report")
        
        try:
            chapter_data = controller.get_chapter_data(user_profile.user_id, topic)
            
            # Update user model
            user_model = user_profile.get_user_model()
            user_model.add_chapter_data(chapter_data)
            user_profile.update_user_model(user_model)
            
            # Display learning results
            print("\n📊 Learning Results:")
            print(f"📈 Chapter Mastery: {chapter_data.masteryLevel:.1%}")
            print(f"🎯 Overall Mastery: {user_model.get_overall_mastery_level():.1%}")
            
            strengths = user_model.get_strength_areas()
            focus_areas = user_model.get_focus_areas()
            
            print(f"💪 Your Strengths: {', '.join(strengths) if strengths else 'Keep learning to discover strengths'}")
            print(f"📈 Areas for Improvement: {', '.join(focus_areas) if focus_areas else 'Maintain current pace'}")
            
            # Learning suggestions
            print("\n🎯 Personalized Learning Suggestions:")
            if chapter_data.masteryLevel >= 0.8:
                print("🌟 Excellent! You've mastered this concept well. Try advanced concepts or real-world applications.")
            elif chapter_data.masteryLevel >= 0.6:
                print("👍 Good job! You have a solid foundation. Practice more to reinforce your understanding.")
            else:
                print("📚 Keep going! Review the concept basics and practice similar problems.")
                
        except Exception as e:
            print(f"⚠️  Error generating analysis report: {e}")
            print("But this doesn't affect your learning progress!")
        
        # Ask whether to view detailed profile
        show_detail = get_user_input("\n📋 View complete user learning profile? (y/n, default n): ").strip().lower()
        if show_detail in ['y', 'yes', 'Y', 'YES']:
            print("\n📋 Complete User Learning Profile:")
            print("=" * 60)
            try:
                profile_dict = user_profile.to_dict()
                print(json.dumps(profile_dict, indent=2, ensure_ascii=False))
            except Exception as e:
                print(f"Error displaying profile: {e}")
        
        print("\n🎉 Congratulations on completing the entire learning flow!")
        print("💡 Suggestion: Review regularly, try different SQL concepts, and keep improving!")
        
    except KeyboardInterrupt:
        print("\n\n👋 Program interrupted by user, goodbye!")
    except Exception as e:
        print(f"\n❌ Program error: {e}")
        print("💡 Please check system configuration or contact technical support")


if __name__ == "__main__":
    main() 