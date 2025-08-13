"""
Enhanced data viewer for comprehensive learning analytics.
"""

import sqlite3
import json
from datetime import datetime

def view_enhanced_learning_data():
    """Display comprehensive learning analytics."""
    conn = sqlite3.connect('pedagogical_ai.db')
    cursor = conn.cursor()
    
    print("🚀 Enhanced Learning Analytics Dashboard")
    print("=" * 60)
    
    # 1. User Overview
    print("\n👤 Users and Their Learning Journey:")
    cursor.execute('''
        SELECT u.user_id, u.name, u.level, 
               COUNT(DISTINCT ls.session_id) as total_sessions,
               MAX(ls.session_start) as last_activity
        FROM users u
        LEFT JOIN learning_sessions ls ON u.user_id = ls.user_id
        GROUP BY u.user_id
    ''')
    users = cursor.fetchall()
    for user in users:
        print(f"  📚 {user[1]} ({user[0]}) - {user[2]} level")
        print(f"      Sessions: {user[3]}, Last seen: {user[4] or 'Never'}")
    
    # 2. Concept Mastery Analysis
    print(f"\n🧠 Concept Mastery Levels:")
    cursor.execute('''
        SELECT c.concept_name, cm.user_id, cm.mastery_level, 
               cm.total_attempts, cm.successful_attempts, cm.last_updated
        FROM concept_mastery cm
        JOIN concepts c ON cm.concept_id = c.concept_id
        ORDER BY cm.mastery_level DESC
    ''')
    mastery_data = cursor.fetchall()
    
    if mastery_data:
        for mastery in mastery_data:
            concept, user, level, attempts, success, updated = mastery
            success_rate = (success / attempts * 100) if attempts > 0 else 0
            level_emoji = "🌟" if level > 0.8 else "📈" if level > 0.5 else "📚"
            print(f"  {level_emoji} {concept}: {level:.2f} mastery")
            print(f"      User: {user}, Success Rate: {success_rate:.1f}% ({success}/{attempts})")
            print(f"      Last Updated: {updated}")
    else:
        print("  No mastery data yet - complete some learning sessions!")
    
    # 3. Step 1 Analytics
    print(f"\n🎭 Step 1 - Analogy Effectiveness:")
    cursor.execute('''
        SELECT sa.user_level, sa.reading_time, sa.comprehension_indicator,
               COUNT(*) as count, AVG(sa.reading_time) as avg_reading_time
        FROM step1_analogies sa
        GROUP BY sa.user_level, sa.comprehension_indicator
    ''')
    step1_data = cursor.fetchall()
    
    for data in step1_data:
        level, reading_time, comprehension, count, avg_time = data
        print(f"  📖 {level} learners: {comprehension} comprehension ({count} sessions)")
        print(f"      Average reading time: {avg_time:.1f}s")
    
    # 4. Step 2 Analytics
    print(f"\n🔮 Step 2 - Prediction Performance:")
    cursor.execute('''
        SELECT sp.correct_answer, sp.user_answer, 
               (sp.correct_answer = sp.user_answer) as is_correct,
               sp.time_to_answer, sp.answer_changed
        FROM step2_predictions sp
    ''')
    step2_data = cursor.fetchall()
    
    if step2_data:
        correct_count = sum(1 for row in step2_data if row[2])
        total_count = len(step2_data)
        accuracy = correct_count / total_count * 100
        avg_time = sum(row[3] for row in step2_data) / total_count
        changed_answers = sum(1 for row in step2_data if row[4])
        
        print(f"  🎯 Overall Accuracy: {accuracy:.1f}% ({correct_count}/{total_count})")
        print(f"  ⏱️  Average Response Time: {avg_time:.1f}s")
        print(f"  🔄 Changed Answers: {changed_answers}/{total_count} ({changed_answers/total_count*100:.1f}%)")
    
    # 5. Step 3 - Query Writing Analysis (Most Detailed)
    print(f"\n✍️ Step 3 - Query Writing Deep Dive:")
    cursor.execute('''
        SELECT qa.interaction_id, qa.attempt_number, qa.syntax_valid,
               qa.error_type, qa.time_since_start, qa.char_count
        FROM query_attempts qa
        ORDER BY qa.interaction_id, qa.attempt_number
    ''')
    query_attempts = cursor.fetchall()
    
    if query_attempts:
        # Group by interaction
        interactions = {}
        for attempt in query_attempts:
            interaction_id = attempt[0]
            if interaction_id not in interactions:
                interactions[interaction_id] = []
            interactions[interaction_id].append(attempt)
        
        print(f"  📝 Total Query Writing Sessions: {len(interactions)}")
        
        for interaction_id, attempts in interactions.items():
            print(f"\n  Session {interaction_id}:")
            for i, attempt in enumerate(attempts):
                _, attempt_num, syntax_valid, error_type, time_elapsed, char_count = attempt
                status = "✅" if syntax_valid else "❌"
                error_info = f" ({error_type})" if error_type else ""
                print(f"    Attempt {attempt_num}: {status} {char_count} chars, {time_elapsed}s elapsed{error_info}")
            
            # Show progression
            if len(attempts) > 1:
                first_valid = attempts[0][2]
                last_valid = attempts[-1][2] 
                if not first_valid and last_valid:
                    print(f"    📈 Improvement: Fixed syntax errors!")
    
    # 6. Step 3 Explanations
    print(f"\n💬 Step 3 - Explanation Quality:")
    cursor.execute('''
        SELECT se.word_count, se.clarity_score, se.accuracy_score,
               se.concepts_mentioned, se.writing_time
        FROM step3_explanations se
    ''')
    explanations = cursor.fetchall()
    
    if explanations:
        avg_words = sum(row[0] for row in explanations) / len(explanations)
        avg_clarity = sum(row[1] for row in explanations) / len(explanations)
        avg_accuracy = sum(row[2] for row in explanations) / len(explanations)
        avg_time = sum(row[4] for row in explanations) / len(explanations)
        
        print(f"  📊 Average Explanation Length: {avg_words:.1f} words")
        print(f"  🎯 Average Clarity Score: {avg_clarity:.2f}/1.0")
        print(f"  ✅ Average Accuracy Score: {avg_accuracy:.2f}/1.0") 
        print(f"  ⏱️  Average Writing Time: {avg_time:.1f}s")
        
        # Show concept mentions
        all_concepts = []
        for exp in explanations:
            if exp[3]:  # concepts_mentioned
                try:
                    concepts = json.loads(exp[3])
                    all_concepts.extend(concepts)
                except:
                    pass
        
        if all_concepts:
            concept_counts = {}
            for concept in all_concepts:
                concept_counts[concept] = concept_counts.get(concept, 0) + 1
            
            print(f"  🔤 Most Mentioned Concepts:")
            for concept, count in sorted(concept_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
                print(f"      {concept}: {count} times")
    
    # 7. Step 4 - Challenge Performance
    print(f"\n🏆 Step 4 - Challenge Performance:")
    cursor.execute('''
        SELECT sc.problem_difficulty, sc.final_success, sc.total_solving_time,
               sc.concepts_tested
        FROM step4_challenges sc
    ''')
    challenges = cursor.fetchall()
    
    if challenges:
        success_count = sum(1 for row in challenges if row[1])
        total_challenges = len(challenges)
        success_rate = success_count / total_challenges * 100
        avg_time = sum(row[2] for row in challenges) / total_challenges
        
        print(f"  🎯 Challenge Success Rate: {success_rate:.1f}% ({success_count}/{total_challenges})")
        print(f"  ⏱️  Average Solving Time: {avg_time:.1f}s ({avg_time//60:.0f}m {avg_time%60:.0f}s)")
        
        # Difficulty breakdown
        difficulty_stats = {}
        for challenge in challenges:
            difficulty = challenge[0]
            success = challenge[1]
            if difficulty not in difficulty_stats:
                difficulty_stats[difficulty] = {"total": 0, "success": 0}
            difficulty_stats[difficulty]["total"] += 1
            if success:
                difficulty_stats[difficulty]["success"] += 1
        
        print(f"  📊 Performance by Difficulty:")
        for difficulty, stats in difficulty_stats.items():
            rate = stats["success"] / stats["total"] * 100
            print(f"      {difficulty}: {rate:.1f}% ({stats['success']}/{stats['total']})")
    
    # 8. Learning Analytics Summary
    print(f"\n📈 Learning Analytics Summary:")
    cursor.execute('''
        SELECT la.learning_efficiency, la.engagement_score,
               la.concepts_attempted, la.analysis_date
        FROM learning_analytics la
        ORDER BY la.analysis_date DESC
    ''')
    analytics = cursor.fetchall()
    
    if analytics:
        latest = analytics[0]
        efficiency, engagement, concepts_json, date = latest
        
        try:
            concepts = json.loads(concepts_json) if concepts_json else []
        except:
            concepts = []
        
        print(f"  📊 Latest Session Analysis ({date}):")
        print(f"      Learning Efficiency: {efficiency:.2f}")
        print(f"      Engagement Score: {engagement:.2f}")
        print(f"      Concepts Attempted: {', '.join(concepts) if concepts else 'None'}")
    
    # 9. Overall Statistics
    print(f"\n🎊 Overall Platform Statistics:")
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM learning_sessions WHERE completed = 1')
    completed_sessions = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM step_interactions')
    total_interactions = cursor.fetchone()[0]
    
    cursor.execute('SELECT SUM(total_duration) FROM learning_sessions WHERE total_duration IS NOT NULL')
    total_learning_time = cursor.fetchone()[0] or 0
    
    print(f"  👥 Total Users: {total_users}")
    print(f"  📚 Completed Sessions: {completed_sessions}")
    print(f"  🔄 Total Step Interactions: {total_interactions}")
    print(f"  ⏱️  Total Learning Time: {total_learning_time//3600:.0f}h {(total_learning_time%3600)//60:.0f}m")
    
    conn.close()
    
    print(f"\n🔮 This comprehensive data enables:")
    print(f"  • Personalized learning path recommendations")
    print(f"  • Early identification of learning difficulties")
    print(f"  • Adaptive content difficulty adjustment")
    print(f"  • Concept mastery progression tracking")
    print(f"  • Learning efficiency optimization")

if __name__ == "__main__":
    view_enhanced_learning_data() 