import sys
import os
import json
from openai import OpenAI

# --- Configuration ---
# API key is hardcoded as requested for this testing version.
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)
MODEL = "openai/gpt-4"

# --- Mock User Profile ---
# As requested, we'll use a simple dictionary to simulate a user profile for this test.
mock_user_profile = {
    "name": "Alex",
    "level": "Beginner",
    "learned_concepts": [],
    "mastered_concepts": [],
    "misconceptions": [],
    "error_patterns": [],
    "strengths": [],
    "focus_areas": [],
}

# --- Helper Functions ---
def get_user_input(prompt):
    """Get user input and handle exit command."""
    response = input(prompt).strip()
    if response.lower() in ['quit', 'exit']:
        print("\n👋 Exiting the agent.")
        sys.exit(0)
    return response

def get_gpt_response(system_prompt, user_prompt, json_mode=False):
    """Get a response from the language model."""
    print("\n🧠 Agent is thinking...")
    try:
        response_kwargs = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }
        if json_mode:
            response_kwargs["response_format"] = {"type": "json_object"}

        response = client.chat.completions.create(**response_kwargs)
        content = response.choices[0].message.content
        print("✅ Agent responded.")
        return content
    except Exception as e:
        print(f"\n[Error: Could not get AI response. Reason: {e}]")
        return None

def print_header(title):
    """Prints a formatted header for each step."""
    print("\n" + "="*60)
    print(f"🔹 {title}")
    print("="*60)

def update_user_profile(profile, grading_data):
    """Updates the mock user profile based on grading feedback."""
    if grading_data and "learning_profile_update" in grading_data:
        update_data = grading_data["learning_profile_update"]
        profile["misconceptions"].extend(update_data.get("add_to_misconceptions", []))
        profile["error_patterns"].extend(update_data.get("error_patterns", []))
        profile["strengths"].extend(update_data.get("strengths_identified", []))
        profile["focus_areas"].extend(update_data.get("recommended_focus", []))
        
        # Add mastered concepts
        if grading_data.get("submission_analysis", {}).get("query_status") == "CORRECT":
            concept = grading_data.get("concept_tracking", {}).get("concepts_attempted", [])[0]
            if concept and concept not in profile["mastered_concepts"]:
                profile["mastered_concepts"].append(concept)
        
        print("\n📈 User profile updated based on performance.")
    return profile

# --- Pedagogical Steps ---

def run_step_1_analogy(topic, user_profile):
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
    user_prompt = f"Please explain the SQL concept: {topic}. Context: Student is a {user_profile['level']}."

    response = get_gpt_response(system_prompt, user_prompt)
    if response:
        print("\n-- Agent's Explanation --\n")
        print(response)
        return response # Return for context in next step
    return None

