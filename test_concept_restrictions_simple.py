#!/usr/bin/env python3
"""
Simple test script to verify concept restriction logic without external dependencies
"""

def map_topic_to_concept_id(topic: str) -> str:
    """Map various topic formats to concept IDs."""
    topic_upper = topic.upper()
    mapping = {
        'SELECT': 'select-from',
        'FROM': 'select-from',
        'SELECT & FROM': 'select-from',
        'WHERE': 'where',
        'ORDER BY': 'order-by',
        'INNER JOIN': 'inner-join',
        'JOIN': 'inner-join',
        'LEFT JOIN': 'left-join',
        'RIGHT JOIN': 'right-join',
        'COUNT': 'aggregates',
        'SUM': 'aggregates',
        'AVG': 'aggregates',
        'AGGREGATES': 'aggregates',
        'GROUP BY': 'group-by',
        'HAVING': 'having',
        'SUBQUERIES': 'subqueries',
        'CASE': 'case',
    }
    return mapping.get(topic_upper, 'select-from')

def get_available_concepts(current_topic: str) -> list:
    """Get available SQL concepts based on curriculum roadmap."""
    
    # Define curriculum roadmap order
    curriculum_order = [
        'select-from',      # Unit 1: SELECT & FROM
        'where',            # Unit 1: WHERE
        'order-by',         # Unit 1: ORDER BY
        'inner-join',       # Unit 2: INNER JOIN
        'left-join',        # Unit 2: LEFT JOIN
        'right-join',       # Unit 2: RIGHT JOIN
        'aggregates',       # Unit 3: COUNT, SUM, AVG
        'group-by',         # Unit 3: GROUP BY
        'having',           # Unit 3: HAVING
        'subqueries',       # Unit 4: Subqueries
        'case',             # Unit 4: CASE Statements
    ]
    
    # Map concept IDs to SQL keywords
    concept_to_sql = {
        'select-from': ['SELECT', 'FROM'],
        'where': ['WHERE'],
        'order-by': ['ORDER BY'],
        'inner-join': ['INNER JOIN', 'JOIN'],
        'left-join': ['LEFT JOIN'],
        'right-join': ['RIGHT JOIN'],
        'aggregates': ['COUNT', 'SUM', 'AVG', 'MIN', 'MAX'],
        'group-by': ['GROUP BY'],
        'having': ['HAVING'],
        'subqueries': ['subqueries', 'nested queries'],
        'case': ['CASE', 'WHEN', 'THEN', 'ELSE', 'END'],
    }
    
    # Get current topic index
    current_topic_mapped = map_topic_to_concept_id(current_topic)
    try:
        current_index = curriculum_order.index(current_topic_mapped)
    except ValueError:
        current_index = 0  # Default to beginning if topic not found
    
    # STRICT: For early concepts, only include current concept to prevent confusion
    if current_topic_mapped in ['select-from', 'where', 'order-by']:
        # For fundamental concepts, be very conservative
        if current_topic_mapped == 'select-from':
            available_concept_ids = ['select-from']  # ONLY SELECT/FROM
        elif current_topic_mapped == 'where':
            available_concept_ids = ['select-from', 'where']  # Only up to WHERE
        else:  # order-by
            available_concept_ids = ['select-from', 'where', 'order-by']  # Only up to ORDER BY
    else:
        # For advanced concepts, include all previous concepts
        available_concept_ids = curriculum_order[:current_index + 1]
    
    # Convert to SQL keywords
    available_concepts = []
    for concept_id in available_concept_ids:
        available_concepts.extend(concept_to_sql.get(concept_id, []))
    
    return available_concepts

def test_concept_restrictions():
    """Test the concept restriction logic for different topics."""
    
    # Test cases for different learning levels
    test_cases = [
        "SELECT & FROM",
        "WHERE", 
        "ORDER BY",
        "INNER JOIN",
        "LEFT JOIN",
        "COUNT",
        "GROUP BY"
    ]
    
    print("=== Testing Concept Restrictions ===\n")
    
    for topic in test_cases:
        print(f"📚 Topic: {topic}")
        
        # Get available concepts
        available_concepts = get_available_concepts(topic)
        print(f"   Available Concepts: {available_concepts}")
        
        # Get concept mapping
        concept_id = map_topic_to_concept_id(topic)
        print(f"   Concept ID: {concept_id}")
        
        # Check if this is a fundamental concept
        is_fundamental = concept_id in ['select-from', 'where', 'order-by']
        max_tables = 1 if is_fundamental else 2
        print(f"   Max Tables: {max_tables}")
        print(f"   Is Fundamental: {is_fundamental}")
        
        # Check for dangerous combinations
        has_join = any('JOIN' in concept for concept in available_concepts)
        if topic in ["SELECT & FROM"] and has_join:
            print(f"   ⚠️  WARNING: JOIN concepts found in SELECT/FROM level!")
        
        print("-" * 50)

if __name__ == "__main__":
    test_concept_restrictions() 