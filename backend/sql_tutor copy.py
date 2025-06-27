import sys
import os
import json
from openai import OpenAI

# --- Configuration ---
# Use OpenRouter to access various models
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)
MODEL = "openai/gpt-4"

# --- Helper Functions ---
def get_user_input(prompt):
    """Get user input and handle exit command."""
    response = input(prompt).strip()
    if response.lower() in ['quit', 'exit']:
        print("\n👋 Thanks for learning! Exiting now.")
        sys.exit(0)
    return response

def get_gpt_response(prompt, json_mode=False):
    """Get a response from the language model."""
    try:
        response_kwargs = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "You are a friendly and encouraging SQL tutor. Your goal is to evaluate student responses accurately and provide clear, concise feedback to help them learn."},
                {"role": "user", "content": prompt}
            ]
        }
        if json_mode:
            response_kwargs["response_format"] = {"type": "json_object"}

        response = client.chat.completions.create(**response_kwargs)
        return response.choices[0].message.content
    except Exception as e:
        print(f"\n[Error: Could not get AI response. Skipping. Reason: {e}]")
        return None

def print_header(title):
    """Prints a formatted header for each step."""
    print("\n" + "="*50)
    print(f"🔹 {title}")
    print("="*50)

def wait_for_user():
    """Pauses the program and waits for the user to press Enter."""
    get_user_input("\nPress Enter to continue to the next step...")

# --- Learning Steps ---

def step_1_concept_guessing():
    """Step 1: Ask the user to guess the concept."""
    print_header("Step 1: Concept Guessing")
    
    # First attempt
    prompt = """
We have two tables: Students and Enrollments. We want to show only students who are actually enrolled in courses.

Which SQL JOIN function should we use?
A. INNER JOIN
B. LEFT JOIN
C. FULL OUTER JOIN
D. CROSS JOIN
\nYour answer (A/B/C/D): """
    answer = get_user_input(prompt).upper()

    if answer == 'A':
        print("\n✅ That's right! INNER JOIN is perfect for finding matching records in both tables.")
        return True

    # Second attempt
    print("\n❌ Not quite. Let's try another one.")
    prompt_2 = """
We want to list songs and the artists who sing them, but only if the artist exists in our Artists table.

Which JOIN is best for this?
A. FULL OUTER JOIN
B. INNER JOIN
C. LEFT JOIN
\nYour answer (A/B/C): """
    answer_2 = get_user_input(prompt_2).upper()

    if answer_2 == 'B':
        print("\n✅ Correct! You got it this time.")
        return True

    # Final explanation
    print("\nLet's clarify. INNER JOIN is like matching an RSVP list against the guests who actually attend a party. You only get the people who are on both lists.")
    print("In SQL, it means: `SELECT ... FROM table1 INNER JOIN table2 ON ...;` only returns rows where the join condition is met in both tables.")
    return False

def step_2_output_prediction():
    """Step 2: Ask the user to predict the output of a query."""
    print_header("Step 2: Output Prediction")
    
    # First attempt
    prompt = """
Here's a query:
SELECT s.name, c.title
FROM Students s
INNER JOIN Enrollments e ON s.student_id = e.student_id
INNER JOIN Courses c ON e.course_id = c.course_id;

What will this return?
A. All students and all courses
B. Only the names of students who are enrolled in a course, along with the course title
C. All students, even if they're not enrolled in any course
D. The query will return an error
\nYour answer (A/B/C/D): """
    answer = get_user_input(prompt).upper()

    if answer == 'B':
        print("\n✅ Exactly! The query links students to their enrollments, and enrollments to courses, so only enrolled students appear.")
        return True

    # Explanation and second attempt
    print("\n❌ That's a common mix-up. Let's break it down:")
    print("The query joins Students to Enrollments and then to Courses. An INNER JOIN requires a match in all tables. If a student isn't in the Enrollments table, they won't be in the final result.")
    
    prompt_2 = """
Given that logic, what would this query return?
SELECT a.name, al.title
FROM Artists a
INNER JOIN Albums al ON a.artist_id = al.artist_id;

A. All artists, even those without albums
B. Only artists who have at least one album in the Albums table
C. All albums, even if the artist is missing
\nYour answer (A/B/C): """
    answer_2 = get_user_input(prompt_2).upper()
    
    if answer_2 == 'B':
        print("\n✅ Perfect! You've got the hang of it now.")
    else:
        print("\nOkay, let's move on. The key is that INNER JOIN only includes results that have a match on both sides of the join.")
    return False

def step_3_write_and_explain():
    """Step 3: Have the user write and explain their own query with a stricter loop."""
    print_header("Step 3: Write & Explain Your Own Query")
    print("""
Now it's your turn.
1. Write a SQL query that uses INNER JOIN between any two tables (e.g., `Products` and `Categories`).
2. Then, explain in your own words what your query does and why INNER JOIN is the right choice.
""")

    while True:
        user_query = get_user_input("Your SQL Query: ")
        user_explanation = get_user_input("Your Explanation: ")

        eval_prompt = f"""
A student submitted a SQL query and an explanation. Please evaluate it based on the following rubric.

**Student's Query:**
```sql
{user_query}
```

**Student's Explanation:**
> {user_explanation}

**Grading Rubric:**
1.  **Query Correctness (Essential):** Does the query use valid `INNER JOIN` syntax? Is the `ON` condition logical?
2.  **Explanation Clarity (Essential):** Does the explanation clearly state what the query is supposed to do?
3.  **Justification (Essential):** Does the explanation justify *why* `INNER JOIN` was the correct choice for the stated goal (i.e., to find matching records)?

**Task:**
Grade the submission as one of three categories: `Excellent`, `So-so`, or `Failed`. Your response MUST start with "Grade: [Your Grade]".
- **Excellent**: All three rubric points are met. The query is correct and the explanation is clear and well-justified.
- **So-so**: The query might have minor errors, or the explanation is vague/partially incorrect.
- **Failed**: The query is fundamentally wrong, or the explanation shows a deep misunderstanding of `INNER JOIN`.

After the grade, provide brief, encouraging feedback. If the grade is not `Excellent`, provide a clear hint for improvement.
"""
        evaluation = get_gpt_response(eval_prompt)
        
        if not evaluation:
            print("\nCould not get evaluation. Let's move on for now.")
            return False

        print(f"\n--- Tutor Feedback ---\n{evaluation}\n--------------------")

        if "Grade: Excellent" in evaluation:
            print("\nFantastic work! You've clearly mastered this. Let's proceed.")
            return True
        else:
            print("\nYour attempt wasn't quite perfect. Take a look at the feedback and let's try that again.")
            # The loop will continue automatically.