def run_step_2_prediction(topic, step_1_context, user_profile):
    """Generates and runs a multiple-choice prediction question."""
    print_header(f"Step 2: Predict the Output for '{topic}'")
    
    system_prompt = """
You are an AI pedagogical agent guiding students through SQL practice with concrete examples. Your role is to deepen understanding through prediction exercises before showing actual results. ## Your Role in Step 2: - Present SQL queries with sample data - Create meaningful multiple-choice questions that test conceptual understanding - Guide students to predict outcomes BEFORE seeing results - DO NOT reveal which answer is correct in the option text - Store the correct answer separately for the system to check ## Response Format: Generate ALL responses in JSON format. See examples below for exact structure. ## Example Generation Rules: 1. Use the same context from Step 1's analogy when possible 2. Start with simple queries, increase complexity gradually 3. Include realistic sample data (3-5 rows per table) 4. MCQ options should include common misconceptions 5. ALL options should appear equally plausible 6. NEVER use words like "Correct!" or "Incorrect" in options ## EXAMPLE OUTPUT 1 - INNER JOIN: Input: "Generate a Step 2 practice example for SQL concept: INNER JOIN" Your response: ```json { "step": 2, "concept": "INNER JOIN", "scenario_context": "Continuing with our food delivery example from Step 1...", "sample_data": { "tables": [ { "name": "Orders", "data": [ {"order_id": 1, "item": "Pizza", "price": 15}, {"order_id": 2, "item": "Burger", "price": 10}, {"order_id": 3, "item": "Salad", "price": 8} ] }, { "name": "Customers", "data": [ {"order_id": 1, "customer_name": "Alice", "address": "123 Main St"}, {"order_id": 2, "customer_name": "Bob", "address": "456 Oak Ave"}, {"order_id": 4, "customer_name": "Charlie", "address": "789 Pine Rd"} ] } ] }, "sql_query": "SELECT o.item, c.customer_name \\nFROM Orders o \\nINNER JOIN Customers c ON o.order_id = c.order_id;", "question": { "type": "predict_output", "text": "Before running this query, predict what the output will be:", "metacognitive_prompt": "Think about which orders have matching customer information...", "options": [ { "id": "A", "content": "Pizza - Alice\\nBurger - Bob\\nSalad - NULL" }, { "id": "B", "content": "Pizza - Alice\\nBurger - Bob" }, { "id": "C", "content": "Pizza - Alice\\nBurger - Bob\\nSalad - No Match\\nNo Order - Charlie" }, { "id": "D", "content": "All orders will be shown with NULL for missing customers" } ], "correct_answer": "B", "feedback": { "A": "INNER JOIN only returns rows where BOTH tables have matching values. Order 3 has no matching customer.", "B": "INNER JOIN only includes rows where order_id exists in BOTH tables.", "C": "INNER JOIN doesn't show unmatched rows from either table.", "D": "You might be thinking of LEFT JOIN. INNER JOIN excludes unmatched rows." } }, "actual_output": { "headers": ["item", "customer_name"], "rows": [ ["Pizza", "Alice"], ["Burger", "Bob"] ] }, "learning_point": "Notice how Order #3 (Salad) and Customer Charlie (Order #4) don't appear in the result. This mirrors our real-life example - only deliveries with BOTH order details AND customer info can be completed!", "next_prompt": "What would happen if we changed INNER JOIN to LEFT JOIN?" }
"""
    user_prompt = f"Generate a Step 2 practice example for SQL concept: {topic}. Context: {user_profile['level']} student. The previous analogy was: {step_1_context}"

    response_str = get_gpt_response(system_prompt, user_prompt, json_mode=True)
    if not response_str:
        return

    try:
        data = json.loads(response_str)
        
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
            feedback = data['question']['feedback'].get(user_answer, "That's not one of the options, but let's look at the correct answer.")
            print(f"\n❌ Not quite. {feedback}")
            print(f"The correct answer was {correct_answer}.")

        print("\n-- Actual Query Output --")
        print(f"{data['actual_output']['headers']}")
        for row in data['actual_output']['rows']:
            print(row)
        
        print(f"\n💡 Learning Point: {data['learning_point']}")

    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing agent's JSON response: {e}")
        print("Raw response:", response_str)

