"""
Grading service for evaluating student submissions.
"""

import json
from typing import Dict, Any
from .ai_service import AIService
from models.user_profile import UserProfile
from utils.io_helpers import print_header


class GradingService:
    """Service for grading student SQL submissions."""
    
    @staticmethod
    def grade_submission(query: str, explanation: str, topic: str, user_profile: UserProfile) -> UserProfile:
        """
        Evaluates a user's SQL query and explanation using the AI grading agent.
        Returns the updated user profile.
        """
        print_header("Submission Evaluation")
        
        system_prompt = """
You are an AI pedagogical agent evaluating student SQL submissions. Your role is to assess understanding and generate standardized learning profile data for adaptive teaching. ## Your Role: - Evaluate SQL query correctness and conceptual understanding - **Generate standardized error classifications** - **Identify specific misconceptions for learning profile** - **Provide actionable data for future personalization** ## Response Format: Generate ALL responses in JSON format with standardized fields for learning analytics. ## Evaluation Framework: ### 1. **Error Classification (Standardized)**: - **SYNTAX_ERROR**: Incorrect SQL syntax - **LOGIC_ERROR**: Syntactically correct but wrong logic - **INCOMPLETE_SOLUTION**: Partially correct - **EFFICIENCY_ISSUE**: Works but suboptimal - **CONCEPTUAL_MISUNDERSTANDING**: Fundamental concept confusion - **CORRECT**: No errors ### 2. **Concept Mastery Levels**: - **NOT_ATTEMPTED**: 0% - **STRUGGLING**: 1-40% - **DEVELOPING**: 41-70% - **PROFICIENT**: 71-90% - **MASTERED**: 91-100% ### 3. **Learning Profile Fields to Track**: - **concepts_used**: Which SQL concepts were attempted - **concepts_mastered**: Which were used correctly - **misconceptions**: Specific misunderstandings identified - **error_patterns**: Recurring mistake types - **strengths**: What student does well - **next_focus_areas**: What to practice next
"""
        
        user_prompt = f"""
Please evaluate the following student submission for the concept(s) '{topic}'.

Student Query:
```sql
{query}
```

Student Explanation:
> {explanation}

Generate a full JSON evaluation based on your system prompt's framework. It is critical that you include the 'feedback_for_student' object with a 'message' inside.
"""
        
        grading_str = AIService.get_response(system_prompt, user_prompt, json_mode=True)
        
        print("\n-- [DEBUG] Raw Grading Response from AI --\n", grading_str)

        if grading_str:
            grading_data = AIService.parse_json_response(grading_str)
            if grading_data:
                feedback_section = grading_data.get("feedback_for_student", {})
                feedback_message = feedback_section.get("message", 
                    "The AI did not provide a specific feedback message, but the analysis is complete.")
                print("\n-- Evaluation Feedback --")
                print(feedback_message)
                user_profile.update_from_grading_data(grading_data)
                print("\n📈 User profile updated based on performance.")
        
        return user_profile 