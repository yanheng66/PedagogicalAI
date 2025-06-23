"""
Teaching controller for managing the 4-step instructional flow.
"""

import json
from typing import Optional
from services.ai_service import AIService
from services.grading_service import GradingService
from models.user_profile import UserProfile
from utils.io_helpers import get_user_input, print_header


class TeachingController:
    """Controller for managing the instructional flow."""
    
    def __init__(self):
        self.ai_service = AIService()
        self.grading_service = GradingService()
    
    def run_step_1_analogy(self, topic: str, user_profile: UserProfile) -> Optional[str]:
        """Generates and displays a real-life analogy for a given SQL concept."""
        print_header(f"Step 1: Real-Life Analogy for '{topic}'")
        
        system_prompt = """
You are an AI pedagogical agent specialized in teaching SQL through real-life analogies. Your teaching philosophy emphasizes metacognition and building intuition before introducing technical concepts.

## Your Role:
- Use familiar everyday scenarios to explain SQL concepts
- Guide students to reflect on their learning process
- Build conceptual understanding before syntax
- Adapt examples to be culturally relevant and relatable

## Teaching Framework for Step 1 - Real-Life Analogies:

### Response Structure:
1. **Opening Hook**: Ask about a familiar experience (1-2 sentences)
2. **Scenario Setup**: Describe the situation in detail (2-3 sentences)
3. **Problem Introduction**: Present the challenge (1-2 sentences)
4. **Bridge to SQL**: Connect scenario to SQL concept (2-3 sentences)
5. **Concept Introduction**: Name the SQL feature (1-2 sentences)
6. **Metacognitive Prompt**: Include a reflection question

### Analogy Bank:
- INNER JOIN → Order-Customer matching, Student-Class enrollment
- LEFT JOIN → Party guest list (all invited, some attended)
- RIGHT JOIN → Work schedule (all days, some with shifts)
- GROUP BY → Organizing receipts by category, Grouping students by grade
- WHERE → Filtering emails, Finding products in budget
- COUNT/SUM/AVG → Event attendance, Shopping totals, Test averages
- DISTINCT → Removing duplicate contacts
- ORDER BY → Sorting music playlists, Arranging books

### Adaptation Rules:
- Use shopping/food examples for everyday contexts
- Use school/gaming examples for younger learners
- Use business/office examples for professionals
- Keep cultural context in mind

### Metacognitive Elements: Always end with ONE of these awareness statements: - "Notice that in this example, [real-world element] represents [SQL concept]." - "This same pattern appears in many daily situations - like [provide 2-3 quick examples]." - "If conditions changed (e.g., [specific change]), the result would be [outcome] - just like in SQL."
"""
        user_prompt = f"Please explain the SQL concept: {topic}. Context: Student is a {user_profile.level}."

        response = self.ai_service.get_response(system_prompt, user_prompt)
        if response:
            print("\n-- Agent's Explanation --\n")
            print(response)
            return response
        return None

    def run_step_2_prediction(self, topic: str, step_1_context: str, user_profile: UserProfile) -> None:
        """Generates and runs a multiple-choice prediction question."""
        print_header(f"Step 2: Predict the Output for '{topic}'")
        
        system_prompt = """
You are an AI pedagogical agent guiding students through SQL practice with concrete examples. Your role is to deepen understanding through prediction exercises before showing actual results. ## Your Role in Step 2: - Present SQL queries with sample data - Create meaningful multiple-choice questions that test conceptual understanding - Guide students to predict outcomes BEFORE seeing results - DO NOT reveal which answer is correct in the option text - Store the correct answer separately for the system to check ## Response Format: Generate ALL responses in JSON format. See examples below for exact structure. ## Example Generation Rules: 1. Use the same context from Step 1's analogy when possible 2. Start with simple queries, increase complexity gradually 3. Include realistic sample data (3-5 rows per table) 4. MCQ options should include common misconceptions 5. ALL options should appear equally plausible 6. NEVER use words like "Correct!" or "Incorrect" in options ## EXAMPLE OUTPUT 1 - INNER JOIN: Input: "Generate a Step 2 practice example for SQL concept: INNER JOIN" Your response: ```json { "step": 2, "concept": "INNER JOIN", "scenario_context": "Continuing with our food delivery example from Step 1...", "sample_data": { "tables": [ { "name": "Orders", "data": [ {"order_id": 1, "item": "Pizza", "price": 15}, {"order_id": 2, "item": "Burger", "price": 10}, {"order_id": 3, "item": "Salad", "price": 8} ] }, { "name": "Customers", "data": [ {"order_id": 1, "customer_name": "Alice", "address": "123 Main St"}, {"order_id": 2, "customer_name": "Bob", "address": "456 Oak Ave"}, {"order_id": 4, "customer_name": "Charlie", "address": "789 Pine Rd"} ] } ] }, "sql_query": "SELECT o.item, c.customer_name \\nFROM Orders o \\nINNER JOIN Customers c ON o.order_id = c.order_id;", "question": { "type": "predict_output", "text": "Before running this query, predict what the output will be:", "metacognitive_prompt": "Think about which orders have matching customer information...", "options": [ { "id": "A", "content": "Pizza - Alice\\nBurger - Bob\\nSalad - NULL" }, { "id": "B", "content": "Pizza - Alice\\nBurger - Bob" }, { "id": "C", "content": "Pizza - Alice\\nBurger - Bob\\nSalad - No Match\\nNo Order - Charlie" }, { "id": "D", "content": "All orders will be shown with NULL for missing customers" } ], "correct_answer": "B", "feedback": { "A": "INNER JOIN only returns rows where BOTH tables have matching values. Order 3 has no matching customer.", "B": "INNER JOIN only includes rows where order_id exists in BOTH tables.", "C": "INNER JOIN doesn't show unmatched rows from either table.", "D": "You might be thinking of LEFT JOIN. INNER JOIN excludes unmatched rows." } }, "actual_output": { "headers": ["item", "customer_name"], "rows": [ ["Pizza", "Alice"], ["Burger", "Bob"] ] }, "learning_point": "Notice how Order #3 (Salad) and Customer Charlie (Order #4) don't appear in the result. This mirrors our real-life example - only deliveries with BOTH order details AND customer info can be completed!", "next_prompt": "What would happen if we changed INNER JOIN to LEFT JOIN?" }
"""
        user_prompt = f"Generate a Step 2 practice example for SQL concept: {topic}. Context: {user_profile.level} student. The previous analogy was: {step_1_context}"

        response_str = self.ai_service.get_response(system_prompt, user_prompt, json_mode=True)
        if not response_str:
            return

        data = self.ai_service.parse_json_response(response_str)
        if not data:
            return
            
        # Display the problem
        print(f"\n-- Scenario: {data['scenario_context']} --\n")
        for table in data['sample_data']['tables']:
            print(f"Table: {table['name']}")
            print(json.dumps(table['data'], indent=2))
        print(f"\nSQL Query:\n{data['sql_query']}\n")
        
        # Ask the question
        print(data['question']['text'])
        print(f"🤔 {data['question']['metacognitive_prompt']}")
        for option in data['question']['options']:
            content_cleaned = option['content'].replace('\\n', ' ')
            print(f"  {option['id']}. {content_cleaned}")
        
        user_answer = get_user_input("\nYour prediction (A/B/C/D): ").upper()
        
        # Provide feedback
        correct_answer = data['question']['correct_answer']
        if user_answer == correct_answer:
            print(f"\n✅ Correct! {data['question']['feedback'][correct_answer]}")
        else:
            feedback = data['question']['feedback'].get(user_answer, 
                "That's not one of the options, but let's look at the correct answer.")
            print(f"\n❌ Not quite. {feedback}")
            print(f"The correct answer was {correct_answer}.")

        print("\n-- Actual Query Output --")
        print(f"{data['actual_output']['headers']}")
        for row in data['actual_output']['rows']:
            print(row)
        
        print(f"\n💡 Learning Point: {data['learning_point']}")

    def run_step_3_writing_task(self, topic: str, step_1_context: str, user_profile: UserProfile) -> UserProfile:
        """Generates and processes the Step 3 open-ended writing task."""
        print_header(f"Step 3: Write Your Own '{topic}' Query")

        # Part A: Generate the writing task
        system_prompt_task = """
You are an AI pedagogical agent creating open-ended SQL practice problems. Your role is to provide a schema and ask students to explore specific SQL concepts through query writing and explanation. ## Your Role: - Provide a clear database schema - Ask an open-ended question that requires using a specific SQL concept - Let students explore and discover solutions themselves - Do NOT provide specific requirements or expected outputs ## Response Format: Generate ALL responses in JSON format. ## Design Principles: 1. Present the schema clearly 2. Ask open-ended questions that encourage exploration 3. Focus on one SQL concept at a time 4. Let students define their own approach ## EXAMPLE OUTPUT: ```json { "step": "3A", "concept": "INNER JOIN", "schema": { "tables": [ { "name": "Orders", "columns": [ {"name": "order_id", "type": "INT", "description": "Unique order identifier"}, {"name": "dish", "type": "VARCHAR", "description": "Name of the dish ordered"}, {"name": "quantity", "type": "INT", "description": "Number of dishes ordered"}, {"name": "date", "type": "DATE", "description": "Date when order was placed"} ] }, { "name": "Deliveries", "columns": [ {"name": "delivery_id", "type": "INT", "description": "Unique delivery identifier"}, {"name": "order_id", "type": "INT", "description": "Reference to Orders table"}, {"name": "customer_name", "type": "VARCHAR", "description": "Name of the customer"}, {"name": "address", "type": "VARCHAR", "description": "Delivery address"} ] } ] }, "open_ended_task": "Using INNER JOIN, write a query that combines information from these two tables in a way that would be useful for the delivery platform. Explain what your query does and why this information might be valuable.", "exploration_prompts": [ "What insights can you discover by joining these tables?", "How does INNER JOIN affect which records appear in your results?", "What business questions could your query answer?" ] }
"""
        user_prompt_task = f"Generate a Step 3 SQL writing task for concept: {topic}. Context: {user_profile.level} student. The previous analogy was: {step_1_context}"
        
        task_str = self.ai_service.get_response(system_prompt_task, user_prompt_task, json_mode=True)
        if not task_str:
            return user_profile
            
        task_data = self.ai_service.parse_json_response(task_str)
        if not task_data:
            return user_profile
            
        print("\n-- Your Task --")
        for table in task_data['schema']['tables']:
            print(f"\nTable: {table['name']}")
            for column in table['columns']:
                print(f"  - {column['name']} ({column['type']}): {column['description']}")
        
        print(f"\nChallenge: {task_data['open_ended_task']}")
        for prompt in task_data['exploration_prompts']:
            print(f"  - {prompt}")

        # Part B: Get user submission
        print("\nPlease write your SQL query below. Type 'DONE' on a new line when finished.")
        user_query_lines = []
        while True:
            line = get_user_input("> ")
            if line.upper() == 'DONE':
                break
            user_query_lines.append(line)
        user_query = "\n".join(user_query_lines)

        print("\nNow, briefly explain what your query does. Type 'DONE' on a new line when finished.")
        user_explanation_lines = []
        while True:
            line = get_user_input("> ")
            if line.upper() == 'DONE':
                break
            user_explanation_lines.append(line)
        user_explanation = "\n".join(user_explanation_lines)

        # Grade the submission
        user_profile = self.grading_service.grade_submission(user_query, user_explanation, topic, user_profile)
        user_profile.add_learned_concept(topic)
            
        return user_profile

    def run_step_4_challenge(self, user_profile: UserProfile) -> UserProfile:
        """Generates a LeetCode-style challenge based on learned concepts."""
        print_header("Step 4: LeetCode-Style Challenge")
        
        if not user_profile.learned_concepts:
            print("No concepts learned yet to generate a challenge. Completing Step 3 first is recommended.")
            return user_profile

        system_prompt = """
You are an AI pedagogical agent providing LeetCode-style SQL challenges. Your role is to present practical SQL problems that integrate multiple concepts the student has learned. ## Your Role: - Present a LeetCode-style SQL problem with clear requirements - Incorporate concepts the student has previously learned - Provide test cases and expected output - Focus on practical application of SQL skills ## Response Format: Generate ALL responses in JSON format. ## Problem Design Rules: 1. Use realistic business scenarios 2. Clearly state the problem requirements 3. Provide sample input/output 4. Integrate multiple SQL concepts when appropriate 5. Match difficulty to student's learned concepts
"""
        user_prompt = f"""
Generate a LeetCode-style problem for a student who has attempted the following concepts: {user_profile.learned_concepts}.
The student's current strengths are: {user_profile.strengths}.
The student needs to work on: {user_profile.focus_areas}.
Create a problem of 'Easy' or 'Medium' difficulty that tests these concepts.
Your JSON response must include top-level keys like 'problem_title', 'difficulty', and 'problem_description'.
"""
        
        challenge_str = self.ai_service.get_response(system_prompt, user_prompt, json_mode=True)

        print("\n-- [DEBUG] Raw Challenge Response from AI --\n", challenge_str)

        if not challenge_str:
            return user_profile
            
        challenge_data = self.ai_service.parse_json_response(challenge_str)
        if not challenge_data:
            return user_profile
            
        # Handle nested problem structure
        if 'problem' in challenge_data:
            problem_details = challenge_data['problem']
        else:
            problem_details = challenge_data

        # Use .get() for all fields to prevent crashes from missing keys
        title = problem_details.get('problem_title') or problem_details.get('title', 'N/A')
        difficulty = problem_details.get('difficulty', 'N/A')
        description = problem_details.get('problem_description') or problem_details.get('description', 'No description provided.')
        concepts_tested = problem_details.get('concepts_tested', [])

        print(f"\nChallenge: {title} ({difficulty})")
        
        if concepts_tested:
             print(f"Concepts Tested: {concepts_tested}")

        print("\nDescription:")
        print(description)
        
        print("\nThis would be a fully interactive challenge. For now, the agent has generated the problem description.")

        # Get user submission for Step 4
        print("\nNow, it's your turn to solve it! Write your SQL query below.")
        print("Type 'DONE' on a new line when finished.")
        user_query_lines = []
        while True:
            line = get_user_input("> ")
            if line.upper() == 'DONE':
                break
            user_query_lines.append(line)
        user_query = "\n".join(user_query_lines)

        # For Step 4, the explanation is less critical, so we use a placeholder
        explanation_placeholder = "Student is solving a LeetCode-style problem."
        
        # Grade the submission
        concepts_tested_str = ", ".join(problem_details.get('concepts_tested', ['SQL']))
        user_profile = self.grading_service.grade_submission(user_query, explanation_placeholder, concepts_tested_str, user_profile)

        return user_profile 