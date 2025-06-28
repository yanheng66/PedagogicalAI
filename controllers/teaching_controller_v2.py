"""
Teaching controller for managing the 5-step dynamic teaching flow.
Version 2.0 - Implements the new 5-step pedagogical framework.
"""

import json
import time
from typing import Optional, Dict, Any, List
from services.ai_service import AIService
from services.grading_service import GradingService
from models.user_profile import UserProfile
from models.teaching_flow_data import (
    Step1Data, Step2Data, Step3Data, Step4Data, Step5Data,
    ChapterData, EventLogEntry, TeachingFlowData
)
from utils.io_helpers import get_user_input, print_header


class TeachingControllerV2:
    """Controller for managing the 5-step dynamic teaching flow."""
    
    def __init__(self):
        self.ai_service = AIService()
        self.grading_service = GradingService()
        self.teaching_flow_data = TeachingFlowData()  # Use structured data model
    
    def run_step_1_concept_introduction(self, topic: str, user_profile: UserProfile) -> Step1Data:
        """
        Step 1: Concept Introduction with understanding check and re-explanation.
        Activates learners' prior knowledge and explains SQL concepts through intuitive analogies.
        """
        print_header(f"Step 1: Concept Introduction for '{topic}'")
        start_time = time.time()
        
        # Initialize step data using the data model
        step1_data = Step1Data()
        
        system_prompt = """
You are an AI pedagogical agent introducing SQL concepts through intuitive analogies and real-life examples.

## Your Role:
- Use familiar everyday scenarios to explain SQL concepts
- Include visual metaphors and simple diagrams (described in text)
- Keep explanations concise but clear
- Adapt complexity to student level

## Response Structure:
1. **Analogy Introduction**: Start with a relatable real-life scenario (2-3 sentences)
2. **Concept Connection**: Link the scenario to the SQL concept (2-3 sentences)
3. **Simple Example**: Show a brief SQL code snippet with explanation
4. **Visual Metaphor**: Describe a simple diagram or visualization

Keep the total response under 200 words for clarity.
"""
        
        # Initial explanation
        user_prompt = f"Introduce the SQL concept '{topic}' to a {user_profile.level} student using an intuitive analogy."
        
        understanding_achieved = False
        max_attempts = 3
        
        while not understanding_achieved and step1_data.reExplanationCount < max_attempts:
            # Get AI explanation
            response = self.ai_service.get_response(system_prompt, user_prompt)
            if response:
                step1_data.aiExplanation = response
                print("\n-- AI's Explanation --\n")
                print(response)
                
                # Check understanding
                print("\n🤔 Do you understand this explanation?")
                user_response = get_user_input("Enter 'yes' or 'no': ").lower().strip()
                
                if user_response == 'yes':
                    step1_data.userUnderstanding = True
                    understanding_achieved = True
                    print("\n✅ Great! Let's move on to the next step.")
                else:
                    step1_data.reExplanationCount += 1
                    if step1_data.reExplanationCount < max_attempts:
                        print("\n📚 Let me explain it differently...")
                        # Modify prompt for alternative explanation
                        user_prompt = f"The student didn't understand the previous explanation of '{topic}'. Provide an alternative explanation using a different analogy or visual approach. Student level: {user_profile.level}."
                    else:
                        print("\n📖 Let's proceed with additional practice to clarify the concept.")
                        understanding_achieved = True  # Force progression
            else:
                print("Failed to generate explanation. Please try again.")
                break
        
        # Calculate response time
        step1_data.responseTimeMs = int((time.time() - start_time) * 1000)
        self.teaching_flow_data.step1 = step1_data
        
        return step1_data
    
    def run_step_2_example_prediction(self, topic: str, user_profile: UserProfile) -> Step2Data:
        """
        Step 2: Concrete Example + Prediction (MCQ).
        Deepens prediction ability for query results through real examples and multiple-choice questions.
        """
        print_header(f"Step 2: Example & Prediction for '{topic}'")
        start_time = time.time()
        
        # Initialize step data using the data model
        step2_data = Step2Data()
        
        system_prompt = """
You are an AI pedagogical agent creating SQL prediction exercises. Generate MCQ questions that test conceptual understanding.

## Your Role:
- Present SQL queries with sample data
- Create meaningful multiple-choice questions
- Include common misconceptions as distractors
- Provide clear feedback for wrong answers

## Response Format:
Generate response in JSON format with this structure:
```json
{
  "scenario": "Brief context continuation from Step 1",
  "sample_data": {
    "tables": [
      {
        "name": "TableName",
        "data": [{"col1": "val1", "col2": "val2"}]
      }
    ]
  },
  "sql_query": "SELECT statement to analyze",
  "question": "What will be the output of this query?",
  "options": [
    {"id": "A", "content": "Option A description"},
    {"id": "B", "content": "Option B description"},
    {"id": "C", "content": "Option C description"},
    {"id": "D", "content": "Option D description"}
  ],
  "correct_answer": "B",
  "feedback": {
    "A": "Why option A is incorrect",
    "B": "Why option B is correct",
    "C": "Why option C is incorrect",
    "D": "Why option D is incorrect"
  },
  "explanation": "Detailed explanation for students who fail twice"
}
```
"""
        
        user_prompt = f"Create a prediction MCQ for SQL concept '{topic}'. Level: {user_profile.level}."
        
        # Generate MCQ
        response_str = self.ai_service.get_response(system_prompt, user_prompt, json_mode=True)
        if not response_str:
            return step2_data
            
        data = self.ai_service.parse_json_response(response_str)
        if not data:
            return step2_data
        
        # Store query and options
        step2_data.sqlQuery = data.get("sql_query", "")
        step2_data.options = [opt["content"] for opt in data.get("options", [])]
        
        # Display scenario and data
        print(f"\n-- Scenario: {data.get('scenario', '')} --\n")
        for table in data.get('sample_data', {}).get('tables', []):
            print(f"Table: {table['name']}")
            print(json.dumps(table['data'], indent=2))
        
        print(f"\nSQL Query:\n{data['sql_query']}\n")
        print(f"📊 {data['question']}")
        
        # MCQ interaction with retry logic
        max_attempts = 2
        attempt = 0
        correct_answer = data.get('correct_answer', '')
        
        while attempt < max_attempts and not step2_data.predictionAccuracy:
            attempt += 1
            step2_data.mcqAttempts = attempt
            
            # Display options
            for option in data.get('options', []):
                print(f"  {option['id']}. {option['content']}")
            
            # Get user answer
            user_answer = get_user_input("\nYour prediction (A/B/C/D): ").upper()
            step2_data.userSelection = user_answer
            
            if user_answer == correct_answer:
                step2_data.predictionAccuracy = True
                print(f"\n✅ Correct! {data['feedback'][correct_answer]}")
            else:
                print(f"\n❌ Not quite. {data['feedback'].get(user_answer, 'Invalid option.')}")
                
                if attempt < max_attempts:
                    print("\n🔄 Let's try a similar question...")
                    # In a real implementation, generate a new similar question
                    # For now, we'll use the same question
                else:
                    # Provide detailed explanation after second failure
                    explanation = data.get('explanation', 'INNER JOIN only returns rows where the join condition is met in both tables.')
                    step2_data.explanationProvided = explanation
                    print(f"\n📖 Detailed Explanation:\n{explanation}")
        
        # Calculate response time
        step2_data.mcqResponseTimeMs = int((time.time() - start_time) * 1000)
        self.teaching_flow_data.step2 = step2_data
        
        return step2_data
    
    def run_step_3_conceptual_assessment(self, topic: str, user_profile: UserProfile) -> Step3Data:
        """
        Step 3: Conceptual Assessment.
        Evaluates whether learners have truly internalized and can clearly express learned concepts.
        """
        print_header(f"Step 3: Conceptual Assessment for '{topic}'")
        start_time = time.time()
        
        # Initialize step data using the data model
        step3_data = Step3Data()
        
        system_prompt_task = """
You are an AI pedagogical agent creating conceptual assessment tasks. Design a simple task that tests understanding of the SQL concept.

## Response Format:
Generate response in JSON format:
```json
{
  "task_description": "Clear description of what the student should write",
  "table_schema": [
    {
      "table_name": "TableName",
      "columns": [
        {"name": "column_name", "type": "DATA_TYPE", "description": "Column purpose"}
      ]
    }
  ],
  "requirements": [
    "Requirement 1",
    "Requirement 2"
  ],
  "example_hint": "A hint to help students start"
}
```
"""
        
        user_prompt_task = f"Create a simple SQL writing task for concept '{topic}'. Level: {user_profile.level}."
        
        # Generate assessment task
        task_str = self.ai_service.get_response(system_prompt_task, user_prompt_task, json_mode=True)
        if not task_str:
            return step3_data
            
        task_data = self.ai_service.parse_json_response(task_str)
        if not task_data:
            return step3_data
        
        # Display task
        print(f"\n-- Your Task --")
        print(f"{task_data.get('task_description', '')}\n")
        
        # Display schema
        for table in task_data.get('table_schema', []):
            print(f"Table: {table['table_name']}")
            for col in table.get('columns', []):
                print(f"  - {col['name']} ({col['type']}): {col['description']}")
        
        print("\nRequirements:")
        for req in task_data.get('requirements', []):
            print(f"  • {req}")
        
        print(f"\n💡 Hint: {task_data.get('example_hint', '')}")
        
        # Collect submissions with retry logic
        submission_accepted = False
        max_submissions = 3
        
        while not submission_accepted and step3_data.submissionCount < max_submissions:
            step3_data.submissionCount += 1
            
            # Collect SQL query
            print(f"\n📝 Write your SQL query (Attempt {step3_data.submissionCount}/{max_submissions}):")
            print("Type 'DONE' on a new line when finished.")
            query_lines = []
            while True:
                line = get_user_input("> ")
                if line.upper() == 'DONE':
                    break
                query_lines.append(line)
            step3_data.userQuery = "\n".join(query_lines)
            
            # Collect explanation
            print("\nNow explain what your query does in plain English.")
            print("Type 'DONE' on a new line when finished.")
            explanation_lines = []
            while True:
                line = get_user_input("> ")
                if line.upper() == 'DONE':
                    break
                explanation_lines.append(line)
            step3_data.userExplanation = "\n".join(explanation_lines)
            
            # Assess submission
            assessment_prompt = f"""
Assess the following SQL query and explanation for the concept '{topic}'.

Query:
{step3_data.userQuery}

Explanation:
{step3_data.userExplanation}

Provide assessment in JSON format:
{{
  "sql_correctness": 0.0-1.0,
  "explanation_depth": 0.0-1.0,
  "misunderstandings": ["list of conceptual errors"],
  "feedback": "constructive feedback",
  "acceptable": true/false
}}
"""
            
            assessment_str = self.ai_service.get_response(
                "You are an SQL tutor assessing student work. Be encouraging but accurate.",
                assessment_prompt,
                json_mode=True
            )
            
            if assessment_str:
                assessment = self.ai_service.parse_json_response(assessment_str)
                if assessment:
                    step3_data.sqlCorrectnessScore = assessment.get("sql_correctness", 0.0)
                    step3_data.explanationDepthScore = assessment.get("explanation_depth", 0.0)
                    step3_data.habitualMisunderstandings = assessment.get("misunderstandings", [])
                    
                    print(f"\n📊 Assessment Results:")
                    print(f"SQL Correctness: {step3_data.sqlCorrectnessScore:.1%}")
                    print(f"Explanation Quality: {step3_data.explanationDepthScore:.1%}")
                    print(f"\nFeedback: {assessment.get('feedback', '')}")
                    
                    if assessment.get("acceptable", False):
                        submission_accepted = True
                        print("\n✅ Well done! Your understanding is solid.")
                    else:
                        if step3_data.submissionCount < max_submissions:
                            print("\n🔄 Please revise your submission based on the feedback.")
        
        # Calculate assessment time
        step3_data.assessmentTimeMs = int((time.time() - start_time) * 1000)
        self.teaching_flow_data.step3 = step3_data
        
        return step3_data
    
    def run_step_4_guided_practice(self, topic: str, user_profile: UserProfile) -> Step4Data:
        """
        Step 4: Guided Practice (LeetCode-Style).
        Consolidates learned concepts and improves problem-solving ability through practical exercises.
        """
        print_header(f"Step 4: Guided Practice for '{topic}'")
        start_time = time.time()
        
        # Initialize step data using the data model
        step4_data = Step4Data(problemId=f"LC_{topic}_001")
        
        # Determine difficulty based on previous performance
        if self.teaching_flow_data.step3:
            avg_score = (self.teaching_flow_data.step3.sqlCorrectnessScore + 
                        self.teaching_flow_data.step3.explanationDepthScore) / 2
            if avg_score > 0.8:
                step4_data.difficultyLevel = 2  # Medium
            elif avg_score < 0.5:
                step4_data.difficultyLevel = 1  # Easy
        
        difficulty_map = {1: "Easy", 2: "Medium", 3: "Hard"}
        difficulty = difficulty_map[step4_data.difficultyLevel]
        
        system_prompt = """
You are an AI creating LeetCode-style SQL problems with adaptive difficulty.

## Response Format:
Generate response in JSON format:
```json
{
  "problem_title": "Problem title",
  "difficulty": "Easy/Medium/Hard",
  "problem_description": "Clear problem statement",
  "table_schemas": "CREATE TABLE statements",
  "sample_input": "Sample data description",
  "expected_output": "Expected result description",
  "hints": [
    "Hint 1 (basic guidance)",
    "Hint 2 (more specific)",
    "Hint 3 (detailed approach)"
  ],
  "solution_template": "Partial SQL with blanks for scaffolding"
}
```
"""
        
        user_prompt = f"Create a {difficulty} LeetCode-style problem for concept '{topic}'. Student level: {user_profile.level}."
        
        # Generate problem
        problem_str = self.ai_service.get_response(system_prompt, user_prompt, json_mode=True)
        if not problem_str:
            return step4_data
            
        problem_data = self.ai_service.parse_json_response(problem_str)
        if not problem_data:
            return step4_data
        
        # Display problem
        print(f"\n🏆 Challenge: {problem_data.get('problem_title', '')} ({difficulty})")
        print(f"\n{problem_data.get('problem_description', '')}")
        print(f"\nTable Schema:\n{problem_data.get('table_schemas', '')}")
        print(f"\nSample Input:\n{problem_data.get('sample_input', '')}")
        print(f"\nExpected Output:\n{problem_data.get('expected_output', '')}")
        
        # Practice loop with hints
        max_retries = 3
        hints = problem_data.get('hints', [])
        
        while step4_data.retryCount < max_retries and not step4_data.practiceSuccess:
            step4_data.retryCount += 1
            
            # Offer hint if not first attempt
            if step4_data.retryCount > 1 and step4_data.hintCount < len(hints):
                print("\n💡 Would you like a hint?")
                if get_user_input("Enter 'yes' for hint or 'no' to continue: ").lower() == 'yes':
                    print(f"\nHint {step4_data.hintCount + 1}: {hints[step4_data.hintCount]}")
                    step4_data.hintCount += 1
            
            # Collect solution
            print(f"\n📝 Your solution (Attempt {step4_data.retryCount}/{max_retries}):")
            print("Type 'DONE' on a new line when finished.")
            solution_lines = []
            while True:
                line = get_user_input("> ")
                if line.upper() == 'DONE':
                    break
                solution_lines.append(line)
            user_solution = "\n".join(solution_lines)
            
            # Evaluate solution
            eval_prompt = f"""
Evaluate this SQL solution for the problem about '{topic}'.

Solution:
{user_solution}

Expected approach: Using {topic} correctly.

Provide evaluation in JSON format:
{{
  "is_correct": true/false,
  "error_types": ["list of error types if any"],
  "feedback": "specific feedback"
}}
"""
            
            eval_str = self.ai_service.get_response(
                "You are evaluating SQL solutions. Be specific about errors.",
                eval_prompt,
                json_mode=True
            )
            
            if eval_str:
                evaluation = self.ai_service.parse_json_response(eval_str)
                if evaluation:
                    if evaluation.get("is_correct", False):
                        step4_data.practiceSuccess = True
                        print("\n✅ Excellent work! Your solution is correct.")
                    else:
                        step4_data.errorTypes.extend(evaluation.get("error_types", []))
                        print(f"\n❌ Not quite right. {evaluation.get('feedback', '')}")
                        
                        # Offer scaffolding on final attempt
                        if step4_data.retryCount == max_retries - 1:
                            print(f"\n📋 Here's a template to help you:")
                            print(problem_data.get('solution_template', '-- Fill in the blanks'))
        
        # Calculate practice time
        step4_data.practiceTimeMs = int((time.time() - start_time) * 1000)
        self.teaching_flow_data.step4 = step4_data
        
        return step4_data
    
    def run_step_5_reflection_poem(self, topic: str, user_profile: UserProfile) -> Step5Data:
        """
        Step 5: AI-Generated Reflection Poem.
        Enhances memory and metacognition through emotional and creative poetry summaries.
        """
        print_header(f"Step 5: Reflection & Poetry for '{topic}'")
        start_time = time.time()
        
        # Initialize step data using the data model
        step5_data = Step5Data()
        
        # Gather performance summary
        performance_summary = self._generate_performance_summary()
        
        system_prompt = """
You are a creative AI poet who writes educational poems about SQL concepts.

## Your Role:
- Create short, memorable poems (4-8 lines)
- Use rhyme and rhythm to reinforce key concepts
- Include specific references to common errors or insights from the student's journey
- Keep the tone encouraging and memorable

## Poem Structure:
- Use AABB or ABAB rhyme scheme
- Include the SQL concept name
- Reference the student's learning journey
- End with an encouraging note
"""
        
        user_prompt = f"""
Write a reflection poem about learning '{topic}'.

Student Performance Summary:
{performance_summary}

Focus on making it memorable and emotionally resonant while reinforcing the key concept.
"""
        
        # Generate poem
        poem = self.ai_service.get_response(system_prompt, user_prompt)
        if poem:
            step5_data.generatedPoem = poem
            print("\n✨ Your Learning Journey in Verse ✨\n")
            print("─" * 40)
            print(poem)
            print("─" * 40)
            
            # Get feedback
            print("\n📝 How did you find this poem?")
            print("Rate from 1 (not helpful) to 5 (very memorable):")
            
            rating_input = get_user_input("Your rating (1-5): ")
            try:
                rating = int(rating_input)
                if 1 <= rating <= 5:
                    step5_data.poemFeedbackRating = rating
                    
                    if rating <= 2:
                        print("\n🔄 Would you like me to create another poem?")
                        if get_user_input("Enter 'yes' or 'no': ").lower() == 'yes':
                            # Generate alternative poem
                            user_prompt += "\nThe student found the previous poem unhelpful. Create a different style focusing more on practical memory aids."
                            new_poem = self.ai_service.get_response(system_prompt, user_prompt)
                            if new_poem:
                                step5_data.generatedPoem = new_poem
                                print("\n✨ Alternative Reflection ✨\n")
                                print("─" * 40)
                                print(new_poem)
                                print("─" * 40)
                    else:
                        print("\n🎉 Glad you found it helpful! Keep up the great learning!")
            except ValueError:
                print("Invalid rating. Proceeding without rating.")
        
        # Calculate read time
        step5_data.poemReadTimeMs = int((time.time() - start_time) * 1000)
        self.teaching_flow_data.step5 = step5_data
        
        return step5_data
    
    def _generate_performance_summary(self) -> str:
        """Generate a summary of student performance across all steps."""
        summary_parts = []
        
        if self.teaching_flow_data.step1:
            reexplain_count = self.teaching_flow_data.step1.reExplanationCount
            if reexplain_count > 0:
                summary_parts.append(f"Needed {reexplain_count} re-explanations in concept introduction")
        
        if self.teaching_flow_data.step2:
            attempts = self.teaching_flow_data.step2.mcqAttempts
            if self.teaching_flow_data.step2.predictionAccuracy:
                summary_parts.append(f"Correctly predicted output in {attempts} attempt(s)")
            else:
                summary_parts.append(f"Struggled with prediction after {attempts} attempts")
        
        if self.teaching_flow_data.step3:
            sql_score = self.teaching_flow_data.step3.sqlCorrectnessScore
            summary_parts.append(f"SQL correctness score: {sql_score:.1%}")
            misunderstandings = self.teaching_flow_data.step3.habitualMisunderstandings
            if misunderstandings:
                summary_parts.append(f"Common errors: {', '.join(misunderstandings[:2])}")
        
        if self.teaching_flow_data.step4:
            if self.teaching_flow_data.step4.practiceSuccess:
                hints = self.teaching_flow_data.step4.hintCount
                summary_parts.append(f"Completed practice with {hints} hints")
            else:
                summary_parts.append("Working on mastering the practice problems")
        
        return "\n".join(summary_parts) if summary_parts else "Student is progressing through the material"
    
    def calculate_mastery_level(self) -> float:
        """
        Calculate overall mastery level based on the formula in the design document.
        """
        # Default values
        accuracy_3 = 0.5
        time_score_3 = 0.5
        success_rate_4 = 0.0
        time_score_4 = 0.5
        hint_score = 1.0
        retention_performance = 0.5  # Placeholder for future implementation
        
        # Calculate accuracy_3
        if self.teaching_flow_data.step3:
            step3 = self.teaching_flow_data.step3
            total_attempts = step3.submissionCount
            error_count = len(step3.habitualMisunderstandings)
            if total_attempts > 0:
                accuracy_3 = max(0, (total_attempts - error_count) / total_attempts)
            
            # Calculate time_score_3
            max_time_3 = 120000  # 120 seconds in ms
            duration_3 = step3.assessmentTimeMs
            if duration_3 > 0:
                time_score_3 = min(max_time_3 / duration_3, 1.0)
        
        # Calculate success_rate_4 and related scores
        if self.teaching_flow_data.step4:
            step4 = self.teaching_flow_data.step4
            success_rate_4 = 1.0 if step4.practiceSuccess else 0.0
            
            # Calculate time_score_4
            max_time_4 = 180000  # 180 seconds in ms
            duration_4 = step4.practiceTimeMs
            if duration_4 > 0:
                time_score_4 = min(max_time_4 / duration_4, 1.0)
            
            # Calculate hint_score
            max_hints = 3
            hint_count = step4.hintCount
            hint_score = max(0, 1 - (hint_count / max_hints))
        
        # Apply the mastery level formula
        mastery_level = (
            0.25 * accuracy_3 +
            0.15 * time_score_3 +
            0.30 * success_rate_4 +
            0.10 * time_score_4 +
            0.10 * hint_score +
            0.10 * retention_performance
        )
        
        return min(1.0, max(0.0, mastery_level))
    
    def get_chapter_data(self, user_id: str, chapter_id: str) -> ChapterData:
        """
        Get complete chapter data structure as defined in the design document.
        """
        chapter_data = ChapterData(
            userId=user_id,
            chapterId=chapter_id,
            steps=self.teaching_flow_data.to_dict(),
            masteryLevel=self.calculate_mastery_level()
        )
        return chapter_data 