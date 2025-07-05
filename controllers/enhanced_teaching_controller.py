"""
Enhanced teaching controller with comprehensive data tracking and user modeling.
"""

import json
import time
import re
import random
from typing import Optional, List, Dict
from datetime import datetime
from services.ai_service import AIService
from services.grading_service import GradingService
from models.user_profile import UserProfile
from utils.io_helpers import get_user_input, print_header

import sqlite3
import uuid


class EnhancedTeachingController:
    """Enhanced controller with comprehensive user modeling and data tracking."""
    
    def __init__(self, user_id: str = "default_user"):
        self.ai_service = AIService()
        self.grading_service = GradingService()
        self.user_id = user_id
        self.session_id = None
        self.concept_id = None
        self.current_step_start_time = None
        self.current_interaction_id = None
        
        # Enhanced tracking
        self.keystroke_tracker = {"deletions": 0, "pauses": []}
        self.step3_attempts = []
        self.session_start_time = None
        # Store Step 3 performance score for adaptive difficulty
        self.step3_score: float | None = None
        # Roadmap progress cache
        self.current_roadmap_step = 0
    
    def _get_db_connection(self):
        """Get database connection."""
        return sqlite3.connect('pedagogical_ai.db')
    
    def start_concept_session(self, topic: str, user_profile: UserProfile) -> str:
        """Start enhanced learning session with full user modeling."""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        try:
            self.session_start_time = time.time()
            
            # Get or create concept
            concept_id = topic.upper().replace(" ", "_")
            self.concept_id = concept_id
            
            cursor.execute('SELECT * FROM concepts WHERE concept_id = ?', (concept_id,))
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO concepts (concept_id, concept_name, category)
                    VALUES (?, ?, ?)
                ''', (concept_id, topic, 'unknown'))
            
            # Ensure user exists
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, name, level)
                VALUES (?, ?, ?)
            ''', (self.user_id, user_profile.name, user_profile.level))
            
            # Get current mastery level
            cursor.execute('''
                SELECT mastery_level FROM concept_mastery 
                WHERE user_id = ? AND concept_id = ?
            ''', (self.user_id, concept_id))
            result = cursor.fetchone()
            current_mastery = result[0] if result else 0.0
            
            # Create new session
            self.session_id = 'session_' + str(uuid.uuid4())[:8]
            cursor.execute('''
                INSERT INTO learning_sessions 
                (session_id, user_id, concept_id, mastery_before)
                VALUES (?, ?, ?, ?)
            ''', (self.session_id, self.user_id, concept_id, current_mastery))
            
            conn.commit()
            print(f"🔗 Enhanced Session: {self.session_id} for '{topic}' (current mastery: {current_mastery:.2f})")
            return self.session_id
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def _start_step(self, step_number: int, step_name: str) -> int:
        """Start step with enhanced tracking."""
        self.current_step_start_time = time.time()
        
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO step_interactions (session_id, step_number, step_name, start_time)
            VALUES (?, ?, ?, ?)
        ''', (self.session_id, step_number, step_name, datetime.now().isoformat()))
        
        self.current_interaction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return self.current_interaction_id
    
    def _end_step(self, step_number: int, success: bool = True, metadata: dict = None):
        """End step with enhanced tracking."""
        if self.current_step_start_time is None:
            return
            
        duration = int(time.time() - self.current_step_start_time)
        
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE step_interactions 
            SET end_time = ?, duration = ?, success = ?, metadata = ?
            WHERE interaction_id = ?
        ''', (
            datetime.now().isoformat(),
            duration,
            success,
            json.dumps(metadata) if metadata else None,
            self.current_interaction_id
        ))
        
        conn.commit()

        # --- Roadmap progress update ---
        try:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS roadmap_progress (
                    user_id TEXT,
                    concept_id TEXT,
                    step_completed INTEGER,
                    PRIMARY KEY (user_id, concept_id)
                )
            ''')
            # Update or insert progress
            conn.execute('''
                INSERT INTO roadmap_progress (user_id, concept_id, step_completed)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, concept_id) DO UPDATE SET step_completed = excluded.step_completed
            ''', (self.user_id, self.concept_id, step_number))
            conn.commit()
        except Exception:
            pass
        conn.close()
        
        print(f"📊 Step {step_number} completed in {duration}s")

    def run_step_1_analogy(self, topic: str, user_profile: UserProfile) -> Optional[str]:
        """Enhanced Step 1 with personalization tracking and regeneration support."""
        if not self.session_id:
            self.start_concept_session(topic, user_profile)
            
        interaction_id = self._start_step(1, "Real-Life Analogy")
        print_header(f"Step 1: Real-Life Analogy for '{topic}'")
        
        # Get user's learning history for personalization
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT concept_id FROM concept_mastery 
            WHERE user_id = ? AND mastery_level > 0.5
        ''', (self.user_id,))
        known_concepts = [row[0] for row in cursor.fetchall()]
        
        # Enhanced analogy generation with regeneration support
        personalization_context = {
            "user_level": user_profile.level,
            "previous_concepts": known_concepts
        }

        regeneration_count = 0
        used_analogies = []  # Track previously generated analogies
        final_analogy = None
        
        while True:
            # Generate analogy (initial or regenerated)
            if regeneration_count == 0:
                analogy = self._generate_initial_analogy(topic, personalization_context)
            else:
                analogy = self._generate_regenerated_analogy(topic, personalization_context, used_analogies)
            
            if not analogy:
                # Fallback simple analogy
                analogy = f"Think of {topic} like a coffee shop. One table lists drink orders, and another lists customers. An {topic} finds which customer belongs to which drink order, so you can call out 'Espresso for Alice!'"

            used_analogies.append(analogy)

            # Present analogy to user
            print("\n-- Agent's Explanation --\n")
            print(analogy)
            
            # Ask for understanding confirmation
            print("\n" + "="*50)
            print("💡 Do you understand this analogy?")
            print("1. Yes, I understand - let's continue")
            print("2. No, please explain it differently")
            print("="*50)
            
            reading_start = time.time()
            user_choice = get_user_input("Your choice (1 or 2): ").strip()
            reading_time = int(time.time() - reading_start)
            
            # Store this attempt
            self._save_step1_attempt(interaction_id, analogy, personalization_context, regeneration_count, user_choice == "1")
            
            if user_choice == "1":
                final_analogy = analogy
                print("\n✅ Great! Let's move to the next step.")
                break
            elif user_choice == "2":
                regeneration_count += 1
                if regeneration_count >= 3:  # Limit regenerations
                    print("\n📚 Let's continue with this explanation and you can ask questions later if needed.")
                    final_analogy = analogy
                    break
                else:
                    print(f"\n🔄 Generating a different explanation... (Attempt {regeneration_count + 1})")
            else:
                print("Please enter 1 or 2.")
                continue
        
        # Calculate final metrics
        expected_reading_time = len(final_analogy) * 0.05  # ~50ms per character
        if reading_time < expected_reading_time * 0.7:
            comprehension = "fast"
        elif reading_time > expected_reading_time * 1.5:
            comprehension = "slow"
        else:
            comprehension = "normal"
        
        conn.close()
        
        # Record step completion
        self._end_step(1, True, {
            "concept": topic,
            "final_analogy": final_analogy,
            "regeneration_count": regeneration_count,
            "reading_time": reading_time,
            "comprehension_speed": comprehension,
            "personalization_applied": True,
            "analogy_complexity": len(final_analogy.split())
        })
        
        return final_analogy

    def _generate_initial_analogy(self, topic: str, personalization_context: dict) -> str:
        """Generate the initial analogy for Step 1."""
        system_prompt = """You are a creative SQL tutor. Generate a concise, real-life analogy for an SQL concept, tailored to the user's level. 
        Use everyday situations that are relatable and easy to understand. Do not include any SQL code or technical jargon. 
        Make it engaging and memorable. Respond in English."""
        
        user_prompt = f"""Concept: {topic}
User Level: {personalization_context['user_level']}
Known Concepts: {json.dumps(personalization_context['previous_concepts'])}

Create a vivid, easy-to-understand analogy that explains how {topic} works:"""
        
        return self.ai_service.get_response(system_prompt, user_prompt)

    def _save_step1_attempt(self, interaction_id: int, analogy: str, personalization_context: dict, regeneration_count: int, user_understood: Optional[bool]):
        """Saves a single Step 1 analogy attempt to the database."""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        # Simplified reading time and comprehension for API version
        reading_time = 10 # Placeholder
        comprehension_indicator = "pending"

        cursor.execute('''
            INSERT INTO step1_analogies 
            (interaction_id, analogy_presented, reading_time, comprehension_indicator, 
             personalization_used, user_level, previous_concepts, regeneration_attempt, user_understood)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            interaction_id, analogy, reading_time, comprehension_indicator,
            json.dumps(personalization_context), personalization_context['user_level'],
            json.dumps(personalization_context['previous_concepts']), regeneration_count, user_understood
        ))
        conn.commit()
        conn.close()

    def _generate_regenerated_analogy(self, topic: str, personalization_context: dict, used_analogies: list) -> str:
        """Generate a different analogy when user doesn't understand the previous one."""
        system_prompt = """You are a creative SQL tutor. Your main goal is to generate a COMPLETELY NEW analogy because the user did not understand the previous ones.
        
You MUST follow these rules:
1.  Your new analogy MUST be on a different topic. For example, if the user saw a 'bakery' analogy, you could use 'library', 'space mission', 'gardening', etc.
2.  DO NOT repeat concepts or metaphors from the previous attempts.
3.  Be clear, concise, and do not include any technical jargon or SQL code. Respond in English."""
        
        previous_explanations = "\\n".join([f"- {analogy[:80]}..." for analogy in used_analogies])
        
        user_prompt = f"""The user needs a new analogy for the SQL concept: "{topic}".

They have already seen the following explanations and did not understand them:
{previous_explanations}

Please generate a fresh, completely different analogy that avoids the topics and ideas used above."""
        
        print(f"\\n[DEBUG] Prompt sent to AI for regeneration:\\n---\\n{user_prompt}\\n---\\n")
        
        return self.ai_service.get_response(system_prompt, user_prompt, temperature=0.8)

    def run_step_2_prediction(self, topic: str, step_1_context: str, user_profile: UserProfile) -> None:
        """Enhanced Step 2 with dynamic GPT-generated content and retry mechanism."""
        interaction_id = self._start_step(2, "Predict the Output")
        print_header(f"Step 2: Predict the Output for '{topic}'")
        
        # Generate dynamic question using GPT
        question_data = self._generate_step2_question(topic, step_1_context)
        if not question_data:
            print("Error generating question. Using fallback.")
            question_data = self._get_fallback_question(topic)
        
        # Display question
        self._display_step2_question(question_data)
        
        # Handle answer attempts with retry logic
        result = self._handle_step2_answer_attempts(interaction_id, question_data, topic)
        
        # Store detailed Step 2 data
        self._save_step2_session(interaction_id, question_data, result)
        
        self._end_step(2, result['success'], {
            "prediction_accuracy": result['final_correct'],
            "attempts_made": result['attempts'],
            "questions_attempted": result['questions_tried'],
            "total_response_time": result['total_time']
        })

    def _generate_step2_question(self, topic: str, step_1_context: str) -> Optional[Dict]:
        """Generate a dynamic Step 2 question using GPT."""
        system_prompt = """You are an expert SQL educator creating prediction questions for students learning SQL JOINs.

Create a realistic scenario with two tables and a multiple-choice question about the output of a SQL query.

Your response must be valid JSON with this exact structure:
{
  "scenario": "Brief description of the business context",
  "tables": {
    "table1_name": [
      {"column1": "value1", "column2": "value2"},
      {"column1": "value3", "column2": "value4"}
    ],
    "table2_name": [
      {"column1": "valueA", "column2": "valueB"},
      {"column1": "valueC", "column2": "valueD"}
    ]
  },
  "query": "SELECT ... FROM table1 [JOIN_TYPE] table2 ON ...",
  "options": {
    "correct": "The actual correct answer result",
    "wrong1": "First incorrect option", 
    "wrong2": "Second incorrect option",
    "wrong3": "Third incorrect option"
  },
  "correct": "correct"
}

Requirements:
- Use realistic business scenarios (e-commerce, library, restaurant, etc.)
- Create 3-4 rows per table with some matching and non-matching data
- Make the JOIN condition clear and logical
- Create 4 distinct multiple choice options
- Include one obviously wrong option, one tricky option, and one correct option
- Make sure only one option is completely correct
- Put the correct answer in the "correct" key and wrong answers in "wrong1", "wrong2", "wrong3"
- Set the "correct" field to "correct" (will be randomized later)"""

        user_prompt = f"""Create a prediction question for the SQL concept: {topic}

Context from Step 1: {step_1_context}

Make the question appropriately challenging but fair for students learning {topic}. 
The query should demonstrate the key behavior of {topic} clearly.

Return only valid JSON, no additional text."""

        try:
            response = self.ai_service.get_response(system_prompt, user_prompt)
            if response:
                question_data = json.loads(response)
                # Randomize the options after generation
                return self._randomize_mcq_options(question_data)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error generating question: {e}")
            return None

    def _randomize_mcq_options(self, question_data: Dict) -> Dict:
        """Randomize the positions of multiple choice options."""
        # Get the options
        options = question_data.get('options', {})
        
        # Extract correct and wrong answers
        correct_answer = options.get('correct', '')
        wrong_answers = [
            options.get('wrong1', ''),
            options.get('wrong2', ''),
            options.get('wrong3', '')
        ]
        
        # Create a list of all options
        all_options = [correct_answer] + wrong_answers
        
        # Shuffle them randomly
        random.shuffle(all_options)
        
        # Assign to A, B, C, D
        option_keys = ['A', 'B', 'C', 'D']
        randomized_options = {}
        correct_key = None
        
        for i, option in enumerate(all_options):
            key = option_keys[i]
            randomized_options[key] = option
            if option == correct_answer:
                correct_key = key
        
        # Update the question data
        question_data['options'] = randomized_options
        question_data['correct'] = correct_key
        
        return question_data

    def _get_fallback_question(self, topic: str) -> Dict:
        """Fallback question if GPT generation fails."""
        fallback_data = {
            "scenario": "E-commerce Order System",
            "tables": {
                "Orders": [
                    {"order_id": 1, "item": "Laptop", "customer_id": 101},
                    {"order_id": 2, "item": "Mouse", "customer_id": 102},
                    {"order_id": 3, "item": "Keyboard", "customer_id": 103}
                ],
                "Customers": [
                    {"customer_id": 101, "name": "Alice", "city": "New York"},
                    {"customer_id": 102, "name": "Bob", "city": "Boston"},
                    {"customer_id": 105, "name": "Charlie", "city": "Chicago"}
                ]
            },
            "query": f"SELECT item, name FROM Orders {topic} Customers ON Orders.customer_id = Customers.customer_id",
            "options": {
                "correct": "Laptop-Alice, Mouse-Bob",
                "wrong1": "Laptop-Alice, Mouse-Bob, Keyboard-NULL",
                "wrong2": "All items with customer names",
                "wrong3": "Laptop-Alice, Mouse-Bob, Keyboard-Unknown, NoOrder-Charlie"
            },
            "correct": "correct"
        }
        
        # Randomize the options
        return self._randomize_mcq_options(fallback_data)

    def _display_step2_question(self, question_data: Dict) -> None:
        """Display the Step 2 question to the user."""
        print(f"\n-- Scenario: {question_data['scenario']} --\n")
        
        for table_name, rows in question_data['tables'].items():
            print(f"{table_name} Table:")
            for row in rows:
                print(f"  {row}")
            print()
        
        print(f"Query: {question_data['query']}")
        print("\nWhat will be the output?")
        for key, value in question_data['options'].items():
            print(f"  {key}. {value}")

    def _handle_step2_answer_attempts(self, interaction_id: int, question_data: Dict, topic: str) -> Dict:
        """Handle answer attempts with retry logic."""
        attempts = 0
        questions_tried = 1
        start_time = time.time()
        
        while attempts < 3:
            attempts += 1
            print(f"\n--- Attempt {attempts} ---")
            
            # Get user answer
            user_answer = get_user_input("Your prediction (A/B/C/D): ").upper()
            while user_answer not in ['A', 'B', 'C', 'D']:
                user_answer = get_user_input("Please enter A, B, C, or D: ").upper()
            
            # Check if correct
            correct_answer = question_data['correct']
            is_correct = user_answer == correct_answer
            
            # Save attempt
            self._save_step2_attempt(interaction_id, attempts, user_answer, correct_answer, is_correct)
            
            if is_correct:
                # Correct answer - provide explanation and finish
                feedback = self._generate_step2_feedback(question_data, user_answer, correct_answer, "correct")
                print(f"\n✅ {feedback}")
                return {
                    'success': True,
                    'final_correct': True,
                    'attempts': attempts,
                    'questions_tried': questions_tried,
                    'total_time': int(time.time() - start_time)
                }
            else:
                # Wrong answer - handle based on attempt number
                if attempts == 1:
                    print(f"\n❌ That's not correct. Please try again.")
                elif attempts == 2:
                    # Give hint
                    hint = self._generate_step2_feedback(question_data, user_answer, correct_answer, "hint")
                    print(f"\n❌ Still not correct. Here's a hint: {hint}")
                else:
                    # Final attempt - give answer and option to try new question
                    feedback = self._generate_step2_feedback(question_data, user_answer, correct_answer, "final")
                    print(f"\n❌ {feedback}")
                    print(f"The correct answer is {correct_answer}.")
                    
                    # Ask if they want to try a new question
                    try_new = get_user_input("Would you like to try a new question? (y/n): ").lower() == 'y'
                    if try_new:
                        print("\n🔄 Generating a new question...")
                        new_question = self._generate_step2_question(topic, "")
                        if new_question:
                            questions_tried += 1
                            attempts = 0  # Reset attempts for new question
                            question_data = new_question
                            self._display_step2_question(question_data)
                            continue
                    
                    return {
                        'success': True,  # Flat rate scoring
                        'final_correct': False,
                        'attempts': attempts,
                        'questions_tried': questions_tried,
                        'total_time': int(time.time() - start_time)
                    }
        
        # Should never reach here, but just in case
        return {
            'success': False,
            'final_correct': False,
            'attempts': attempts,
            'questions_tried': questions_tried,
            'total_time': int(time.time() - start_time)
        }

    def _generate_step2_feedback(self, question_data: Dict, user_answer: str, correct_answer: str, feedback_type: str) -> str:
        """Generate feedback using GPT based on the question and user's answer."""
        system_prompt = """You are an expert SQL tutor providing feedback on student predictions.

Your feedback should be:
- Clear and educational
- Specific to the question and answer given
- Encouraging but honest
- Focused on the learning objective

For different feedback types:
- "correct": Explain WHY the answer is correct and what concept it demonstrates
- "hint": Give a helpful hint without revealing the answer directly
- "final": Explain what went wrong and provide a clear explanation of the correct answer"""

        user_prompt = f"""Question scenario: {question_data['scenario']}
Query: {question_data['query']}
Correct answer: {correct_answer} - {question_data['options'][correct_answer]}
Student's answer: {user_answer} - {question_data['options'].get(user_answer, 'Invalid')}

Feedback type: {feedback_type}

Provide appropriate feedback for this student's answer."""

        try:
            response = self.ai_service.get_response(system_prompt, user_prompt)
            return response or "Please review the query and table data carefully."
        except Exception as e:
            if feedback_type == "correct":
                return "Great job! You correctly understood how the JOIN works."
            elif feedback_type == "hint":
                return "Look carefully at which rows have matching values in both tables."
            else:
                return "Think about which rows meet the JOIN condition in both tables."

    def _save_step2_attempt(self, interaction_id: int, attempt_number: int, user_answer: str, correct_answer: str, is_correct: bool) -> None:
        """Save a single Step 2 attempt."""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO step2_attempts 
            (interaction_id, attempt_number, user_answer, correct_answer, is_correct, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            interaction_id, attempt_number, user_answer, correct_answer, is_correct, datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()

    def _save_step2_session(self, interaction_id: int, question_data: Dict, result: Dict) -> None:
        """Save the complete Step 2 session data."""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO step2_sessions 
            (interaction_id, question_data, total_attempts, questions_tried, final_success, total_time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            interaction_id, json.dumps(question_data), result['attempts'], 
            result['questions_tried'], result['final_correct'], result['total_time']
        ))
        
        conn.commit()
        conn.close()

    def run_step_3_writing_task(self, topic: str, step_1_context: str, user_profile: UserProfile) -> UserProfile:
        """Enhanced Step 3 with detailed query attempt tracking."""
        interaction_id = self._start_step(3, "Write Your Own Query")
        print_header(f"Step 3: Write Your Own '{topic}' Query")
        
        # Reset attempt tracking
        self.step3_attempts = []
        
        # Provide task context
        print("\n-- Your Challenge --")
        print("Database: Online Bookstore")
        print("Tables available:")
        print("  Books (book_id, title, author_id, price)")
        print("  Authors (author_id, name, country)")
        print(f"\nWrite a {topic} query to find books with their author names.")
        
        attempt_number = 0
        query_writing_start = time.time()
        
        while True:
            attempt_number += 1
            print(f"\n--- Attempt {attempt_number} ---")
            
            # Track query writing with timing
            attempt_start = time.time()
            print("Write your SQL query (type 'DONE' when finished):")
            
            query_lines = []
            while True:
                line = get_user_input("> ")
                if line.upper() == 'DONE':
                    break
                query_lines.append(line)
            
            query_text = "\n".join(query_lines)
            attempt_time = time.time() - attempt_start
            
            # Analyze query
            analysis = self._analyze_query(query_text, topic)
            
            # Store attempt
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO query_attempts 
                (interaction_id, attempt_number, query_text, syntax_valid, error_type, 
                 error_message, time_since_start, char_count, word_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                interaction_id, attempt_number, query_text, analysis['syntax_valid'],
                analysis.get('error_type'), analysis.get('error_message'),
                int(time.time() - query_writing_start), len(query_text), len(query_text.split())
            ))
            
            conn.commit()
            conn.close()
            
            # Store in memory for session analysis
            self.step3_attempts.append({
                "attempt": attempt_number,
                "query": query_text,
                "analysis": analysis,
                "time": attempt_time
            })
            
            # Provide feedback
            if analysis['syntax_valid'] and analysis['has_target_concept']:
                print("✅ Great! Your query looks correct.")
                break
            else:
                print("🔧 Let's improve this query:")
                if not analysis['syntax_valid']:
                    print(f"   - Syntax issue: {analysis.get('error_message', 'Check SQL syntax')}")
                if not analysis['has_target_concept']:
                    print(f"   - Missing: Make sure to use {topic}")
                
                retry = get_user_input("Try again? (y/n): ").lower()
                if retry != 'y':
                    break
        
        # Get explanation
        print("\nNow explain your query (type 'DONE' when finished):")
        explanation_lines = []
        explanation_start = time.time()
        
        while True:
            line = get_user_input("> ")
            if line.upper() == 'DONE':
                break
            explanation_lines.append(line)
        
        explanation_text = "\n".join(explanation_lines)
        explanation_time = time.time() - explanation_start
        
        # Analyze explanation
        explanation_analysis = self._analyze_explanation(explanation_text, topic)
        
        # Store explanation
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO step3_explanations 
            (interaction_id, explanation_text, word_count, concepts_mentioned,
             clarity_score, accuracy_score, writing_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            interaction_id, explanation_text, len(explanation_text.split()),
            json.dumps(explanation_analysis['concepts_mentioned']),
            explanation_analysis['clarity_score'], explanation_analysis['accuracy_score'],
            int(explanation_time)
        ))
        
        conn.commit()
        conn.close()
        
        # Update user profile and mastery
        if analysis['syntax_valid'] and analysis['has_target_concept']:
            user_profile.add_learned_concept(topic)
            self._update_concept_mastery(topic, True, len(self.step3_attempts))
            print(f"\n🎉 Congratulations! You've successfully mastered {topic} basics.")
        else:
            self._update_concept_mastery(topic, False, len(self.step3_attempts))
            print(f"\n📚 Keep practicing {topic}. You're making progress!")
        
        # Calculate behavioral metrics
        behavioral_metrics = self._calculate_step3_behavioral_metrics()
        
        # Add deletion/rewrite count (number of extra attempts beyond the first)
        behavioral_metrics["deletion_count"] = max(0, len(self.step3_attempts) - 1)
        
        self._end_step(3, analysis['syntax_valid'], {
            "total_attempts": len(self.step3_attempts),
            "final_success": analysis['syntax_valid'] and analysis['has_target_concept']
        })
        
        # -------------------------------------------------------------
        # New 100-point scoring rubric
        # -------------------------------------------------------------
        total_time_sec = behavioral_metrics.get("total_time", 999)

        # Time Efficiency (30 pts)
        if total_time_sec < 60:
            time_points = 30
        elif total_time_sec < 120:
            time_points = 25
        elif total_time_sec < 180:
            time_points = 20
        elif total_time_sec < 300:
            time_points = 10
        else:
            time_points = 5

        # Hint usage (20 pts) – still placeholder 0 hints
        hints_used = 0  # integrate actual hint tracking later
        if hints_used == 0:
            hint_points = 20
        elif hints_used == 1:
            hint_points = 15
        elif hints_used == 2:
            hint_points = 10
        else:
            hint_points = 5

        # Query Evaluation via GPT (50 pts)
        evaluation_level = self._evaluate_query_quality(query_text, explanation_text, topic)
        eval_mapping = {
            "Excellent": 50,
            "Good": 35,
            "Fair": 20,
            "Poor": 10,
            "Failed": 0,
        }
        eval_points = eval_mapping.get(evaluation_level, 0)

        self.step3_score = time_points + hint_points + eval_points
        print(f"\n🧮 Step 3 Score (new rubric): {self.step3_score} / 100  (Eval: {evaluation_level}, Time: {time_points}, Hints: {hint_points})")

        # If evaluation is lower than "Good", force retry of Step 3
        if evaluation_level not in ("Good", "Excellent"):
            print("\n🔁 The evaluation is only '" + evaluation_level + "'. Let's refine your query and try Step 3 again!\n")
            return self.run_step_3_writing_task(topic, step_1_context, user_profile)

        return user_profile

    def _analyze_query(self, query_text: str, target_concept: str) -> Dict:
        """Analyze SQL query for syntax and concept usage."""
        analysis = {
            "syntax_valid": True,
            "has_target_concept": target_concept.upper() in query_text.upper(),
            "error_type": None,
            "error_message": None
        }
        
        # Basic syntax checks
        if not query_text.strip():
            analysis["syntax_valid"] = False
            analysis["error_type"] = "EMPTY_QUERY"
            analysis["error_message"] = "Query is empty"
        elif not query_text.upper().startswith("SELECT"):
            analysis["syntax_valid"] = False
            analysis["error_type"] = "MISSING_SELECT"
            analysis["error_message"] = "Query should start with SELECT"
        elif "FROM" not in query_text.upper():
            analysis["syntax_valid"] = False
            analysis["error_type"] = "MISSING_FROM"
            analysis["error_message"] = "Query should include FROM clause"
        
        return analysis
    
    def _analyze_explanation(self, explanation_text: str, target_concept: str) -> Dict:
        """Analyze explanation quality."""
        words = explanation_text.split()
        concepts_mentioned = []
        
        # Look for SQL concepts
        sql_concepts = ["JOIN", "SELECT", "FROM", "WHERE", "ON", "TABLE"]
        for concept in sql_concepts:
            if concept.lower() in explanation_text.lower():
                concepts_mentioned.append(concept)
        
        # Score clarity (simplified)
        clarity_score = min(1.0, len(words) / 20)  # 20 words = full clarity
        
        # Score accuracy (simplified)
        accuracy_score = 0.8 if target_concept.upper() in explanation_text.upper() else 0.3
        
        return {
            "concepts_mentioned": concepts_mentioned,
            "clarity_score": clarity_score,
            "accuracy_score": accuracy_score
        }
    
    def _calculate_step3_behavioral_metrics(self) -> Dict:
        """Calculate behavioral learning metrics for Step 3."""
        if not self.step3_attempts:
            return {}
        
        # Calculate metrics
        total_time = sum(attempt.get("time", 0) for attempt in self.step3_attempts)
        progression = "PROGRESSIVE" if len(self.step3_attempts) <= 3 else "STRUGGLING"
        
        return {
            "total_time": total_time,
            "number_of_attempts": len(self.step3_attempts),
            "query_evolution": progression,
            "average_attempt_time": total_time / len(self.step3_attempts),
            # deletion_count will be added by caller
        }
    
    def _analyze_query_evolution(self) -> str:
        """Analyze how queries evolved over attempts."""
        if len(self.step3_attempts) <= 1:
            return "SINGLE_ATTEMPT"
        elif len(self.step3_attempts) <= 3:
            return "PROGRESSIVE"
        else:
            return "EXPLORATORY"
    
    def _update_concept_mastery(self, concept: str, success: bool, attempts: int):
        """Update concept mastery based on performance."""
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        concept_id = concept.upper().replace(" ", "_")
        
        # Get current mastery
        cursor.execute('''
            SELECT mastery_level, total_attempts, successful_attempts
            FROM concept_mastery WHERE user_id = ? AND concept_id = ?
        ''', (self.user_id, concept_id))
        
        result = cursor.fetchone()
        if result:
            current_mastery, total_attempts, successful_attempts = result
            new_total = total_attempts + 1
            new_successful = successful_attempts + (1 if success else 0)
        else:
            current_mastery = 0.0
            new_total = 1
            new_successful = 1 if success else 0
        
        # Calculate new mastery (simplified algorithm)
        base_score = new_successful / new_total
        attempt_penalty = max(0, (attempts - 1) * 0.1)  # Penalty for multiple attempts
        new_mastery = min(1.0, base_score - attempt_penalty)
        
        # Update or insert
        cursor.execute('''
            INSERT OR REPLACE INTO concept_mastery 
            (user_id, concept_id, mastery_level, total_attempts, successful_attempts, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.user_id, concept_id, new_mastery, new_total, new_successful, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        print(f"📊 Mastery Update: {concept} = {new_mastery:.2f} (was {current_mastery:.2f})")
    
    def run_step_4_challenge(self, user_profile: UserProfile) -> UserProfile:
        """Enhanced Step 4 with adaptive challenge selection."""
        interaction_id = self._start_step(4, "Adaptive Challenge")
        print_header("Step 4: Adaptive SQL Challenge")
        
        if not user_profile.learned_concepts:
            print("Complete Step 3 first to unlock challenges.")
            self._end_step(4, False, {"error": "No learned concepts"})
            return user_profile
        
        # Select challenge based on performance
        challenge_difficulty = self._select_adaptive_difficulty(user_profile)
        
        print(f"\n🎯 Challenge Level: {challenge_difficulty}")
        print("Combine multiple concepts in a real-world scenario:")
        print("\nDatabase: Company HR System")
        print("Tables: employees, departments, projects, assignments")
        print("Challenge: Write a query to find employees working on multiple projects")
        
        # ------------------------------------------------------
        # Record per-attempt solutions in step4_solution_attempts
        # ------------------------------------------------------

        conn = self._get_db_connection()
        cursor = conn.cursor()

        # Ensure attempts table exists (minimal on-the-fly schema)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS step4_solution_attempts (
                attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                interaction_id INTEGER,
                attempt_number INTEGER,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                solution_text TEXT,
                success_rate REAL,
                final_success BOOLEAN
            )
        ''')
        conn.commit()

        attempt_number = 0
        challenge_start = time.time()
        final_success = False

        while True:
            attempt_number += 1
            print(f"\n--- Attempt {attempt_number} (type 'DONE' on new line to finish query) ---")

            solution_lines = []
            while True:
                line = get_user_input("> ")
                if line.upper() == 'DONE':
                    break
                solution_lines.append(line)

            solution = "\n".join(solution_lines)

            # Analyze solution
            analysis = self._analyze_challenge_solution(solution, user_profile.learned_concepts)
            success_rate = analysis["success_rate"]
            attempt_success = success_rate > 0.7

            # Store attempt
            cursor.execute('''
                INSERT INTO step4_solution_attempts
                (interaction_id, attempt_number, solution_text, success_rate, final_success)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                interaction_id, attempt_number, solution, success_rate, attempt_success
            ))
            conn.commit()

            if attempt_success:
                print("🏆 Excellent solution! You've demonstrated concept mastery.")
                final_success = True
                break
            else:
                print("❌ Not quite correct yet. Success rate {:.0%}.".format(success_rate))
                retry = get_user_input("Try again? (y/n): ").lower()
                if retry != 'y':
                    break

        total_time = time.time() - challenge_start

        # ------------------------------------------------------
        # Step 4 Scoring (100-point rubric)
        # ------------------------------------------------------
        def _step4_score(correctness_pts: int, concept_pts: int, approach_pts: int, attempt_pts: int, bonus: int) -> int:
            return correctness_pts + concept_pts + approach_pts + attempt_pts + bonus

        # 1. Correctness (40)
        if success_rate == 1.0:
            correctness = 40
        elif success_rate >= 0.9:
            correctness = 30
        elif success_rate >= 0.5:
            correctness = 20
        elif success_rate > 0.0:
            correctness = 10
        else:
            correctness = 0

        # 2. Concept Integration (30)
        required_count = len(user_profile.learned_concepts)
        used_count = len(analysis["concepts_used"])
        missing = required_count - used_count
        if used_count == required_count and required_count > 0:
            concept_pts = 30
        elif missing == 1:
            concept_pts = 20
        elif missing >= 2:
            concept_pts = 10
        else:  # only current concept
            concept_pts = 5

        # 3. Approach (20)
        approach_map = {"systematic": 20, "simple": 15, "complex": 10, "partial": 5}
        approach_pts = approach_map.get(analysis.get("approach", "partial"), 5)

        # 4. Attempt count (10)
        if attempt_number == 1:
            attempt_pts = 10
        elif attempt_number == 2:
            attempt_pts = 7
        elif attempt_number == 3:
            attempt_pts = 5
        else:
            attempt_pts = 3

        # Difficulty bonuses
        bonus = 0
        if challenge_difficulty == "EASY" and final_success:
            bonus = 10  # No hints assumption
        if challenge_difficulty == "HARD" and analysis.get("approach") == "systematic" and final_success:
            bonus = 15

        step4_score = _step4_score(correctness, concept_pts, approach_pts, attempt_pts, bonus)
        print(f"\n🧮 Step 4 Score: {step4_score} / 100  (Correctness {correctness}, Concepts {concept_pts}, Approach {approach_pts}, Attempts {attempt_pts}, Bonus {bonus})")

        # Pass / Retry logic
        if step4_score < 60:
            if step4_score >= 40:
                print("\n🔁 Score below 60. Recommended to retry this challenge to reinforce concepts.")
            else:
                print("\n❗ Score below 40. You should review earlier concepts before attempting again.")
            retry_ch = get_user_input("Retry Step 4 now? (y/n): ").lower()
            if retry_ch == 'y':
                return self.run_step_4_challenge(user_profile)  # recursive retry

        # else pass and continue

        # Store overall challenge summary
        cursor.execute('''
            INSERT INTO step4_challenges 
            (interaction_id, problem_difficulty, concepts_tested, final_success, total_solving_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            interaction_id, challenge_difficulty, json.dumps(user_profile.learned_concepts),
            final_success, int(total_time)
        ))

        conn.commit()
        conn.close()
         
        self._end_step(4, final_success, {
            "challenge_difficulty": challenge_difficulty,
            "final_success": final_success,
            "total_time": int(total_time)
        })
        
        return user_profile
    
    def _select_adaptive_difficulty(self, user_profile: UserProfile) -> str:
        """Select challenge difficulty using new 100-point rubric."""
        if self.step3_score is not None:
            if self.step3_score >= 80:
                return "HARD"
            elif self.step3_score >= 50:
                return "MEDIUM"
            else:
                return "EASY"

        # Fallback to concept mastery average (original logic)
        conn = self._get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT AVG(mastery_level) FROM concept_mastery WHERE user_id = ?
        ''', (self.user_id,))
        result = cursor.fetchone()
        avg_mastery = result[0] if result and result[0] else 0.0

        conn.close()

        if avg_mastery > 0.8:
            return "HARD"
        elif avg_mastery > 0.6:
            return "MEDIUM"
        else:
            return "EASY"
    
    def _analyze_challenge_solution(self, solution: str, learned_concepts: List[str]) -> Dict:
        """Analyze challenge solution quality."""
        concepts_used = []
        for concept in learned_concepts:
            if concept.upper() in solution.upper():
                concepts_used.append(concept)
        
        success_rate = len(concepts_used) / max(1, len(learned_concepts))
        
        return {
            "concepts_used": concepts_used,
            "success_rate": success_rate,
            "solution_length": len(solution),
            "approach": "systematic" if len(solution) > 50 else "simple"
        }
    
    def end_session(self, user_profile: UserProfile):
        """End session with comprehensive analytics."""
        if not self.session_id:
            return
        
        session_end_time = time.time()
        total_session_time = int(session_end_time - self.session_start_time)
        
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        # Calculate session metrics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_steps,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_steps,
                SUM(duration) as total_duration
            FROM step_interactions 
            WHERE session_id = ?
        ''', (self.session_id,))
        
        metrics = cursor.fetchone()
        
        # Calculate learning efficiency
        concepts_attempted = [self.concept_id] if self.concept_id else []
        learning_efficiency = metrics[1] / metrics[0] if metrics[0] > 0 else 0
        
        # Update session
        cursor.execute('''
            UPDATE learning_sessions 
            SET session_end = ?, total_duration = ?, completed = TRUE
            WHERE session_id = ?
        ''', (datetime.now().isoformat(), total_session_time, self.session_id))
        
        # Store learning analytics
        cursor.execute('''
            INSERT INTO learning_analytics 
            (user_id, session_id, concepts_attempted, learning_efficiency, engagement_score)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            self.user_id, self.session_id, json.dumps(concepts_attempted),
            learning_efficiency, 0.85  # Simplified engagement score
        ))
        
        conn.commit()
        conn.close()
        
        # Display session summary
        print(f"\n📈 Enhanced Session Summary:")
        print(f"   📚 Concept: {self.concept_id}")
        print(f"   ⏱️  Total Time: {total_session_time//60}m {total_session_time%60}s")
        print(f"   🎯 Steps Completed: {metrics[0]}")
        print(f"   💾 All data saved for future personalization!")

    def _evaluate_query_quality(self, query_text: str, explanation_text: str, concept: str) -> str:
        """Call GPT to classify query quality (Excellent/Good/Fair/Poor/Failed)."""
        system_prompt = (
            "You are an AI SQL tutor. Based on student's SQL query and short explanation, "
            "classify overall quality into one of five levels: Excellent, Good, Fair, Poor, Failed.\n\n"
            "Definitions:\n"
            "Excellent: Correct, efficient, well-structured.\n"
            "Good: Correct but could be optimized or minor style issues.\n"
            "Fair: Mostly correct but has minor logical or style errors.\n"
            "Poor: Major errors but shows some understanding.\n"
            "Failed: Completely incorrect or off-topic.\n\n"
            "Output MUST be valid JSON of the form {\"evaluation_level\": \"...\"} and the response must be in English."
        )
        user_prompt = (
            f"Concept: {concept}\n\nSQL Query:\n{query_text}\n\nExplanation:\n{explanation_text}\n"
            "Return only the JSON object."
        )
        resp = self.ai_service.get_response(system_prompt, user_prompt, json_mode=True)
        data = self.ai_service.parse_json_response(resp) if resp else None
        if data and isinstance(data, dict) and data.get("evaluation_level"):
            return data["evaluation_level"].title()
        # Fallback simple logic
        return "Excellent" if "SELECT" in query_text.upper() and concept.upper() in query_text.upper() else "Failed" 