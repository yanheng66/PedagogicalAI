"""
Enhanced database schema with core missing tables.
"""

import sqlite3
import os

def create_enhanced_schema():
    """Create enhanced database schema with all core tables."""
    
    # Remove existing database
    if os.path.exists('pedagogical_ai.db'):
        os.remove('pedagogical_ai.db')
        print("🗑️ Removed existing database")
    
    conn = sqlite3.connect('pedagogical_ai.db')
    cursor = conn.cursor()
    
    print("📊 Creating enhanced database schema...")
    
    # 1. Basic tables (existing)
    cursor.execute('''
        CREATE TABLE users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            level TEXT DEFAULT 'Beginner',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            total_learning_time INTEGER DEFAULT 0,
            preferred_language TEXT DEFAULT 'en'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE concepts (
            concept_id TEXT PRIMARY KEY,
            concept_name TEXT NOT NULL,
            category TEXT,
            difficulty_base INTEGER,
            prerequisites TEXT,  -- JSON array
            estimated_time INTEGER,
            description TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE learning_sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT,
            concept_id TEXT,
            session_start TEXT DEFAULT CURRENT_TIMESTAMP,
            session_end TEXT,
            completed BOOLEAN DEFAULT FALSE,
            total_duration INTEGER,
            mastery_before REAL DEFAULT 0.0,
            mastery_after REAL,
            device_type TEXT,
            ip_address TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (concept_id) REFERENCES concepts (concept_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE step_interactions (
            interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            step_number INTEGER,
            step_name TEXT,
            start_time TEXT,
            end_time TEXT,
            duration INTEGER,
            success BOOLEAN,
            metadata TEXT,  -- JSON
            FOREIGN KEY (session_id) REFERENCES learning_sessions (session_id)
        )
    ''')
    
    # 2. 🔴 HIGH PRIORITY: Core user modeling tables
    
    # Concept Mastery - tracks user's mastery of each concept
    cursor.execute('''
        CREATE TABLE concept_mastery (
            mastery_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            concept_id TEXT,
            mastery_level REAL DEFAULT 0.0,
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
            total_attempts INTEGER DEFAULT 0,
            successful_attempts INTEGER DEFAULT 0,
            retention_score REAL DEFAULT 0.0,
            step3_performance TEXT,  -- JSON with step3 metrics
            step4_performance TEXT,  -- JSON with step4 metrics
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (concept_id) REFERENCES concepts (concept_id),
            UNIQUE(user_id, concept_id)
        )
    ''')
    
    # Error Patterns - tracks recurring mistakes
    cursor.execute('''
        CREATE TABLE error_patterns (
            pattern_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            pattern_type TEXT,  -- 'syntax', 'logic', 'conceptual'
            pattern_description TEXT,
            frequency INTEGER DEFAULT 1,
            first_observed TEXT DEFAULT CURRENT_TIMESTAMP,
            last_observed TEXT DEFAULT CURRENT_TIMESTAMP,
            concepts_affected TEXT,  -- JSON array
            severity TEXT DEFAULT 'medium',  -- 'low', 'medium', 'high'
            suggested_remediation TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # Query Attempts - detailed tracking of Step 3 query writing
    cursor.execute('''
        CREATE TABLE query_attempts (
            attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
            interaction_id INTEGER,
            attempt_number INTEGER,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            query_text TEXT,
            syntax_valid BOOLEAN,
            execution_successful BOOLEAN,
            execution_time_ms INTEGER,
            error_type TEXT,
            error_message TEXT,
            time_since_start INTEGER,  -- seconds since step started
            char_count INTEGER,
            word_count INTEGER,
            delete_count INTEGER DEFAULT 0,  -- backspace/delete operations
            pause_duration INTEGER DEFAULT 0,  -- pause before this attempt
            FOREIGN KEY (interaction_id) REFERENCES step_interactions (interaction_id)
        )
    ''')
    
    # Learning Analytics - session summaries and aggregated metrics
    cursor.execute('''
        CREATE TABLE learning_analytics (
            analytics_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            session_id TEXT,
            analysis_date TEXT DEFAULT CURRENT_TIMESTAMP,
            concepts_attempted TEXT,  -- JSON array
            concepts_mastered TEXT,   -- JSON array
            average_mastery_level REAL,
            learning_velocity REAL,  -- concepts per hour
            strongest_category TEXT,
            weakest_category TEXT,
            error_rate REAL,
            self_correction_rate REAL,
            help_seeking_frequency REAL,
            engagement_score REAL,
            learning_efficiency REAL,
            recommended_next_concepts TEXT,  -- JSON array
            session_notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (session_id) REFERENCES learning_sessions (session_id)
        )
    ''')
    
    # 3. 🟡 MEDIUM PRIORITY: Detailed step tracking
    
    # Step 1 Analogies
    cursor.execute('''
        CREATE TABLE step1_analogies (
            analogy_id INTEGER PRIMARY KEY AUTOINCREMENT,
            interaction_id INTEGER,
            analogy_presented TEXT,
            reading_time INTEGER,
            comprehension_indicator TEXT,  -- 'fast', 'normal', 'slow'
            personalization_used TEXT,  -- JSON
            user_level TEXT,
            previous_concepts TEXT,  -- JSON array
            regeneration_attempt INTEGER DEFAULT 0,  -- 0 for initial, 1+ for regenerations
            user_understood BOOLEAN,  -- true if user selected "understand"
            FOREIGN KEY (interaction_id) REFERENCES step_interactions (interaction_id)
        )
    ''')
    
    # Step 2 Predictions
    cursor.execute('''
        CREATE TABLE step2_predictions (
            prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            interaction_id INTEGER,
            question_presented TEXT,  -- JSON
            options_presented TEXT,   -- JSON
            correct_answer TEXT,
            user_answer TEXT,
            time_to_answer INTEGER,
            hesitation_time INTEGER,  -- time before first selection
            answer_changed BOOLEAN DEFAULT FALSE,
            confidence_level INTEGER,  -- 1-5 scale
            hint_used BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (interaction_id) REFERENCES step_interactions (interaction_id)
        )
    ''')
    
    # Step 2 Dynamic Implementation Tables
    cursor.execute('''
        CREATE TABLE step2_questions (
            question_id TEXT PRIMARY KEY,
            interaction_id INTEGER,
            question_data TEXT,  -- JSON with generated question
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (interaction_id) REFERENCES step_interactions (interaction_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE step2_attempts (
            attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
            interaction_id INTEGER,
            attempt_number INTEGER,
            user_answer TEXT,
            correct_answer TEXT,
            is_correct BOOLEAN,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (interaction_id) REFERENCES step_interactions (interaction_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE step2_sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            interaction_id INTEGER,
            question_data TEXT,  -- JSON with final question used
            total_attempts INTEGER,
            questions_tried INTEGER,
            final_success BOOLEAN,
            total_time INTEGER,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (interaction_id) REFERENCES step_interactions (interaction_id)
        )
    ''')
    
    # Step 3 Explanations
    cursor.execute('''
        CREATE TABLE step3_explanations (
            explanation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            interaction_id INTEGER,
            explanation_text TEXT,
            word_count INTEGER,
            concepts_mentioned TEXT,  -- JSON array
            clarity_score REAL,
            accuracy_score REAL,
            conceptual_understanding_score REAL,
            ai_feedback TEXT,  -- JSON
            writing_time INTEGER,
            FOREIGN KEY (interaction_id) REFERENCES step_interactions (interaction_id)
        )
    ''')
    
    # Step 4 Challenges
    cursor.execute('''
        CREATE TABLE step4_challenges (
            challenge_id INTEGER PRIMARY KEY AUTOINCREMENT,
            interaction_id INTEGER,
            problem_id TEXT,
            problem_difficulty TEXT,
            concepts_tested TEXT,  -- JSON array
            challenge_selected_based_on TEXT,  -- JSON with reasoning
            solution_attempts TEXT,  -- JSON array of attempts
            final_success BOOLEAN,
            problem_solving_approach TEXT,  -- 'systematic', 'trial_error', 'methodical'
            concepts_used TEXT,  -- JSON array
            skill_transfer_demonstrated BOOLEAN,
            time_to_first_attempt INTEGER,
            total_solving_time INTEGER,
            FOREIGN KEY (interaction_id) REFERENCES step_interactions (interaction_id)
        )
    ''')
    
    # Step 4 Dynamic Implementation Tables
    cursor.execute('''
        CREATE TABLE step4_questions (
            question_id TEXT PRIMARY KEY,
            interaction_id INTEGER,
            question_data TEXT,  -- JSON with generated challenge
            difficulty TEXT,
            step3_score INTEGER,  -- Score that determined this difficulty
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (interaction_id) REFERENCES step_interactions (interaction_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE step4_attempts (
            attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
            interaction_id INTEGER,
            attempt_number INTEGER,
            user_solution TEXT,
            feedback TEXT,
            is_correct BOOLEAN,
            feedback_type TEXT,  -- 'correct', 'incorrect', 'hint'
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (interaction_id) REFERENCES step_interactions (interaction_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE step4_sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            interaction_id INTEGER,
            question_data TEXT,  -- JSON with final question used
            total_attempts INTEGER,
            final_success BOOLEAN,
            total_time INTEGER,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (interaction_id) REFERENCES step_interactions (interaction_id)
        )
    ''')
    
    print("✅ Enhanced database schema created!")
    print("📊 Created tables:")
    print("   🔴 Core: concept_mastery, error_patterns, query_attempts, learning_analytics")
    print("   🟡 Detailed: step1_analogies, step2_predictions, step3_explanations, step4_challenges")
    print("   🟢 Step 2 Dynamic: step2_questions, step2_attempts, step2_sessions")
    print("   🟢 Step 4 Dynamic: step4_questions, step4_attempts, step4_sessions")
    
    # Insert some sample concepts
    sample_concepts = [
        ('INNER_JOIN', 'INNER JOIN', 'joins', 3, '["SELECT", "WHERE"]', 15, 'Inner join between tables'),
        ('LEFT_JOIN', 'LEFT JOIN', 'joins', 4, '["INNER_JOIN"]', 20, 'Left outer join'),
        ('GROUP_BY', 'GROUP BY', 'aggregation', 4, '["SELECT", "WHERE"]', 18, 'Grouping rows'),
        ('HAVING', 'HAVING', 'aggregation', 5, '["GROUP_BY"]', 22, 'Filtering grouped results'),
    ]
    
    cursor.executemany('''
        INSERT INTO concepts (concept_id, concept_name, category, difficulty_base, prerequisites, estimated_time, description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', sample_concepts)
    
    conn.commit()
    conn.close()
    
    print("🎯 Sample concepts added!")

if __name__ == "__main__":
    create_enhanced_schema() 