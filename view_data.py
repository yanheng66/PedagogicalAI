"""
View learning data from the database.
"""

import sqlite3
import json

def view_learning_data():
    """Display learning data in a formatted way."""
    conn = sqlite3.connect('pedagogical_ai.db')
    cursor = conn.cursor()
    
    print("📊 Learning Data Summary")
    print("=" * 50)
    
    # Users
    print("\n👤 Users:")
    cursor.execute('SELECT user_id, name, level, created_at FROM users')
    users = cursor.fetchall()
    for user in users:
        print(f"  - {user[1]} ({user[0]}) - Level: {user[2]} - Joined: {user[3]}")
    
    # Learning Sessions
    print(f"\n📚 Learning Sessions:")
    cursor.execute('''
        SELECT ls.session_id, ls.user_id, COALESCE(c.concept_name, ls.concept_id) AS concept_name,
               ls.session_start, ls.session_end, ls.mastery_before, ls.mastery_after
        FROM learning_sessions ls
        LEFT JOIN concepts c ON ls.concept_id = c.concept_id
    ''')
    sessions = cursor.fetchall()
    for session in sessions:
        print(f"  Session: {session[0][:8]}...")
        print(f"    User: {session[1]}")
        print(f"    Concept: {session[2]}")
        print(f"    Started: {session[3]}")
        print(f"    Ended: {session[4] or 'In Progress'}")
        print(f"    Mastery: {session[5]} → {session[6] or 'TBD'}")
        print()
    
    # Step Interactions
    print(f"🔄 Step Interactions:")
    cursor.execute('''
        SELECT si.session_id, si.step_number, si.step_name, si.duration, 
               si.success, si.metadata
        FROM step_interactions si
        ORDER BY si.session_id, si.step_number
    ''')
    interactions = cursor.fetchall()
    
    current_session = None
    for interaction in interactions:
        if interaction[0] != current_session:
            current_session = interaction[0]
            print(f"\n  Session {current_session[:8]}:")
        
        step_name = interaction[2] or f"Step {interaction[1]}"
        duration = f"{interaction[3]}s" if interaction[3] else "In Progress"
        success = "✅" if interaction[4] else "❌" if interaction[4] is False else "⏳"
        
        print(f"    {success} {step_name} - {duration}")
        
        # Show metadata if available
        if interaction[5]:
            try:
                metadata = json.loads(interaction[5])
                if isinstance(metadata, dict):
                    for key, value in metadata.items():
                        if len(str(value)) < 50:  # Only show short values
                            print(f"        {key}: {value}")
            except:
                pass
    
    print(f"\n📈 Statistics:")
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM learning_sessions')
    session_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM step_interactions')
    interaction_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT AVG(duration) FROM step_interactions WHERE duration IS NOT NULL')
    avg_duration = cursor.fetchone()[0]
    
    print(f"  Total Users: {user_count}")
    print(f"  Total Sessions: {session_count}")
    print(f"  Total Interactions: {interaction_count}")
    print(f"  Average Step Duration: {avg_duration:.1f}s" if avg_duration else "  Average Step Duration: N/A")
    
    conn.close()

if __name__ == "__main__":
    view_learning_data() 