"""
Enhanced teaching controller with comprehensive data tracking and user modeling.
"""

import json
import time
import re
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
        """Enhanced Step 1 with personalization tracking."""
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
        
        # Enhanced analogy generation (simplified for demo)
        personalization_context = {
            "user_level": user_profile.level,
            "previous_concepts": known_concepts
        }

        system_prompt = "You are a creative SQL tutor. Generate a concise, real-life analogy for an SQL concept, tailored to the user's level. Do not include any SQL code or technical jargon. Respond in English."
        user_prompt = f"Concept: {topic}\nUser Level: {user_profile.level}\nKnown Concepts: {json.dumps(known_concepts)}\n\nAnalogy:"
        
        analogy = self.ai_service.get_response(system_prompt, user_prompt)
        
        if not analogy:
             # Fallback simple analogy
            analogy = f"Think of {topic} like a coffee shop. One table lists drink orders, and another lists customers. An {topic} finds which customer belongs to which drink order, so you can call out 'Espresso for Alice!'"

        # Track reading time
        print("\n-- Agent's Explanation --\n")
        print(analogy)
        
        reading_start = time.time()
        get_user_input("\nPress Enter when you've understood the analogy...")
        reading_time = int(time.time() - reading_start)
        
        # Determine comprehension speed
        expected_reading_time = len(analogy) * 0.05  # ~50ms per character
        if reading_time < expected_reading_time * 0.7:
            comprehension = "fast"
        elif reading_time > expected_reading_time * 1.5:
            comprehension = "slow"
        else:
            comprehension = "normal"
        
        # Store Step 1 details
        cursor.execute('''
            INSERT INTO step1_analogies 
            (interaction_id, analogy_presented, reading_time, comprehension_indicator, 
             personalization_used, user_level, previous_concepts)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            interaction_id, analogy, reading_time, comprehension,
            json.dumps(personalization_context), user_profile.level,
            json.dumps(known_concepts)
        ))
        
        conn.commit()
        conn.close()
        
        # Record step completion
        self._end_step(1, True, {
            "concept": topic,
            "reading_time": reading_time,
            "comprehension_speed": comprehension,
            "personalization_applied": True,
            "analogy_complexity": len(analogy.split())
        })
        
        return analogy

    def run_step_2_prediction(self, topic: str, step_1_context: str, user_profile: UserProfile) -> None:
        """Enhanced Step 2 with metacognitive tracking."""
        interaction_id = self._start_step(2, "Predict the Output")
        print_header(f"Step 2: Predict the Output for '{topic}'")
        
        # Generate prediction question (enhanced)
        question_data = {
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
                "A": "Laptop-Alice, Mouse-Bob, Keyboard-NULL",
                "B": "Laptop-Alice, Mouse-Bob",
                "C": "All items with customer names",
                "D": "Laptop-Alice, Mouse-Bob, Keyboard-Unknown, NoOrder-Charlie"
            },
            "correct": "B"
        }
        
        # Display question
        print(f"\n-- Scenario: {question_data['scenario']} --\n")
        print("Orders Table:")
        for order in question_data['tables']['Orders']:
            print(f"  {order}")
        print("\nCustomers Table:")
        for customer in question_data['tables']['Customers']:
            print(f"  {customer}")
        print(f"\nQuery: {question_data['query']}")
        print("\nWhat will be the output?")
        for key, value in question_data['options'].items():
            print(f"  {key}. {value}")
        
        # Track hesitation and response
        print("\n🤔 Think carefully about which rows will match...")
        hesitation_start = time.time()
        
        # Simplified timing
        user_answer = get_user_input("Your prediction (A/B/C/D): ").upper()
        total_answer_time = time.time() - hesitation_start
        
        # Check if they want to change answer
        change_answer = get_user_input("Do you want to change your answer? (y/n): ").lower() == 'y'
        if change_answer:
            user_answer = get_user_input("New answer (A/B/C/D): ").upper()
        
        # Provide feedback
        correct_answer = question_data['correct']
        is_correct = user_answer == correct_answer
        
        if is_correct:
            print(f"\n✅ Excellent! You correctly predicted that {topic} only returns matching rows.")
        else:
            print(f"\n❌ Not quite. The correct answer is {correct_answer}.")
            print(f"Remember: {topic} only includes rows where the join condition is satisfied in BOTH tables.")
        
        # Store detailed Step 2 data
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO step2_predictions 
            (interaction_id, question_presented, options_presented, correct_answer, user_answer,
             time_to_answer, answer_changed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            interaction_id, json.dumps(question_data), json.dumps(question_data['options']),
            correct_answer, user_answer, int(total_answer_time), change_answer
        ))
        
        conn.commit()
        conn.close()
        
        self._end_step(2, True, {
            "prediction_accuracy": is_correct,
            "answer_changed": change_answer,
            "total_response_time": int(total_answer_time)
        })

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