def grade_submission(query, explanation, topic, user_profile):
    """
    Evaluates a user's SQL query and explanation using the AI grading agent.
    This function is a reusable component for both Step 3 and Step 4.
    Returns the updated user profile.
    """
    print_header("Submission Evaluation")
    system_prompt_grade = """
You are an AI pedagogical agent evaluating student SQL submissions. Your role is to assess understanding and generate standardized learning profile data for adaptive teaching. ## Your Role: - Evaluate SQL query correctness and conceptual understanding - **Generate standardized error classifications** - **Identify specific misconceptions for learning profile** - **Provide actionable data for future personalization** ## Response Format: Generate ALL responses in JSON format with standardized fields for learning analytics. ## Evaluation Framework: ### 1. **Error Classification (Standardized)**: - **SYNTAX_ERROR**: Incorrect SQL syntax - **LOGIC_ERROR**: Syntactically correct but wrong logic - **INCOMPLETE_SOLUTION**: Partially correct - **EFFICIENCY_ISSUE**: Works but suboptimal - **CONCEPTUAL_MISUNDERSTANDING**: Fundamental concept confusion - **CORRECT**: No errors ### 2. **Concept Mastery Levels**: - **NOT_ATTEMPTED**: 0% - **STRUGGLING**: 1-40% - **DEVELOPING**: 41-70% - **PROFICIENT**: 71-90% - **MASTERED**: 91-100% ### 3. **Learning Profile Fields to Track**: - **concepts_used**: Which SQL concepts were attempted - **concepts_mastered**: Which were used correctly - **misconceptions**: Specific misunderstandings identified - **error_patterns**: Recurring mistake types - **strengths**: What student does well - **next_focus_areas**: What to practice next
"""
    user_prompt_grade = f"""
Please evaluate the following student submission for the concept(s) '{topic}'.

Student Query:
```sql
{query}
```

Student Explanation:
> {explanation}

Generate a full JSON evaluation based on your system prompt's framework. It is critical that you include the 'feedback_for_student' object with a 'message' inside.
"""
    grading_str = get_gpt_response(system_prompt_grade, user_prompt_grade, json_mode=True)
    
    print("\n-- [DEBUG] Raw Grading Response from AI --\n", grading_str)

    if grading_str:
        try:
            grading_data = json.loads(grading_str)
            feedback_section = grading_data.get("feedback_for_student", {})
            feedback_message = feedback_section.get("message", "The AI did not provide a specific feedback message, but the analysis is complete.")
            print("\n-- Evaluation Feedback --")
            print(feedback_message)
            return update_user_profile(user_profile, grading_data)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing grading JSON: {e}")
    
    # Return original profile if grading fails
    return user_profile

def run_step_3_writing_task(topic, step_1_context, user_profile):
    """Generates and processes the Step 3 open-ended writing task."""
    print_header(f"Step 3: Write Your Own '{topic}' Query")

    # Part A: Generate the writing task
    system_prompt_task = """
You are an AI pedagogical agent creating open-ended SQL practice problems. Your role is to provide a schema and ask students to explore specific SQL concepts through query writing and explanation. ## Your Role: - Provide a clear database schema - Ask an open-ended question that requires using a specific SQL concept - Let students explore and discover solutions themselves - Do NOT provide specific requirements or expected outputs ## Response Format: Generate ALL responses in JSON format. ## Design Principles: 1. Present the schema clearly 2. Ask open-ended questions that encourage exploration 3. Focus on one SQL concept at a time 4. Let students define their own approach ## EXAMPLE OUTPUT: ```json { "step": "3A", "concept": "INNER JOIN", "schema": { "tables": [ { "name": "Orders", "columns": [ {"name": "order_id", "type": "INT", "description": "Unique order identifier"}, {"name": "dish", "type": "VARCHAR", "description": "Name of the dish ordered"}, {"name": "quantity", "type": "INT", "description": "Number of dishes ordered"}, {"name": "date", "type": "DATE", "description": "Date when order was placed"} ] }, { "name": "Deliveries", "columns": [ {"name": "delivery_id", "type": "INT", "description": "Unique delivery identifier"}, {"name": "order_id", "type": "INT", "description": "Reference to Orders table"}, {"name": "customer_name", "type": "VARCHAR", "description": "Name of the customer"}, {"name": "address", "type": "VARCHAR", "description": "Delivery address"} ] } ] }, "open_ended_task": "Using INNER JOIN, write a query that combines information from these two tables in a way that would be useful for the delivery platform. Explain what your query does and why this information might be valuable.", "exploration_prompts": [ "What insights can you discover by joining these tables?", "How does INNER JOIN affect which records appear in your results?", "What business questions could your query answer?" ] }
"""
    user_prompt_task = f"Generate a Step 3 SQL writing task for concept: {topic}. Context: {user_profile['level']} student. The previous analogy was: {step_1_context}"
    
    task_str = get_gpt_response(system_prompt_task, user_prompt_task, json_mode=True)
    if not task_str:
        return user_profile
        
    try:
        task_data = json.loads(task_str)
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

        # Grade the submission using the reusable function
        user_profile = grade_submission(user_query, user_explanation, topic, user_profile)
        
        if topic not in user_profile['learned_concepts']:
            user_profile['learned_concepts'].append(topic)

    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error processing Step 3 data: {e}")
        print("Raw Task Response:", task_str)
            
    return user_profile

