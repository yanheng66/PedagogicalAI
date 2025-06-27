import sqlite3

conn = sqlite3.connect('pedagogical_ai.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("📊 Database Tables Created:")
for table in tables:
    print(f"  ✅ {table[0]}")

cursor.execute("SELECT COUNT(*) FROM concepts")
concept_count = cursor.fetchone()[0]
print(f"\n🎯 Sample concepts loaded: {concept_count}")

if concept_count > 0:
    cursor.execute("SELECT concept_name, category, difficulty_base FROM concepts")
    concepts = cursor.fetchall()
    for concept in concepts:
        print(f"   - {concept[0]} ({concept[1]}, difficulty: {concept[2]})")

conn.close() 