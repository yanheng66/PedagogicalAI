"""
Reset the database to match our controller requirements.
"""

import sqlite3
import os

def reset_database():
    """Drop and recreate the database with correct schema."""
    
    # Remove existing database file
    if os.path.exists('pedagogical_ai.db'):
        os.remove('pedagogical_ai.db')
        print("🗑️  Removed existing database")
    
    # Create new database with correct schema
    conn = sqlite3.connect('pedagogical_ai.db')
    cursor = conn.cursor()
    
    print("📊 Creating tables with correct schema...")
    
    # Users table
    cursor.execute('''
        CREATE TABLE users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            level TEXT DEFAULT 'Beginner',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Learning sessions table
    cursor.execute('''
        CREATE TABLE learning_sessions (
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
    
    # Step interactions table with all required columns
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
            metadata TEXT,
            FOREIGN KEY (session_id) REFERENCES learning_sessions (session_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print("✅ Database reset complete with correct schema!")

if __name__ == "__main__":
    reset_database() 