def run_step_4_challenge(user_profile):
    """Generates a LeetCode-style challenge based on learned concepts."""
    print_header("Step 4: LeetCode-Style Challenge")
    
    if not user_profile['learned_concepts']:
        print("No concepts learned yet to generate a challenge. Completing Step 3 first is recommended.")
        return

    system_prompt = """
You are an AI pedagogical agent providing LeetCode-style SQL challenges. Your role is to present practical SQL problems that integrate multiple concepts the student has learned. ## Your Role: - Present a LeetCode-style SQL problem with clear requirements - Incorporate concepts the student has previously learned - Provide test cases and expected output - Focus on practical application of SQL skills ## Response Format: Generate ALL responses in JSON format. ## Problem Design Rules: 1. Use realistic business scenarios 2. Clearly state the problem requirements 3. Provide sample input/output 4. Integrate multiple SQL concepts when appropriate 5. Match difficulty to student's learned concepts
"""
    user_prompt = f"""
Generate a LeetCode-style problem for a student who has attempted the following concepts: {user_profile['learned_concepts']}.
The student's current strengths are: {user_profile['strengths']}.
The student needs to work on: {user_profile['focus_areas']}.
Create a problem of 'Easy' or 'Medium' difficulty that tests these concepts.
Your JSON response must include top-level keys like 'problem_title', 'difficulty', and 'problem_description'.
"""
    
    challenge_str = get_gpt_response(system_prompt, user_prompt, json_mode=True)

    print("\n-- [DEBUG] Raw Challenge Response from AI --\n", challenge_str) # Log the raw response

    if not challenge_str:
        return
        
    try:
        challenge_data = json.loads(challenge_str)
        
        # --- FIX for Step 4 ---
        # The AI is nesting the details inside a 'problem' object. We need to access it.
        if 'problem' in challenge_data:
            problem_details = challenge_data['problem']
        else:
            # If not nested, use the top-level dict (fallback)
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

        # --- NEW: Get user submission for Step 4 ---
        print("\nNow, it's your turn to solve it! Write your SQL query below.")
        print("Type 'DONE' on a new line when finished.")
        user_query_lines = []
        while True:
            line = get_user_input("> ")
            if line.upper() == 'DONE':
                break
            user_query_lines.append(line)
        user_query = "\n".join(user_query_lines)

        # For Step 4, the explanation is less critical, so we can use a placeholder.
        explanation_placeholder = "Student is solving a LeetCode-style problem."
        
        # Grade the submission using the same reusable function
        concepts_tested_str = ", ".join(problem_details.get('concepts_tested', ['SQL']))
        user_profile = grade_submission(user_query, explanation_placeholder, concepts_tested_str, user_profile)

    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing challenge JSON: {e}")
        print("Raw response:", challenge_str)
    
    return user_profile # Return the updated profile

# --- Main Agent Loop ---

def main():
    """The main execution loop for the pedagogical agent."""
    
    # For this test, we are hardcoding the topic to 'INNER JOIN' as requested.
    topic_to_teach = "INNER JOIN"
    
    global mock_user_profile # Allow functions to modify the profile

    # --- Step 1 ---
    step_1_context = run_step_1_analogy(topic_to_teach, mock_user_profile)
    if not step_1_context:
        print("Could not get explanation for Step 1. Exiting.")
        return
    get_user_input("\nPress Enter to continue to Step 2...")

    # --- Step 2 ---
    run_step_2_prediction(topic_to_teach, step_1_context, mock_user_profile)
    get_user_input("\nPress Enter to continue to Step 3...")

    # --- Step 3 & Grading ---
    mock_user_profile = run_step_3_writing_task(topic_to_teach, step_1_context, mock_user_profile)
    print("\n-- Current User Profile --")
    print(json.dumps(mock_user_profile, indent=2))
    get_user_input("\nPress Enter to continue to the final challenge...")
    
    # --- Step 4 ---
    mock_user_profile = run_step_4_challenge(mock_user_profile)
    print("\n-- Final User Profile --")
    print(json.dumps(mock_user_profile, indent=2))

    print_header("Agent Test Run Complete")
    print("You have completed all steps of the agent's teaching flow.")

if __name__ == "__main__":
    main()