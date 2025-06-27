"""
Database-integrated teaching controller for managing the 4-step instructional flow.
"""

import json
import time
from typing import Optional
from services.ai_service import AIService
from services.grading_service import GradingService
from models.user_profile import UserProfile
from utils.io_helpers import get_user_input, print_header

# Import our basic database functionality
import sqlite3
from datetime import datetime
import uuid


class DBTeachingController:
    """Controller with integrated database tracking."""
    
    def __init__(self, user_id: str = "default_user"):
        self.ai_service = AIService()
        self.grading_service = GradingService()
        self.user_id = user_id
        self.session_id = None
        self.current_step_start_time = None
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables."""
        conn = sqlite3.connect('pedagogical_ai.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                level TEXT DEFAULT 'Beginner',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                concept_name TEXT,
                session_start TEXT DEFAULT CURRENT_TIMESTAMP,
                session_end TEXT,
                mastery_before REAL DEFAULT 0.0,
                mastery_after REAL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS step_interactions (
                interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                step_number INTEGER,
                step_name TEXT,
                start_time TEXT,
                end_time TEXT,
                duration INTEGER,
                success BOOLEAN,
                metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES learning_sessions (session_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def start_concept_session(self, topic: str, user_profile: UserProfile) -> str:
        """Start a new learning session and return session_id."""
        conn = sqlite3.connect('pedagogical_ai.db')
        cursor = conn.cursor()
        
        try:
            # Ensure user exists
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, name, level)
                VALUES (?, ?, ?)
            ''', (self.user_id, user_profile.name, user_profile.level))
            
            # Create new session
            self.session_id = 'session_' + str(uuid.uuid4())[:8]
            cursor.execute('''
                INSERT INTO learning_sessions (session_id, user_id, concept_name, mastery_before)
                VALUES (?, ?, ?, ?)
            ''', (self.session_id, self.user_id, topic, 0.0))  # TODO: Get actual mastery
            
            conn.commit()
            print(f"🔗 Database: Started session {self.session_id} for concept '{topic}'")
            return self.session_id
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def _start_step(self, step_number: int, step_name: str):
        """Record the start of a step."""
        self.current_step_start_time = time.time()
        
        conn = sqlite3.connect('pedagogical_ai.db')
        cursor = conn.cursor()
        
        # First, add the step_name column if it doesn't exist
        try:
            cursor.execute('ALTER TABLE step_interactions ADD COLUMN step_name TEXT')
            conn.commit()
        except sqlite3.OperationalError:
            # Column already exists, continue
            pass
        
        cursor.execute('''
            INSERT INTO step_interactions (session_id, step_number, step_name, start_time)
            VALUES (?, ?, ?, ?)
        ''', (self.session_id, step_number, step_name, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def _end_step(self, step_number: int, success: bool = True, metadata: dict = None):
        """Record the completion of a step."""
        if self.current_step_start_time is None:
            return
            
        duration = int(time.time() - self.current_step_start_time)
        
        conn = sqlite3.connect('pedagogical_ai.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE step_interactions 
            SET end_time = ?, duration = ?, success = ?, metadata = ?
            WHERE session_id = ? AND step_number = ? AND end_time IS NULL
        ''', (
            datetime.now().isoformat(),
            duration,
            success,
            json.dumps(metadata) if metadata else None,
            self.session_id,
            step_number
        ))
        
        conn.commit()
        conn.close()
        
        print(f"📊 Database: Step {step_number} completed in {duration}s")

    def run_step_1_analogy(self, topic: str, user_profile: UserProfile) -> Optional[str]:
        """Step 1 with database tracking."""
        if not self.session_id:
            self.start_concept_session(topic, user_profile)
            
        self._start_step(1, "Real-Life Analogy")
        print_header(f"Step 1: Real-Life Analogy for '{topic}'")
        
        # Simplified analogy for demo (you can use the full AI service)
        response = f"Think of {topic} like matching puzzle pieces. Each piece (table row) needs to find its perfect match in another puzzle (table) using a common pattern (join condition). Only pieces that have matching partners will appear in the final picture!"
        
        print("\n-- Agent's Explanation --\n")
        print(response)
        
        # Record step completion
        self._end_step(1, True, {
            "concept": topic,
            "user_level": user_profile.level,
            "analogy_length": len(response),
            "personalization_used": True
        })
        
        return response

    def run_step_2_prediction(self, topic: str, step_1_context: str, user_profile: UserProfile) -> None:
        """Step 2 with database tracking."""
        self._start_step(2, "Predict the Output")
        print_header(f"Step 2: Predict the Output for '{topic}'")
        
        # Simplified prediction question
        print("Sample Tables:")
        print("Orders: {id: 1, item: 'Pizza'}, {id: 2, item: 'Burger'}, {id: 3, item: 'Salad'}")
        print("Customers: {id: 1, name: 'Alice'}, {id: 2, name: 'Bob'}, {id: 4, name: 'Charlie'}")
        print(f"\nQuery: SELECT item, name FROM Orders {topic} Customers ON Orders.id = Customers.id")
        print("\nPredict the output:")
        print("A. Pizza-Alice, Burger-Bob, Salad-NULL")
        print("B. Pizza-Alice, Burger-Bob")
        print("C. All items with customer names")
        print("D. Pizza-Alice, Burger-Bob, Salad-NoMatch, NoOrder-Charlie")
        
        # Track response time
        start_answer_time = time.time()
        user_answer = get_user_input("\nYour prediction (A/B/C/D): ").upper()
        answer_time = time.time() - start_answer_time
        
        # Simple feedback
        correct_answer = "B"
        is_correct = user_answer == correct_answer
        
        if is_correct:
            print(f"\n✅ Correct! {topic} only returns rows where both tables have matching values.")
        else:
            print(f"\n❌ Not quite. The correct answer was {correct_answer}.")
            print(f"{topic} only includes rows where the join condition is met in BOTH tables.")
        
        # Record step completion with detailed metadata
        self._end_step(2, True, {
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "answer_time": round(answer_time, 2),
            "question_type": "multiple_choice_prediction",
            "concept": topic
        })

    def run_step_3_writing_task(self, topic: str, step_1_context: str, user_profile: UserProfile) -> UserProfile:
        """Step 3 with database tracking."""
        self._start_step(3, "Write Your Own Query")
        print_header(f"Step 3: Write Your Own '{topic}' Query")

        # Generate task (simplified for demo)
        print(f"\n-- Your Task --")
        print(f"Write a SQL query using {topic} to solve a real-world problem.")
        print("Think about what business question you want to answer.")

        # Get user submission
        print("\nPlease write your SQL query below. Type 'DONE' on a new line when finished.")
        user_query_lines = []
        query_start_time = time.time()
        
        while True:
            line = get_user_input("> ")
            if line.upper() == 'DONE':
                break
            user_query_lines.append(line)
        user_query = "\n".join(user_query_lines)
        query_time = time.time() - query_start_time

        print("\nNow, briefly explain what your query does. Type 'DONE' on a new line when finished.")
        user_explanation_lines = []
        explanation_start_time = time.time()
        
        while True:
            line = get_user_input("> ")
            if line.upper() == 'DONE':
                break
            user_explanation_lines.append(line)
        user_explanation = "\n".join(user_explanation_lines)
        explanation_time = time.time() - explanation_start_time

        # Simplified grading (you can use the full grading service)
        has_concept = topic.lower() in user_query.lower()
        query_length = len(user_query.strip())
        explanation_length = len(user_explanation.strip())
        
        success = has_concept and query_length > 10 and explanation_length > 10

        # Update user profile
        if success:
            user_profile.add_learned_concept(topic)
            print(f"\n✅ Great work! You've successfully used {topic} in your query.")
        else:
            print(f"\n📝 Keep practicing! Try to include {topic} in your query.")

        # Record step completion with detailed metadata
        self._end_step(3, success, {
            "query_text": user_query,
            "explanation_text": user_explanation,
            "query_length": query_length,
            "explanation_length": explanation_length,
            "has_target_concept": has_concept,
            "query_writing_time": round(query_time, 2),
            "explanation_writing_time": round(explanation_time, 2),
            "concept": topic,
            "attempt_count": 1  # Could track multiple attempts
        })
            
        return user_profile

    def run_step_4_challenge(self, user_profile: UserProfile) -> UserProfile:
        """Step 4 with database tracking."""
        self._start_step(4, "LeetCode-Style Challenge")
        print_header("Step 4: LeetCode-Style Challenge")
        
        if not user_profile.learned_concepts:
            print("No concepts learned yet to generate a challenge.")
            self._end_step(4, False, {"error": "No learned concepts"})
            return user_profile

        # Simplified challenge generation
        concepts_str = ", ".join(user_profile.learned_concepts)
        print(f"\nChallenge: Create a query that combines multiple concepts you've learned: {concepts_str}")
        print("This is your chance to show mastery by building a more complex query.")

        # Get user solution
        print("\nWrite your challenge solution below. Type 'DONE' when finished.")
        solution_lines = []
        solution_start_time = time.time()
        
        while True:
            line = get_user_input("> ")
            if line.upper() == 'DONE':
                break
            solution_lines.append(line)
        solution = "\n".join(solution_lines)
        solution_time = time.time() - solution_start_time

        # Simplified evaluation
        concepts_used = [concept for concept in user_profile.learned_concepts 
                        if concept.lower() in solution.lower()]
        success = len(concepts_used) > 0 and len(solution.strip()) > 20

        if success:
            print(f"\n🏆 Excellent! You used: {', '.join(concepts_used)}")
            # Could update mastery levels here
        else:
            print(f"\n📚 Good attempt! Try incorporating more of the concepts you've learned.")

        # Record step completion
        self._end_step(4, success, {
            "solution_text": solution,
            "solution_length": len(solution),
            "concepts_attempted": user_profile.learned_concepts,
            "concepts_used": concepts_used,
            "solution_time": round(solution_time, 2),
            "challenge_type": "integration"
        })

        return user_profile
    
    def end_session(self, user_profile: UserProfile):
        """End the learning session and calculate final metrics."""
        if not self.session_id:
            return
            
        conn = sqlite3.connect('pedagogical_ai.db')
        cursor = conn.cursor()
        
        # Calculate session metrics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_steps,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_steps,
                SUM(duration) as total_duration,
                AVG(duration) as avg_step_duration
            FROM step_interactions 
            WHERE session_id = ?
        ''', (self.session_id,))
        
        metrics = cursor.fetchone()
        
        # Update session end
        cursor.execute('''
            UPDATE learning_sessions 
            SET session_end = ?, mastery_after = ?
            WHERE session_id = ?
        ''', (datetime.now().isoformat(), 0.8, self.session_id))  # TODO: Calculate actual mastery
        
        conn.commit()
        conn.close()
        
        print(f"\n📈 Session Summary:")
        print(f"   Steps completed: {metrics[0]}")
        print(f"   Success rate: {metrics[1]}/{metrics[0]} ({100*metrics[1]/metrics[0]:.1f}%)")
        print(f"   Total time: {metrics[2]}s ({metrics[2]//60}m {metrics[2]%60}s)")
        print(f"   Average step time: {metrics[3]:.1f}s") 