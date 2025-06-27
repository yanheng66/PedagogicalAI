"""
Main entry point for the SQL Tutor application with database integration.
"""

import json
from models.user_profile import UserProfile
from controllers.db_teaching_controller import DBTeachingController
from utils.io_helpers import get_user_input, print_header


def main():
    """The main execution loop for the pedagogical agent with database tracking."""
    
    # For this test, we are hardcoding the topic to 'INNER JOIN' as requested.
    topic_to_teach = "INNER JOIN"
    
    # Initialize components with database tracking
    user_profile = UserProfile()
    teaching_controller = DBTeachingController(user_id="demo_user_2025")

    print_header("🚀 SQL Tutor with Database Integration")
    print("This version will track all your learning interactions in the database!")
    
    # --- Step 1: Analogy ---
    step_1_context = teaching_controller.run_step_1_analogy(topic_to_teach, user_profile)
    if not step_1_context:
        print("Could not get explanation for Step 1. Exiting.")
        return
    get_user_input("\nPress Enter to continue to Step 2...")

    # --- Step 2: Prediction ---
    teaching_controller.run_step_2_prediction(topic_to_teach, step_1_context, user_profile)
    get_user_input("\nPress Enter to continue to Step 3...")

    # --- Step 3: Writing Task & Grading ---
    user_profile = teaching_controller.run_step_3_writing_task(topic_to_teach, step_1_context, user_profile)
    print("\n-- Current User Profile --")
    print(json.dumps(user_profile.to_dict(), indent=2))
    get_user_input("\nPress Enter to continue to the final challenge...")
    
    # --- Step 4: Challenge ---
    user_profile = teaching_controller.run_step_4_challenge(user_profile)
    print("\n-- Final User Profile --")
    print(json.dumps(user_profile.to_dict(), indent=2))

    # --- End Session ---
    teaching_controller.end_session(user_profile)

    print_header("🎉 Agent Test Run Complete")
    print("You have completed all steps of the agent's teaching flow.")
    print("All your learning data has been saved to the database!")


if __name__ == "__main__":
    main() 