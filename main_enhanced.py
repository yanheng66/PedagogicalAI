"""
Main entry point using the enhanced teaching controller with comprehensive tracking.
"""

import json
from models.user_profile import UserProfile
from controllers.enhanced_teaching_controller import EnhancedTeachingController
from utils.io_helpers import get_user_input, print_header


def main():
    """Enhanced SQL Tutor with comprehensive user modeling and analytics."""
    
    topic_to_teach = "INNER JOIN"
    
    # Initialize enhanced components
    user_profile = UserProfile()
    enhanced_controller = EnhancedTeachingController(user_id="enhanced_user_2025")

    print_header("🚀 Enhanced SQL Tutor with Full User Modeling")
    print("This version implements comprehensive data tracking including:")
    print("  📊 Detailed step-by-step analytics")
    print("  🧠 Concept mastery tracking")
    print("  🔍 Error pattern analysis")
    print("  ⚡ Adaptive difficulty adjustment")
    print("  📈 Learning efficiency calculation")
    print("  🎯 Personalized analogies and challenges")
    
    # --- Enhanced Step 1: Personalized Analogy ---
    step_1_context = enhanced_controller.run_step_1_analogy(topic_to_teach, user_profile)
    if not step_1_context:
        print("Could not generate personalized analogy. Exiting.")
        return
    get_user_input("\nPress Enter to continue to Enhanced Step 2...")

    # --- Enhanced Step 2: Metacognitive Prediction ---
    enhanced_controller.run_step_2_prediction(topic_to_teach, step_1_context, user_profile)
    get_user_input("\nPress Enter to continue to Enhanced Step 3...")

    # --- Enhanced Step 3: Multi-Attempt Query Writing ---
    user_profile = enhanced_controller.run_step_3_writing_task(topic_to_teach, step_1_context, user_profile)
    print("\n-- Updated User Profile --")
    print(json.dumps(user_profile.to_dict(), indent=2))
    get_user_input("\nPress Enter to continue to Enhanced Step 4...")
    
    # --- Enhanced Step 4: Adaptive Challenge ---
    user_profile = enhanced_controller.run_step_4_challenge(user_profile)
    print("\n-- Final User Profile --")
    print(json.dumps(user_profile.to_dict(), indent=2))

    # --- Enhanced Session Analytics ---
    enhanced_controller.end_session(user_profile)

    print_header("🎉 Enhanced Learning Session Complete")
    print("Your complete learning journey has been captured!")
    # Verbose summary removed for minimal version


if __name__ == "__main__":
    main() 