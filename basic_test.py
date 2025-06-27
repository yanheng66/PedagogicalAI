"""
Basic database connectivity test.
"""

import sqlite3
import json
from datetime import datetime

def test_basic_db():
    """Test basic database operations with raw SQL."""
    print("Testing basic database connectivity...")
    
    # Connect to SQLite database
    conn = sqlite3.connect('pedagogical_ai.db')
    cursor = conn.cursor()
    
    try:
        # Create basic tables
        print("1. Creating tables...")
        
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
                mastery_before REAL DEFAULT 0.0,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS step_interactions (
                interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                step_number INTEGER,
                success BOOLEAN,
                duration INTEGER,
                metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES learning_sessions (session_id)
            )
        ''')
        
        print("   ✅ Tables created")
        
        # Test data insertion
        print("\n2. Inserting test data...")
        
        # Insert user
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, name, level)
            VALUES (?, ?, ?)
        ''', ('test_user_123', 'Test User', 'Beginner'))
        
        # Insert session
        session_id = 'session_' + datetime.now().strftime('%Y%m%d_%H%M%S')
        cursor.execute('''
            INSERT INTO learning_sessions (session_id, user_id, concept_name, mastery_before)
            VALUES (?, ?, ?, ?)
        ''', (session_id, 'test_user_123', 'INNER JOIN', 0.0))
        
        # Insert interactions
        for step in range(1, 4):
            metadata = json.dumps({
                f"step_{step}_data": f"test_data_for_step_{step}",
                "success": True,
                "duration": 120 + step * 60
            })
            
            cursor.execute('''
                INSERT INTO step_interactions (session_id, step_number, success, duration, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, step, True, 120 + step * 60, metadata))
        
        print(f"   ✅ Data inserted for session: {session_id}")
        
        # Test data retrieval
        print("\n3. Retrieving data...")
        
        cursor.execute('''
            SELECT 
                u.name,
                ls.concept_name,
                ls.session_start,
                COUNT(si.interaction_id) as total_steps
            FROM users u
            JOIN learning_sessions ls ON u.user_id = ls.user_id
            LEFT JOIN step_interactions si ON ls.session_id = si.session_id
            WHERE u.user_id = ?
            GROUP BY u.user_id, ls.session_id
        ''', ('test_user_123',))
        
        results = cursor.fetchall()
        for row in results:
            print(f"   📊 User: {row[0]}, Concept: {row[1]}, Steps: {row[3]}")
        
        # Commit changes
        conn.commit()
        print("\n🎉 Basic database test passed! SQLite is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    test_basic_db() 