def generate_sql_challenge():
    """Generates a dynamic LeetCode-style SQL challenge using GPT."""
    print("\n🔄 Generating a new SQL challenge for you...")
    prompt = """
Create a LeetCode-style SQL challenge that requires using an `INNER JOIN`.
Your response must be a JSON object with three keys:
1.  `challenge_title` (string): A short, descriptive title for the problem (e.g., "Find Employees in a Department").
2.  `challenge_description` (string): A clear description of the task, including the table schemas involved. Use Markdown for table names (e.g., `Employees`).
3.  `correct_solution` (string): The correct SQL query to solve the challenge.

Example:
{
  "challenge_title": "List Products and Their Categories",
  "challenge_description": "You are given two tables: `Products (product_id, name, category_id)` and `Categories (category_id, category_name)`. Write a query to list the name of each product along with its category name.",
  "correct_solution": "SELECT p.name, c.category_name FROM Products p INNER JOIN Categories c ON p.category_id = c.category_id;"
}
"""
    response = get_gpt_response(prompt, json_mode=True)
    if not response:
        return None
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        print("\n[Error: Could not parse the generated challenge. Using a fallback.]")
        return None

def step_4_practice_challenge():
    """Step 4: A dynamically generated practice challenge."""
    print_header("Step 4: Practice Challenge")

    challenge = generate_sql_challenge()
    if not challenge:
        # Fallback challenge if generation fails
        challenge = {
            "challenge_title": "Fallback Challenge: Students in Multiple Courses",
            "challenge_description": "Write a SQL query to list the names of students who are enrolled in more than one course. Assume you have `Students(student_id, name)` and `Enrollments(student_id, course_id)` tables.",
            "correct_solution": "SELECT s.name FROM Students s INNER JOIN Enrollments e ON s.student_id = e.student_id GROUP BY s.student_id, s.name HAVING COUNT(e.course_id) > 1;"
        }

    print(f"Challenge: {challenge['challenge_title']}")
    print(challenge['challenge_description'])

    for i in range(2): # Allow two attempts
        attempt_num = i + 1
        print(f"\n--- Attempt #{attempt_num} ---")
        user_query = get_user_input("Your SQL Query: ")

        eval_prompt = f"""
A student is solving this SQL challenge: "{challenge['challenge_description']}"
The student's submitted query is:
```sql
{user_query}
```
The correct solution is:
```sql
{challenge['correct_solution']}
```
Is the student's query correct? It may be syntactically different but semantically correct.
Your response MUST start with "Correct" or "Incorrect".
If "Incorrect", briefly explain the mistake (e.g., "This is missing a GROUP BY clause" or "The HAVING condition is not quite right").
"""
        evaluation = get_gpt_response(eval_prompt)

        if not evaluation:
            print("\nCould not get evaluation. Let's move on for now.")
            break
            
        print(f"\n--- Tutor Feedback ---\n{evaluation}\n--------------------")

        if evaluation.startswith("Correct"):
            print("\n✅ Great work! You solved the challenge.")
            return True
    
    print("\nThat was a tough one! Here's a correct solution:")
    print(f"```sql\n{challenge['correct_solution']}\n```")
    return False

def step_5_summary(results):
    """Step 5: Summarize performance and suggest next steps."""
    print_header("Step 5: Summary")
    print("🎉 Awesome job! Here's a summary of what you've done:")
    
    status_1 = "✅" if results.get('step1', False) else "❌"
    status_2 = "✅" if results.get('step2', False) else "❌"
    status_3 = "✅" if results.get('step3', False) else "❌"
    status_4 = "✅" if results.get('step4', False) else "❌"

    print(f"- Step 1: Concept recognition {status_1}")
    print(f"- Step 2: Query prediction {status_2}")
    print(f"- Step 3: Wrote your own JOIN {status_3}")
    print(f"- Step 4: Solved a challenge {status_4}")

    print("\nNext step: Want to try `LEFT JOIN` or `GROUP BY` next?")
    print("You can type 'restart' to review, or 'exit' to finish.")

def main():
    """Main function to run the SQL tutor with improved pacing."""
    while True:
        results = {}
        
        results['step1'] = step_1_concept_guessing()
        wait_for_user()

        results['step2'] = step_2_output_prediction()
        wait_for_user()

        results['step3'] = step_3_write_and_explain()
        wait_for_user()

        results['step4'] = step_4_practice_challenge()
        wait_for_user()
        
        step_5_summary(results)
        
        choice = get_user_input("\nYour choice: ").lower()
        if choice != 'restart':
            print("\nHappy coding!")
            break

if __name__ == "__main__":
    main() 