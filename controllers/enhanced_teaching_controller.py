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
from services.firestore_service import (
    get_client, add_document, update_document, get_document, 
    delete_document, list_collection
)
from models.user_profile import UserProfile
from utils.io_helpers import get_user_input, print_header

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
        # Store Step 1 analogy in memory for Step 2 access
        self.current_analogy: str | None = None
        self.current_topic: str | None = None
    
    def _get_firestore_client(self):
        """Get Firestore client."""
        return get_client()
    
    def start_concept_session(self, topic: str, user_profile: UserProfile) -> str:
        """Start enhanced learning session with full user modeling."""
        try:
            self.session_start_time = time.time()
            
            # Get or create concept
            concept_id = topic.upper().replace(" ", "_")
            self.concept_id = concept_id
            
            # Get or create concept document
            concept_doc = get_document("concepts", concept_id)
            if not concept_doc:
                add_document("concepts", {
                    "concept_id": concept_id,
                    "concept_name": topic,
                    "category": "unknown"
                }, concept_id)
            
            # Ensure user exists
            update_document("users", self.user_id, {
                "user_id": self.user_id,
                "name": user_profile.name,
                "level": user_profile.level
            })
            
            # Get current mastery level
            mastery_doc = get_document("concept_mastery", f"{self.user_id}_{concept_id}")
            current_mastery = mastery_doc.get("mastery_level", 0.0) if mastery_doc else 0.0
            
            # Create new session
            self.session_id = 'session_' + str(uuid.uuid4())[:8]
            add_document("learning_sessions", {
                "session_id": self.session_id,
                "user_id": self.user_id,
                "concept_id": concept_id,
                "mastery_before": current_mastery,
                "timestamp": datetime.now().isoformat()
            }, self.session_id)
            
            print(f"🔗 Enhanced Session: {self.session_id} for '{topic}' (current mastery: {current_mastery:.2f})")
            return self.session_id
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            return None
    
    def _start_step(self, step_number: int, step_name: str) -> str:
        """Start step with enhanced tracking."""
        self.current_step_start_time = time.time()
        
        interaction_data = {
            "session_id": self.session_id,
            "step_number": step_number,
            "step_name": step_name,
            "start_time": datetime.now().isoformat()
        }
        
        # Generate a unique interaction ID
        interaction_id = f"interaction_{self.session_id}_{step_number}_{int(time.time())}"
        add_document("step_interactions", interaction_data, interaction_id)
        
        self.current_interaction_id = interaction_id
        return interaction_id
    
    def _end_step(self, step_number: int, success: bool = True, metadata: dict = None):
        """End step with enhanced tracking."""
        if self.current_step_start_time is None:
            return
            
        duration = int(time.time() - self.current_step_start_time)
        
        # Update step interaction
        update_document("step_interactions", self.current_interaction_id, {
            "end_time": datetime.now().isoformat(),
            "duration": duration,
            "success": success,
            "metadata": json.dumps(metadata) if metadata else None
        })

        # --- Roadmap progress update ---
        try:
            # Update or insert progress
            progress_id = f"{self.user_id}_{self.concept_id}"
            update_document("roadmap_progress", progress_id, {
                "user_id": self.user_id,
                "concept_id": self.concept_id,
                "step_completed": step_number
            })
        except Exception:
            pass
        
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
        system_prompt = """You are an expert SQL instructor who explains concepts using vivid, creative analogies and also guides learners to reflect metacognitively. Keep explanations concise, engaging, and clear for beginners. Always follow your analogy with 1-2 reflection questions prompting the learner to think about how the analogy relates to their prior knowledge or experiences."""
        
        user_prompt = f"""Explain the concept of {topic} using a vivid real-life analogy.

- Avoid SQL syntax or code.
- Keep the explanation under 120 words.
- After the analogy, include 1-2 metacognitive reflection questions, for example:
    • "Does this analogy connect to something you've experienced?"
    • "Can you explain this idea back in your own words?"
    • "What part of this analogy makes the concept clearer for you?"
- Make the analogy engaging, memorable, and relevant for a {personalization_context['user_level']} learner.
- Optionally, use examples from everyday life, hobbies, or common experiences."""
        
        analogy = self.ai_service.get_response(system_prompt, user_prompt)
        
        # Store analogy in memory for Step 2 access
        if analogy:
            self.current_analogy = analogy
            self.current_topic = topic
        
        return analogy

    def _save_step1_attempt(self, interaction_id: str, analogy: str, personalization_context: dict, regeneration_count: int, user_understood: Optional[bool]):
        """Saves a single Step 1 analogy attempt to the database."""
        # Simplified reading time and comprehension for API version
        reading_time = 10 # Placeholder
        comprehension_indicator = "pending"

        analogy_data = {
            "interaction_id": interaction_id,
            "analogy_presented": analogy,
            "reading_time": reading_time,
            "comprehension_indicator": comprehension_indicator,
            "personalization_used": json.dumps(personalization_context),
            "user_level": personalization_context['user_level'],
            "previous_concepts": json.dumps(personalization_context['previous_concepts']),
            "regeneration_attempt": regeneration_count,
            "user_understood": user_understood,
            "timestamp": datetime.now().isoformat()
        }
        
        # Generate unique ID for this analogy attempt
        analogy_id = f"analogy_{interaction_id}_{regeneration_count}_{int(time.time())}"
        add_document("step1_analogies", analogy_data, analogy_id)

    def _generate_regenerated_analogy(self, topic: str, personalization_context: dict, used_analogies: list) -> str:
        """Generate a different analogy when user doesn't understand the previous one."""
        system_prompt = """You are an expert SQL instructor who explains concepts using vivid, creative analogies and also guides learners to reflect metacognitively. Keep explanations concise, engaging, and clear for beginners. Always follow your analogy with 1-2 reflection questions prompting the learner to think about how the analogy relates to their prior knowledge or experiences.

Your main goal is to generate a COMPLETELY NEW analogy because the user did not understand the previous ones.

You MUST follow these rules:
1.  Your new analogy MUST be on a different topic. For example, if the user saw a 'bakery' analogy, you could use 'library', 'space mission', 'gardening', etc.
2.  DO NOT repeat concepts or metaphors from the previous attempts.
3.  Be clear, concise, and do not include any technical jargon or SQL code."""
        
        previous_explanations = "\\n".join([f"- {analogy[:80]}..." for analogy in used_analogies])
        
        user_prompt = f"""The user needs a new analogy for the SQL concept: "{topic}".

They have already seen the following explanations and did not understand them:
{previous_explanations}

Please generate a fresh, completely different analogy that avoids the topics and ideas used above.

- Avoid SQL syntax or code.
- Keep the explanation under 120 words.
- After the analogy, include 1-2 metacognitive reflection questions, for example:
    • "Does this analogy connect to something you've experienced?"
    • "Can you explain this idea back in your own words?"
    • "What part of this analogy makes the concept clearer for you?"
- Make the analogy engaging, memorable, and relevant for a {personalization_context['user_level']} learner.
- Optionally, use examples from everyday life, hobbies, or common experiences."""
        
        print(f"\\n[DEBUG] Prompt sent to AI for regeneration:\\n---\\n{user_prompt}\\n---\\n")
        
        analogy = self.ai_service.get_response(system_prompt, user_prompt, temperature=0.8)
        
        # Store regenerated analogy in memory for Step 2 access
        if analogy:
            self.current_analogy = analogy
            self.current_topic = topic
        
        return analogy

    def generate_dynamic_schema_gpt(self, topic: str) -> Optional[Dict]:
        """Generate dynamic schema using GPT-4-mini for Step 3 tasks."""
        
        # Ensure topic safety
        safe_topic = topic.strip() if topic and topic.strip() else "SQL"
        
        # Pre-defined real-life scenarios for maximum diversity
        scenarios = [
            # Technology & Digital
            {"domain": "Video Streaming Platform", "tables": ["Movies", "Users", "Subscriptions"], "context": "Netflix-like streaming service"},
            {"domain": "Social Media Platform", "tables": ["Posts", "Users", "Comments"], "context": "Instagram/Facebook-like platform"},
            {"domain": "E-learning Platform", "tables": ["Courses", "Students", "Enrollments"], "context": "Online education system"},
            {"domain": "Gaming Platform", "tables": ["Games", "Players", "Achievements"], "context": "Steam-like gaming platform"},
            {"domain": "Music Streaming", "tables": ["Songs", "Artists", "Playlists"], "context": "Spotify-like music service"},
            
            # Healthcare & Fitness
            {"domain": "Hospital Management", "tables": ["Patients", "Doctors", "Appointments"], "context": "Hospital management system"},
            {"domain": "Fitness Tracking", "tables": ["Workouts", "Users", "Exercises"], "context": "Fitness app like MyFitnessPal"},
            {"domain": "Pharmacy Chain", "tables": ["Medications", "Customers", "Prescriptions"], "context": "Pharmacy management system"},
            {"domain": "Dental Clinic", "tables": ["Patients", "Dentists", "Treatments"], "context": "Dental practice management"},
            
            # Food & Restaurant
            {"domain": "Food Delivery", "tables": ["Restaurants", "Orders", "Customers"], "context": "UberEats-like delivery service"},
            {"domain": "Recipe Platform", "tables": ["Recipes", "Chefs", "Ingredients"], "context": "Cooking recipe sharing site"},
            {"domain": "Restaurant Chain", "tables": ["Locations", "Menu_Items", "Staff"], "context": "Multi-location restaurant management"},
            {"domain": "Food Truck Network", "tables": ["Food_Trucks", "Events", "Menu_Items"], "context": "Food truck coordination system"},
            
            # Travel & Transportation
            {"domain": "Flight Booking", "tables": ["Flights", "Passengers", "Bookings"], "context": "Airline reservation system"},
            {"domain": "Hotel Booking", "tables": ["Hotels", "Guests", "Reservations"], "context": "Hotel management system"},
            {"domain": "Car Rental", "tables": ["Vehicles", "Customers", "Rentals"], "context": "Car rental service"},
            {"domain": "Ride Sharing", "tables": ["Drivers", "Riders", "Trips"], "context": "Uber-like ride sharing"},
            {"domain": "Cruise Management", "tables": ["Ships", "Passengers", "Cabins"], "context": "Cruise line management"},
            
            # Retail & E-commerce
            {"domain": "Online Marketplace", "tables": ["Products", "Sellers", "Orders"], "context": "Amazon-like marketplace"},
            {"domain": "Fashion Retailer", "tables": ["Clothing_Items", "Customers", "Orders"], "context": "Fashion e-commerce site"},
            {"domain": "Electronics Store", "tables": ["Products", "Customers", "Warranties"], "context": "Electronics retailer"},
            {"domain": "Book Publishing", "tables": ["Books", "Authors", "Publishers"], "context": "Publishing house management"},
            
            # Entertainment & Events
            {"domain": "Concert Venue", "tables": ["Concerts", "Artists", "Tickets"], "context": "Concert hall management"},
            {"domain": "Movie Theater", "tables": ["Movies", "Screenings", "Customers"], "context": "Cinema management system"},
            {"domain": "Event Planning", "tables": ["Events", "Venues", "Bookings"], "context": "Event management company"},
            {"domain": "Sports League", "tables": ["Teams", "Players", "Matches"], "context": "Professional sports league"},
            {"domain": "Art Gallery", "tables": ["Artworks", "Artists", "Exhibitions"], "context": "Art gallery management"},
            
            # Financial & Business
            {"domain": "Banking System", "tables": ["Accounts", "Customers", "Transactions"], "context": "Bank management system"},
            {"domain": "Insurance Company", "tables": ["Policies", "Customers", "Claims"], "context": "Insurance management"},
            {"domain": "Real Estate", "tables": ["Properties", "Agents", "Sales"], "context": "Real estate management"},
            {"domain": "Stock Trading", "tables": ["Stocks", "Traders", "Trades"], "context": "Stock trading platform"},
            
            # Education & Research
            {"domain": "University System", "tables": ["Students", "Professors", "Courses"], "context": "University management system"},
            {"domain": "Library Management", "tables": ["Books", "Members", "Loans"], "context": "Public library system"},
            {"domain": "Research Lab", "tables": ["Projects", "Researchers", "Publications"], "context": "Scientific research lab"},
            {"domain": "Online Tutoring", "tables": ["Tutors", "Students", "Sessions"], "context": "Online tutoring platform"},
            
            # Agriculture & Environment
            {"domain": "Farm Management", "tables": ["Crops", "Farmers", "Harvests"], "context": "Agricultural management system"},
            {"domain": "Zoo Management", "tables": ["Animals", "Keepers", "Exhibits"], "context": "Zoo management system"},
            {"domain": "Weather Monitoring", "tables": ["Stations", "Readings", "Locations"], "context": "Weather tracking system"},
            
            # Logistics & Supply Chain
            {"domain": "Shipping Company", "tables": ["Packages", "Customers", "Deliveries"], "context": "Package delivery service"},
            {"domain": "Warehouse Management", "tables": ["Products", "Locations", "Inventory"], "context": "Warehouse management system"},
            {"domain": "Manufacturing", "tables": ["Products", "Workers", "Production_Lines"], "context": "Manufacturing plant management"}
        ]
        
        # Randomly select a scenario
        import random
        selected_scenario = random.choice(scenarios)
        
        # Determine table count based on topic
        is_join_topic = any(join_word in safe_topic.upper() for join_word in ['JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL'])
        table_count = "2 to 3" if is_join_topic else "1 to 2"
        
        system_prompt = f"""You are an expert SQL database designer creating a schema for a {selected_scenario['domain']} system.

Context: {selected_scenario['context']}

Generate a realistic database schema for teaching {safe_topic} concepts in this specific business context.

CRITICAL REQUIREMENTS:
- Generate between {table_count} tables
- Each table must have 4-8 columns
- Use the suggested table names as inspiration: {selected_scenario['tables']}
- Column types: INT, VARCHAR, DECIMAL, DATE, BOOLEAN, CHAR
- Include primary keys (usually ending with _id)
- For multi-table schemas: include foreign keys to establish relationships
- Make column names descriptive and professional for this industry
- Ensure the schema naturally supports {safe_topic} queries

Return ONLY valid JSON with this EXACT structure (no additional text):
{{
  "schema": {{
    "TableName1": [
      {{"column": "column_name", "type": "SQL_TYPE", "desc": "Brief description"}},
      {{"column": "another_column", "type": "SQL_TYPE", "desc": "Brief description"}}
    ],
    "TableName2": [
      {{"column": "column_name", "type": "SQL_TYPE", "desc": "Brief description"}}
    ]
  }},
  "concept_focus": "Brief description of what {safe_topic} concept this schema teaches"
}}"""
        
        user_prompt = f"""Create a SQL database schema for a {selected_scenario['domain']} ({selected_scenario['context']}).

Specific Requirements:
- Generate between {table_count} tables
- Each table has 4–8 columns
- Focus on the {selected_scenario['domain']} business domain
- Consider using table names like: {', '.join(selected_scenario['tables'])}
- Make it realistic for this specific industry
- Ensure the schema naturally supports {safe_topic} operations

Output JSON in this exact format:
{{
  "schema": {{
    "TableName": [
      {{"column": "col_name", "type": "col_type", "desc": "col_description"}}
    ]
  }},
  "concept_focus": "Brief description of what {safe_topic} concept this schema teaches in {selected_scenario['domain']}"
}}"""
        
        try:
            response = self.ai_service.get_response(system_prompt, user_prompt)
            if response:
                return json.loads(response)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error generating schema with GPT: {e}")
            return None
        
        return None

    # GPT task generation method removed - using simple static template instead

    def get_step1_analogy_for_step2(self, topic: str) -> str:
        """
        Get Step 1 analogy for Step 2 use. First checks memory, then falls back to Firestore.
        Returns empty string if no analogy is found.
        """
        # First, try to get from memory
        if self.current_analogy and self.current_topic == topic:
            print(f"[DEBUG] Retrieved analogy from memory for topic: {topic}")
            return self.current_analogy
            
        # Fallback to Firestore lookup
        print(f"[DEBUG] Analogy not in memory, trying Firestore lookup for topic: {topic}")
        if self.session_id:
            try:
                # First, find the Step 1 interaction for this session
                step_interactions = list_collection("step_interactions")
                step1_interaction = None
                
                for interaction in step_interactions:
                    if (interaction.get("session_id") == self.session_id and 
                        interaction.get("step_number") == 1):
                        step1_interaction = interaction
                        break
                
                if step1_interaction:
                    interaction_id = step1_interaction.get("id")
                    
                    # Find the most recent analogy for this interaction
                    analogies = list_collection("step1_analogies")
                    latest_analogy = None
                    
                    for analogy in analogies:
                        if analogy.get("interaction_id") == interaction_id:
                            latest_analogy = analogy
                            break
                    
                    if latest_analogy:
                        analogy_text = latest_analogy.get("analogy_presented", "")
                        # Store in memory for future use
                        self.current_analogy = analogy_text
                        self.current_topic = topic
                        print(f"[DEBUG] Retrieved analogy from Firestore and stored in memory")
                        return analogy_text
                        
            except Exception as e:
                print(f"[DEBUG] Firestore lookup failed: {e}")
                
        print(f"[DEBUG] No analogy found in memory or Firestore")
        return ""

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

    def _get_step2_system_prompt(self, topic: str) -> str:
        """Generate concept-appropriate system prompt for Step 2 questions."""
        base_json_structure = """{
  "scenario": "Brief description of the business context",
  "tables": {
    "table_name": [
      {"column1": "value1", "column2": "value2"},
      {"column1": "value3", "column2": "value4"}
    ]
  },
  "query": "SELECT ... FROM table_name ...",
  "options": {
    "correct": "The actual correct answer result",
    "wrong1": "First incorrect option", 
    "wrong2": "Second incorrect option",
    "wrong3": "Third incorrect option"
  },
  "correct": "correct"
}"""

        common_requirements = """Requirements:
- Use realistic business scenarios (e-commerce, library, restaurant, etc.)
- Create 4-5 rows in the table with diverse data
- Create 4 distinct multiple choice options
- Include one obviously wrong option, one tricky option, and one correct option
- Make sure only one option is completely correct
- Put the correct answer in the "correct" key and wrong answers in "wrong1", "wrong2", "wrong3"
- Set the "correct" field to "correct" (will be randomized later)
- IMPORTANT: Make sure the SQL query is syntactically correct"""

        if topic == "SELECT & FROM":
            return f"""You are an expert SQL educator creating prediction questions for students learning basic SELECT and FROM statements.

Create a realistic scenario with ONE table and a multiple-choice question about the output of a basic SELECT query.

Your response must be valid JSON with this exact structure:
{base_json_structure}

{common_requirements}
- Use ONLY SELECT and FROM clauses - NO JOINs, WHERE, ORDER BY, or other advanced concepts
- Focus on selecting specific columns or using SELECT * 
- The query should demonstrate basic data retrieval from a single table
- Examples: "SELECT name, age FROM students" or "SELECT * FROM products" """

        elif topic == "WHERE":
            return f"""You are an expert SQL educator creating prediction questions for students learning WHERE clauses.

Create a realistic scenario with ONE table and a multiple-choice question about the output of a SELECT query with WHERE conditions.

Your response must be valid JSON with this exact structure:
{base_json_structure}

{common_requirements}
- Use SELECT, FROM, and WHERE clauses only - NO JOINs, ORDER BY, or other advanced concepts
- Focus on filtering data with WHERE conditions (=, >, <, >=, <=, !=, LIKE, IN, etc.)
- The query should demonstrate how WHERE filters the result set
- Examples: "SELECT * FROM products WHERE price > 100" or "SELECT name FROM students WHERE age >= 18" """

        elif topic == "ORDER BY":
            return f"""You are an expert SQL educator creating prediction questions for students learning ORDER BY clauses.

Create a realistic scenario with ONE table and a multiple-choice question about the output of a SELECT query with ORDER BY.

Your response must be valid JSON with this exact structure:
{base_json_structure}

{common_requirements}
- Use SELECT, FROM, and ORDER BY clauses (optionally WHERE) - NO JOINs or other advanced concepts
- Focus on sorting data with ORDER BY (ASC, DESC)
- The query should demonstrate how ORDER BY changes the order of results
- Examples: "SELECT * FROM products ORDER BY price DESC" or "SELECT name, age FROM students ORDER BY age ASC" """

        else:  # For JOIN concepts and other advanced topics
            multi_table_structure = """{
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
}"""
            return f"""You are an expert SQL educator creating prediction questions for students learning {topic}.

Create a realistic scenario with multiple tables and a multiple-choice question about the output of a SQL query using {topic}.

Your response must be valid JSON with this exact structure:
{multi_table_structure}

Requirements:
- Use realistic business scenarios (e-commerce, library, restaurant, etc.)
- Create 3-4 rows per table with some matching and non-matching data
- Make the JOIN condition clear and logical
- Create 4 distinct multiple choice options
- Include one obviously wrong option, one tricky option, and one correct option
- Make sure only one option is completely correct
- Put the correct answer in the "correct" key and wrong answers in "wrong1", "wrong2", "wrong3"
- Set the "correct" field to "correct" (will be randomized later)
- IMPORTANT: Make sure the SQL query is syntactically correct and only references tables that are actually JOINed in the FROM clause
- Do not use WHERE clauses that reference tables not included in the JOIN"""

    def _generate_step2_question(self, topic: str, step_1_context: str) -> Optional[Dict]:
        """Generate a dynamic Step 2 question using GPT with improved prompts."""
        
        # Check if we have a Step 1 analogy to reference
        analogy_context = self.get_step1_analogy_for_step2(topic)
        
        # Create improved system prompt for GPT-4-mini
        system_prompt = """You are an expert SQL instructor creating multiple-choice questions for beginner learners. Your goal is to generate a single, clear MCQ that tests understanding of the given SQL concept.

Requirements:
- Create exactly 4 answer choices (A, B, C, D)
- Make the question under 50 words
- Include realistic sample data and a clear SQL query
- Only one answer should be completely correct
- Make it suitable for beginners learning the concept
- If an analogy is provided, you may optionally reference it to maintain learning consistency

Return your response as valid JSON with this exact structure:
{
  "scenario": "Brief business context",
  "query": "SELECT ... FROM ... (actual SQL query)",
  "tables": {
    "table_name": [
      {"column1": "value1", "column2": "value2"},
      {"column1": "value3", "column2": "value4"}
    ]
  },
  "options": {
    "A": "First option",
    "B": "Second option", 
    "C": "Third option",
    "D": "Fourth option"
  },
  "correct": "B"
}"""

        # Create context-aware user prompt
        analogy_reference = f"\n\nStep 1 Analogy Context: {analogy_context}" if analogy_context else ""
        
        user_prompt = f"""Create a multiple-choice question for the SQL concept: {topic}

Focus on testing basic understanding of {topic} for beginners.
The question should be clear, concise (under 50 words), and have exactly 4 choices with one correct answer.

Use realistic sample data and ensure the SQL query demonstrates {topic} clearly.{analogy_reference}

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
        options = question_data.get('options', {})
        
        # Check if we already have A, B, C, D format (new GPT output)
        if 'A' in options and 'B' in options and 'C' in options and 'D' in options:
            # Already in the correct format, just randomize the positions
            option_texts = [options['A'], options['B'], options['C'], options['D']]
            correct_key = question_data.get('correct', 'A')
            correct_text = options[correct_key]
            
            # Shuffle the option texts
            random.shuffle(option_texts)
            
            # Reassign to A, B, C, D
            option_keys = ['A', 'B', 'C', 'D']
            randomized_options = {}
            new_correct_key = None
            
            for i, text in enumerate(option_texts):
                key = option_keys[i]
                randomized_options[key] = text
                if text == correct_text:
                    new_correct_key = key
            
            # Update the question data
            question_data['options'] = randomized_options
            question_data['correct'] = new_correct_key
            
        else:
            # Handle old format (fallback questions)
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
        
        if topic == "SELECT & FROM":
            fallback_data = {
                "scenario": "Student Grade Database",
                "tables": {
                    "students": [
                        {"student_id": 1, "name": "Alice", "major": "Computer Science", "gpa": 3.8},
                        {"student_id": 2, "name": "Bob", "major": "Mathematics", "gpa": 3.2},
                        {"student_id": 3, "name": "Charlie", "major": "Physics", "gpa": 3.9},
                        {"student_id": 4, "name": "Diana", "major": "Computer Science", "gpa": 3.5}
                    ]
                },
                "query": "SELECT name, major FROM students",
                "options": {
                    "correct": "Alice-Computer Science, Bob-Mathematics, Charlie-Physics, Diana-Computer Science",
                    "wrong1": "All student data with GPA",
                    "wrong2": "Only student names",
                    "wrong3": "Alice, Bob, Charlie"
                },
                "correct": "correct"
            }
            
        elif topic == "WHERE":
            fallback_data = {
                "scenario": "Product Inventory System",
                "tables": {
                    "products": [
                        {"product_id": 1, "name": "Laptop", "price": 999, "category": "Electronics"},
                        {"product_id": 2, "name": "Book", "price": 25, "category": "Education"},
                        {"product_id": 3, "name": "Phone", "price": 599, "category": "Electronics"},
                        {"product_id": 4, "name": "Desk", "price": 150, "category": "Furniture"}
                    ]
                },
                "query": "SELECT name, price FROM products WHERE price > 100",
                "options": {
                    "correct": "Laptop-999, Phone-599, Desk-150",
                    "wrong1": "All products with their prices",
                    "wrong2": "Laptop-999, Phone-599",
                    "wrong3": "Book-25, Desk-150"
                },
                "correct": "correct"
            }
            
        elif topic == "ORDER BY":
            fallback_data = {
                "scenario": "Employee Salary Database",
                "tables": {
                    "employees": [
                        {"emp_id": 1, "name": "John", "salary": 50000, "department": "IT"},
                        {"emp_id": 2, "name": "Sarah", "salary": 75000, "department": "Finance"},
                        {"emp_id": 3, "name": "Mike", "salary": 45000, "department": "HR"},
                        {"emp_id": 4, "name": "Lisa", "salary": 80000, "department": "IT"}
                    ]
                },
                "query": "SELECT name, salary FROM employees ORDER BY salary DESC",
                "options": {
                    "correct": "Lisa-80000, Sarah-75000, John-50000, Mike-45000",
                    "wrong1": "John-50000, Sarah-75000, Mike-45000, Lisa-80000",
                    "wrong2": "Mike-45000, John-50000, Sarah-75000, Lisa-80000",
                    "wrong3": "All employees in random order"
                },
                "correct": "correct"
            }
            
        else:  # For JOIN concepts and other advanced topics
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

    def _save_step2_attempt(self, interaction_id: str, attempt_number: int, user_answer: str, correct_answer: str, is_correct: bool) -> None:
        """Save a single Step 2 attempt."""
        attempt_data = {
            "interaction_id": interaction_id,
            "attempt_number": attempt_number,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "timestamp": datetime.now().isoformat()
        }
        
        # Generate unique ID for this attempt
        attempt_id = f"attempt_{interaction_id}_{attempt_number}_{int(time.time())}"
        add_document("step2_attempts", attempt_data, attempt_id)

    def _save_step2_session(self, interaction_id: str, question_data: Dict, result: Dict) -> None:
        """Save the complete Step 2 session data."""
        session_data = {
            "interaction_id": interaction_id,
            "question_data": json.dumps(question_data),
            "total_attempts": result['attempts'],
            "questions_tried": result['questions_tried'],
            "final_success": result['final_correct'],
            "total_time": result['total_time'],
            "timestamp": datetime.now().isoformat()
        }
        
        # Generate unique ID for this session
        session_id = f"session_{interaction_id}_{int(time.time())}"
        add_document("step2_sessions", session_data, session_id)

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
            attempt_data = {
                "interaction_id": interaction_id,
                "attempt_number": attempt_number,
                "query_text": query_text,
                "syntax_valid": analysis['syntax_valid'],
                "error_type": analysis.get('error_type'),
                "error_message": analysis.get('error_message'),
                "time_since_start": int(time.time() - query_writing_start),
                "char_count": len(query_text),
                "word_count": len(query_text.split()),
                "timestamp": datetime.now().isoformat()
            }
            
            # Generate unique ID for this query attempt
            attempt_id = f"query_{interaction_id}_{attempt_number}_{int(time.time())}"
            add_document("query_attempts", attempt_data, attempt_id)
            
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
        explanation_data = {
            "interaction_id": interaction_id,
            "explanation_text": explanation_text,
            "word_count": len(explanation_text.split()),
            "concepts_mentioned": json.dumps(explanation_analysis['concepts_mentioned']),
            "clarity_score": explanation_analysis['clarity_score'],
            "accuracy_score": explanation_analysis['accuracy_score'],
            "writing_time": int(explanation_time),
            "timestamp": datetime.now().isoformat()
        }
        
        # Generate unique ID for this explanation
        explanation_id = f"explanation_{interaction_id}_{int(time.time())}"
        add_document("step3_explanations", explanation_data, explanation_id)
        
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
        concept_id = concept.upper().replace(" ", "_")
        mastery_doc_id = f"{self.user_id}_{concept_id}"
        
        # Get current mastery
        mastery_doc = get_document("concept_mastery", mastery_doc_id)
        
        if mastery_doc:
            current_mastery = mastery_doc.get('mastery_level', 0.0)
            total_attempts = mastery_doc.get('total_attempts', 0)
            successful_attempts = mastery_doc.get('successful_attempts', 0)
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
        mastery_data = {
            "user_id": self.user_id,
            "concept_id": concept_id,
            "mastery_level": new_mastery,
            "total_attempts": new_total,
            "successful_attempts": new_successful,
            "last_updated": datetime.now().isoformat()
        }
        
        update_document("concept_mastery", mastery_doc_id, mastery_data)
        
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
        """Select challenge difficulty using Step 3 score mapping."""
        if self.step3_score is not None:
            if self.step3_score >= 70:
                return "HARD"    # 70-100 points → Hard
            elif self.step3_score >= 50:
                return "MEDIUM"  # 50-69 points → Medium  
            else:
                return "EASY"    # 0-49 points → Easy

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

    def _generate_step4_challenge(self, topic: str, difficulty: str, user_concepts: List[str]) -> Dict:
        """Generate a dynamic Step 4 challenge based on difficulty level and user's learning progress."""
        
        # Get user's learning progress to determine available concepts
        user_progress = self._get_user_learning_progress()
        available_concepts = self._get_available_concepts(user_progress, topic)
        
        # Define concept-specific requirements based on curriculum roadmap
        concept_specs = self._get_concept_specific_specs(topic, available_concepts)
        
        # Define difficulty-specific requirements (adjusted for user's level and concept restrictions)
        # For early concepts (SELECT/FROM, WHERE, ORDER BY), always use single table
        max_tables_for_level = 1 if self._map_topic_to_concept_id(topic) in ['select-from', 'where', 'order-by'] else 2
        
        difficulty_specs = {
            "EASY": {
                "complexity": "basic",
                "tables": max_tables_for_level,
                "concepts": f"focus ONLY on {topic} using {', '.join(available_concepts)}",
                "description": "Practice basic SQL concepts with straightforward queries"
            },
            "MEDIUM": {
                "complexity": "intermediate", 
                "tables": max_tables_for_level,
                "concepts": f"apply {topic} using ONLY {', '.join(available_concepts)}",
                "description": "Apply SQL concepts to solve real-world scenarios"
            },
            "HARD": {
                "complexity": "advanced",
                "tables": max_tables_for_level,
                "concepts": f"master {topic} using ONLY {', '.join(available_concepts)}",
                "description": "Master SQL challenges within your learning scope"
            }
        }
        
        spec = difficulty_specs.get(difficulty, difficulty_specs["MEDIUM"])
        
        # Use concept-specific customizations if available
        final_spec = {**spec, **concept_specs}
        
        system_prompt = f"""You are an expert SQL educator creating coding challenges for students.

🚨 CRITICAL RESTRICTION 🚨
This student has ONLY learned these concepts: {', '.join(available_concepts)}

ABSOLUTE PROHIBITIONS:
- DO NOT use JOIN, INNER JOIN, LEFT JOIN, RIGHT JOIN if not in the allowed list
- DO NOT use COUNT, SUM, AVG, GROUP BY, HAVING if not in the allowed list  
- DO NOT use subqueries, CASE statements, or any advanced concepts not listed
- If student is learning SELECT/FROM, use ONLY single table queries with SELECT and FROM
- STICK STRICTLY to the allowed concepts list

Create a realistic, {final_spec['complexity']} SQL challenge that tests ONLY {topic} using ONLY the allowed concepts.

Your response must be valid JSON with this exact structure:
{{
  "title": "Challenge Title",
  "difficulty": "{difficulty}",
  "description": "Clear problem description",
  "scenario": "Business context and background",
  "schema": {{
    "table1_name": [
      {{"column": "column_name", "type": "data_type", "description": "what this column represents"}}
    ],
    "table2_name": [
      {{"column": "column_name", "type": "data_type", "description": "what this column represents"}}
    ]
  }},
  "sample_data": {{
    "table1_name": [
      {{"col1": "value1", "col2": "value2"}},
      {{"col1": "value3", "col2": "value4"}}
    ],
    "table2_name": [
      {{"col1": "valueA", "col2": "valueB"}},
      {{"col1": "valueC", "col2": "valueD"}}
    ]
  }},
  "task": "Specific task description with clear expected output",
  "expected_concepts": ["{topic}", "additional_concept1", "additional_concept2"],
  "hints": [
    "Helpful hint 1",
    "Helpful hint 2"
  ]
}}

Requirements:
- Use realistic business scenarios (e-commerce, HR, library, etc.)
- Create {spec['tables']} tables with logical relationships
- Make the challenge appropriately {difficulty.lower()} difficulty
- Include sample data that makes the expected output clear
- Ensure the task requires using {topic}
- Provide helpful hints without giving away the complete solution"""

        user_prompt = f"""Create a {difficulty.lower()} SQL challenge for the concept: {topic}

🎯 STRICT CURRICULUM CONTEXT:
- Student's ONLY allowed concepts: {', '.join(available_concepts)}
- Current learning level: {topic}
- Challenge type: {final_spec.get('challenge_type', 'general')}
- Maximum tables allowed: {final_spec.get('max_tables', 1)}

📋 MANDATORY REQUIREMENTS:
- Use EXCLUSIVELY the concepts: {', '.join(available_concepts)}
- Create a {final_spec.get('complexity_limit', final_spec['complexity'])} level challenge
- Choose scenario from: {', '.join(final_spec.get('sample_scenarios', ['single table scenario']))}
- Focus ONLY on {topic}

🚫 ABSOLUTE RESTRICTIONS (MUST FOLLOW):
- If studying SELECT/FROM: Use ONLY single table with SELECT and FROM - NO JOIN, NO WHERE
- If studying WHERE: Use SELECT, FROM, WHERE - NO JOIN, NO aggregates
- If studying ORDER BY: Use SELECT, FROM, WHERE, ORDER BY - NO JOIN, NO aggregates
- NEVER exceed the allowed concepts list
- NEVER assume student knows concepts not in the allowed list

EXAMPLE for SELECT/FROM level:
- Schema: One simple table (e.g., products, students, books)
- Task: "Select specific columns from the table"
- NO relationships between tables, NO complex conditions

Return only valid JSON, no additional text."""

        try:
            response = self.ai_service.get_response(system_prompt, user_prompt)
            if response:
                challenge_data = json.loads(response)
                # Add metadata
                challenge_data["generated_for_score"] = self.step3_score
                challenge_data["user_concepts"] = user_concepts
                return challenge_data
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error generating Step 4 challenge: {e}")
            return self._get_fallback_step4_challenge(difficulty, topic)

    def _get_user_learning_progress(self) -> List[str]:
        """Get user's completed concepts from Firestore or default to basic concepts."""
        try:
            # Get all roadmap progress documents
            progress_docs = list_collection("roadmap_progress")
            
            # Filter for this user's progress
            user_progress = [
                doc.get("concept_id") for doc in progress_docs
                if doc.get("user_id") == self.user_id and doc.get("concept_id")
            ]
            
            if user_progress:
                return user_progress
            
        except Exception as e:
            print(f"Error getting user progress: {e}")
        
        # Default to early concepts if no progress found
        return ['select-from']

    def _get_available_concepts(self, user_progress: List[str], current_topic: str) -> List[str]:
        """Get available SQL concepts based on curriculum roadmap and user progress."""
        
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
        current_topic_mapped = self._map_topic_to_concept_id(current_topic)
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

    def _map_topic_to_concept_id(self, topic: str) -> str:
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

    def _get_concept_specific_specs(self, topic: str, available_concepts: List[str]) -> Dict:
        """Get concept-specific challenge specifications based on learning level."""
        
        concept_id = self._map_topic_to_concept_id(topic)
        
        # Early concepts (Unit 1): Focus on fundamentals - SINGLE TABLE ONLY
        if concept_id in ['select-from', 'where', 'order-by']:
            return {
                'challenge_type': 'fundamental',
                'max_tables': 1,  # STRICT: Only single table for early concepts
                'concepts_focus': f"Practice {topic} with simple, single-table examples",
                'complexity_limit': 'basic',
                'sample_scenarios': [
                    'Single employee table queries',
                    'Student records (one table)', 
                    'Product catalog (one table)',
                    'Book inventory (one table)'
                ]
            }
        
        # JOIN concepts (Unit 2): Relationship understanding
        elif concept_id in ['inner-join', 'left-join', 'right-join']:
            return {
                'challenge_type': 'relational',
                'max_tables': 3,
                'concepts_focus': f"Practice {topic} to understand table relationships",
                'complexity_limit': 'intermediate',
                'sample_scenarios': [
                    'Customer orders and products',
                    'Students and their courses',
                    'Employees and departments',
                    'Authors and their books'
                ]
            }
        
        # Aggregation concepts (Unit 3): Data summarization
        elif concept_id in ['aggregates', 'group-by', 'having']:
            return {
                'challenge_type': 'analytical',
                'max_tables': 3,
                'concepts_focus': f"Practice {topic} for data analysis and summarization",
                'complexity_limit': 'intermediate',
                'sample_scenarios': [
                    'Sales performance analysis',
                    'Student grade statistics',
                    'Inventory management reports',
                    'Customer behavior analytics'
                ]
            }
        
        # Advanced concepts (Unit 4): Complex logic
        else:
            return {
                'challenge_type': 'advanced',
                'max_tables': 4,
                'concepts_focus': f"Practice {topic} with complex real-world scenarios",
                'complexity_limit': 'advanced',
                'sample_scenarios': [
                    'Multi-tier business analytics',
                    'Complex reporting systems',
                    'Advanced data transformations',
                    'Business intelligence queries'
                ]
            }

    def _get_fallback_step4_challenge(self, difficulty: str, topic: str) -> Dict:
        """Fallback challenge if GPT generation fails - adapted to user's learning level."""
        
        # Get user progress and available concepts
        user_progress = self._get_user_learning_progress()
        available_concepts = self._get_available_concepts(user_progress, topic)
        concept_id = self._map_topic_to_concept_id(topic)
        
        # Base challenge structure
        base_challenge = {
            "title": f"SQL Challenge - {difficulty} Level",
            "difficulty": difficulty,
            "description": f"Apply your {topic} knowledge to solve this challenge",
            "expected_concepts": available_concepts,
            "hints": [f"Focus on using {topic} correctly", "Take your time to understand the requirements"]
        }
        
        # Concept-specific fallback challenges
        if concept_id in ['select-from', 'where', 'order-by']:
            # Early concepts - Simple single table challenges
            base_challenge.update({
                "scenario": "Student Records Database",
                "schema": {
                    "students": [
                        {"column": "student_id", "type": "INT", "description": "Student ID"},
                        {"column": "name", "type": "VARCHAR", "description": "Student Name"},
                        {"column": "age", "type": "INT", "description": "Student Age"},
                        {"column": "grade", "type": "CHAR", "description": "Letter Grade"},
                        {"column": "gpa", "type": "DECIMAL", "description": "Grade Point Average"}
                    ]
                },
                "sample_data": {
                    "students": [
                        {"student_id": 1, "name": "Alice", "age": 20, "grade": "A", "gpa": 3.8},
                        {"student_id": 2, "name": "Bob", "age": 19, "grade": "B", "gpa": 3.2},
                        {"student_id": 3, "name": "Carol", "age": 21, "grade": "A", "gpa": 3.9}
                    ]
                }
            })
            
            if concept_id == 'select-from':
                base_challenge["task"] = "Write a query to select all student names and their GPAs from the students table."
            elif concept_id == 'where':
                base_challenge["task"] = "Write a query to find all students who have a GPA greater than 3.5."
            else:  # order-by
                base_challenge["task"] = "Write a query to list all students ordered by their GPA in descending order."
                
        elif concept_id in ['inner-join', 'left-join', 'right-join']:
            # JOIN concepts - Two table challenges
            base_challenge.update({
                "scenario": "Library Management System",
                "schema": {
                    "books": [
                        {"column": "book_id", "type": "INT", "description": "Book ID"},
                        {"column": "title", "type": "VARCHAR", "description": "Book Title"},
                        {"column": "author_id", "type": "INT", "description": "Author ID"}
                    ],
                    "authors": [
                        {"column": "author_id", "type": "INT", "description": "Author ID"},
                        {"column": "author_name", "type": "VARCHAR", "description": "Author Name"},
                        {"column": "country", "type": "VARCHAR", "description": "Author's Country"}
                    ]
                },
                "sample_data": {
                    "books": [
                        {"book_id": 1, "title": "SQL Basics", "author_id": 1},
                        {"book_id": 2, "title": "Data Science", "author_id": 2},
                        {"book_id": 3, "title": "Web Design", "author_id": 1}
                    ],
                    "authors": [
                        {"author_id": 1, "author_name": "John Smith", "country": "USA"},
                        {"author_id": 2, "author_name": "Mary Johnson", "country": "Canada"}
                    ]
                },
                "task": f"Write a query using {topic} to show book titles with their author names."
            })
            
        else:
            # Advanced concepts - Multi-table challenges
            base_challenge.update({
                "scenario": "E-commerce Sales System",
                "schema": {
                    "orders": [
                        {"column": "order_id", "type": "INT", "description": "Order ID"},
                        {"column": "customer_id", "type": "INT", "description": "Customer ID"},
                        {"column": "order_date", "type": "DATE", "description": "Order Date"},
                        {"column": "total_amount", "type": "DECIMAL", "description": "Total Amount"}
                    ],
                    "customers": [
                        {"column": "customer_id", "type": "INT", "description": "Customer ID"},
                        {"column": "customer_name", "type": "VARCHAR", "description": "Customer Name"},
                        {"column": "city", "type": "VARCHAR", "description": "Customer City"}
                    ]
                },
                "sample_data": {
                    "orders": [
                        {"order_id": 1, "customer_id": 1, "order_date": "2023-01-15", "total_amount": 150.00},
                        {"order_id": 2, "customer_id": 2, "order_date": "2023-01-16", "total_amount": 200.00},
                        {"order_id": 3, "customer_id": 1, "order_date": "2023-01-17", "total_amount": 75.00}
                    ],
                    "customers": [
                        {"customer_id": 1, "customer_name": "Alice Brown", "city": "New York"},
                        {"customer_id": 2, "customer_name": "Bob Wilson", "city": "Los Angeles"}
                    ]
                },
                "task": f"Write a query using {topic} to analyze customer order patterns."
            })
            
        return base_challenge

    def _save_step4_question(self, interaction_id: str, question_data: dict) -> str:
        """Save Step 4 question to Firestore and return question_id."""
        import uuid
        question_id = str(uuid.uuid4())
        
        try:
            # Prepare question document
            question_doc = {
                "question_id": question_id,
                "interaction_id": interaction_id,
                "question_data": json.dumps(question_data),
                "difficulty": question_data.get('difficulty', 'MEDIUM'),
                "step3_score": self.step3_score or 60,
                "timestamp": datetime.now().isoformat()
            }
            
            # Insert the question
            add_document("step4_questions", question_doc, question_id)
            return question_id
        except Exception as e:
            print(f"Error saving Step 4 question: {e}")
            return question_id

    def _save_step4_attempt(self, interaction_id: str, attempt_number: int, user_solution: str, 
                           feedback: str, is_correct: bool, feedback_type: str) -> None:
        """Save Step 4 attempt to Firestore."""
        try:
            # Prepare attempt document
            attempt_doc = {
                "interaction_id": interaction_id,
                "attempt_number": attempt_number,
                "user_solution": user_solution,
                "feedback": feedback,
                "is_correct": is_correct,
                "feedback_type": feedback_type,
                "timestamp": datetime.now().isoformat()
            }
            
            # Generate unique ID for this attempt
            attempt_id = f"attempt_{interaction_id}_{attempt_number}_{int(time.time())}"
            add_document("step4_attempts", attempt_doc, attempt_id)
        except Exception as e:
            print(f"Error saving Step 4 attempt: {e}")

    def _save_step4_session(self, interaction_id: str, question_data: dict, total_attempts: int, 
                           final_success: bool, total_time: int) -> None:
        """Save Step 4 session summary to Firestore."""
        try:
            # Prepare session document
            session_doc = {
                "interaction_id": interaction_id,
                "question_data": json.dumps(question_data),
                "total_attempts": total_attempts,
                "final_success": final_success,
                "total_time": total_time,
                "timestamp": datetime.now().isoformat()
            }
            
            # Generate unique ID for this session
            session_id = f"session_{interaction_id}_{int(time.time())}"
            add_document("step4_sessions", session_doc, session_id)
        except Exception as e:
            print(f"Error saving Step 4 session: {e}")

    def _generate_step4_feedback(self, user_solution: str, question_data: dict, overall_quality: str, evaluation: dict = None) -> str:
        """Generate AI-powered feedback for Step 4 solutions based on quality level."""
        
        task = question_data.get('task', 'SQL Challenge')
        expected_concepts = question_data.get('expected_concepts', [])
        difficulty = question_data.get('difficulty', 'MEDIUM')
        
        # Get quality level from evaluation or use passed parameter
        if not overall_quality:
            overall_quality = evaluation.get('overall_quality', 'FAIR') if evaluation else 'FAIR'
        correctness_level = evaluation.get('correctness_level', 'FAIR') if evaluation else 'FAIR'
        structure_level = evaluation.get('structure_level', 'FAIR') if evaluation else 'FAIR'
        
        # Generate feedback based on quality level
        if overall_quality == 'EXCELLENT':
            system_prompt = """You are an encouraging SQL tutor providing positive feedback for EXCELLENT solutions.

The student has achieved EXCELLENT quality. Provide feedback that:
1. Congratulates them enthusiastically on their perfect solution
2. Highlights specific strengths in their solution
3. Acknowledges their mastery of the concepts
4. Encourages continued learning

Be enthusiastic and specific. Keep your response to 3-4 sentences."""
            
            user_prompt = f"""The student solved this {difficulty.lower()} SQL challenge with EXCELLENT quality:

Task: {task}
Expected concepts: {', '.join(expected_concepts)}

Their solution:
{user_solution}

Quality Assessment: EXCELLENT (perfect solution with clear understanding)

Provide encouraging feedback highlighting what they did perfectly."""

        elif overall_quality == 'GOOD':
            system_prompt = """You are an encouraging SQL tutor providing positive feedback for GOOD solutions.

The student has achieved GOOD quality. Provide feedback that:
1. Congratulates them on their successful solution
2. Highlights what they did well
3. Mentions any minor areas for improvement if relevant
4. Encourages continued learning

Be positive and supportive. Keep your response to 3-4 sentences."""

            user_prompt = f"""The student solved this {difficulty.lower()} SQL challenge with GOOD quality:

Task: {task}
Expected concepts: {', '.join(expected_concepts)}

Their solution:
{user_solution}

Quality Assessment: GOOD (mostly correct with minor issues)

Provide encouraging feedback highlighting their success."""

        elif overall_quality == 'FAIR':
            system_prompt = """You are a helpful SQL tutor providing constructive feedback for FAIR solutions.

The student has achieved FAIR quality. Provide feedback that:
1. Acknowledges their effort and partial understanding
2. Explains specific areas that need improvement
3. Provides actionable suggestions for enhancement
4. Encourages them to refine their solution

Be supportive but honest about areas for improvement. Keep your response to 3-4 sentences."""

            user_prompt = f"""The student attempted this {difficulty.lower()} SQL challenge with FAIR quality:

Task: {task}
Expected concepts: {', '.join(expected_concepts)}

Their solution:
{user_solution}

Quality Assessment: FAIR (basic understanding but has noticeable errors or missing elements)

Provide constructive feedback focusing on areas for improvement."""

        elif overall_quality == 'POOR':
            system_prompt = """You are a helpful SQL tutor providing constructive feedback for POOR solutions.

The student has achieved POOR quality. Provide feedback that:
1. Acknowledges their effort
2. Explains major areas that need improvement
3. Provides clear, actionable suggestions
4. Encourages them to review concepts and try again

Be supportive but clear about what needs to be fixed. Keep your response to 3-4 sentences."""

            user_prompt = f"""The student attempted this {difficulty.lower()} SQL challenge with POOR quality:

Task: {task}
Expected concepts: {', '.join(expected_concepts)}

Their solution:
{user_solution}

Quality Assessment: POOR (major errors or fundamental misunderstanding)

Provide constructive feedback focusing on fundamental issues that need to be addressed."""

        else:  # This shouldn't happen with the new system, but keep for safety
            system_prompt = """You are a helpful SQL tutor providing hints for SQL challenges.

Provide a specific hint that guides the student toward the correct solution without giving the answer away.
Focus on the approach or concept they should consider."""

            user_prompt = f"""The student is struggling with this {difficulty.lower()} SQL challenge:

Task: {task}
Expected concepts: {', '.join(expected_concepts)}

Their solution:
{user_solution}

Provide a helpful hint to guide them toward the correct solution."""

        try:
            response = self.ai_service.get_response(system_prompt, user_prompt)
            ai_feedback = response if response else f"Keep working on your {difficulty.lower()} SQL solution!"
            
            return ai_feedback
        except Exception as e:
            print(f"Error generating Step 4 feedback: {e}")
            return f"Good effort! Keep working on your SQL solution based on the {overall_quality.lower()} quality level."

    def _evaluate_step4_solution(self, user_solution: str, question_data: dict) -> dict:
        """Evaluate Step 4 solution using detailed grading rubric."""
        
        task = question_data.get('task', 'SQL Challenge')
        expected_concepts = question_data.get('expected_concepts', [])
        difficulty = question_data.get('difficulty', 'MEDIUM')
        
        # Phase 1: Get basic correctness evaluation
        correctness_evaluation = self._evaluate_solution_correctness(user_solution, question_data)
        
        # Phase 2: Get code structure evaluation
        structure_evaluation = self._evaluate_code_structure(user_solution)
        
        # Phase 3: Calculate scores based on rubric
        scores = self._calculate_step4_scores(correctness_evaluation, structure_evaluation, difficulty)
        
        # Phase 4: Determine if solution is acceptable
        is_correct = scores['total_score'] >= 35  # Minimum passing threshold
        
        # Combine all evaluations
        return {
            "is_correct": is_correct,
            "correctness_score": scores['correctness_score'],
            "structure_score": scores['structure_score'],
            "bonus_score": scores['bonus_score'],
            "total_score": scores['total_score'],
            "max_possible_score": scores['max_possible_score'],
            "correctness_level": correctness_evaluation.get('correctness_level', 'fair'),
            "structure_level": structure_evaluation.get('structure_level', 'fair'),
            "concepts_used": correctness_evaluation.get('concepts_used', []),
            "missing_concepts": correctness_evaluation.get('missing_concepts', []),
            "syntax_errors": correctness_evaluation.get('syntax_errors', []),
            "logic_errors": correctness_evaluation.get('logic_errors', []),
            "structure_feedback": structure_evaluation.get('feedback', []),
            "suggestions": correctness_evaluation.get('suggestions', []),
            "detailed_breakdown": {
                "correctness": f"{scores['correctness_score']}/35 points",
                "structure": f"{scores['structure_score']}/15 points",
                "bonus": f"+{scores['bonus_score']} points",
                "total": f"{scores['total_score']}/{scores['max_possible_score']} points"
            }
        }

    def _evaluate_solution_correctness(self, user_solution: str, question_data: dict) -> dict:
        """Evaluate solution correctness with improved 4-level grading."""
        
        task = question_data.get('task', 'SQL Challenge')
        expected_concepts = question_data.get('expected_concepts', [])
        difficulty = question_data.get('difficulty', 'MEDIUM')
        
        system_prompt = """You are an expert SQL instructor evaluating solution correctness with a 4-level grading system.

Analyze the SQL solution and classify correctness into one of four levels:

- EXCELLENT: Query is 100% correct, perfectly formatted, produces exactly the expected output, demonstrates clear understanding. The query must be COMPLETE and FUNCTIONAL.
- GOOD: Query is mostly correct (90-99%), produces the expected output with minor formatting issues or very small inefficiencies
- FAIR: Query is correct but has noticeable errors, syntax issues, or logic problems that affect execution or output quality (70-89% correct)
- POOR: Query has major errors, won't execute correctly, produces wrong output, or shows fundamental misunderstanding (<70% correct)

**CRITICAL RULES:**
- INCOMPLETE queries (missing SELECT, FROM, WHERE, semicolons, etc.) cannot receive EXCELLENT grade
- SYNTAX ERRORS immediately disqualify from EXCELLENT grade
- LOGICAL ERRORS or wrong results cannot be EXCELLENT

**Guidelines for simple queries (SELECT...FROM...WHERE):**
- EXCELLENT: Perfect syntax, proper column selection, correct WHERE conditions, well-formatted, AND COMPLETE
- GOOD: Minor formatting issues but logically sound and executable
- FAIR: Works but has syntax errors, missing elements, or logic issues
- POOR: Major problems that prevent execution or produce wrong results

Return JSON with this exact structure:
{
  "correctness_level": "EXCELLENT" | "GOOD" | "FAIR" | "POOR",
  "confidence": float (0.0 to 1.0),
  "concepts_used": [list of SQL concepts identified],
  "missing_concepts": [list of expected concepts not used],
  "syntax_errors": [list of syntax issues if any],
  "logic_errors": [list of logical issues if any],
  "suggestions": [list of improvement suggestions],
  "works_correctly": boolean,
  "output_accuracy": float (0.0 to 1.0),
  "quality_explanation": "Brief explanation of why this grade was assigned"
}"""

        user_prompt = f"""Evaluate this SQL solution for correctness:

Task: {task}
Expected concepts: {', '.join(expected_concepts)}
Difficulty: {difficulty}

Student solution:
{user_solution}

Focus on whether the query would work correctly and produce the expected output. Be generous with EXCELLENT ratings for solutions that correctly solve the problem, even if simple."""

        try:
            response = self.ai_service.get_response(system_prompt, user_prompt)
            if response:
                evaluation = json.loads(response)
                return evaluation
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error evaluating solution correctness: {e}")
        
        # Fallback evaluation
        return {
            "correctness_level": "FAIR",
            "confidence": 0.5,
            "concepts_used": [],
            "missing_concepts": expected_concepts,
            "syntax_errors": [],
            "logic_errors": ["Unable to evaluate solution"],
            "suggestions": ["Please check your SQL syntax and try again"],
            "works_correctly": False,
            "output_accuracy": 0.5,
            "quality_explanation": "Evaluation failed, defaulting to FAIR"
        }

    def _evaluate_code_structure(self, user_solution: str) -> dict:
        """Evaluate code structure quality with improved 4-level grading."""
        
        system_prompt = """You are an expert SQL instructor evaluating code structure and formatting with a 4-level grading system.

Analyze the SQL code structure and classify into one of four levels:

- EXCELLENT: Perfect formatting, proper indentation, each SQL clause on its own line, clear structure, readable and professional
- GOOD: Well-structured code with minor formatting issues, mostly follows best practices, readable
- FAIR: Basic structure present but has formatting issues, inconsistent spacing/indentation, acceptable but could improve
- POOR: Poor structure, everything on one line or confusing layout, hard to read, needs significant improvement

**Guidelines for simple queries (SELECT...FROM...WHERE):**
- EXCELLENT: Perfect formatting with proper line breaks and indentation
- GOOD: Decent structure with minor formatting issues
- FAIR: Basic structure but needs formatting improvement
- POOR: Poor or no formatting structure

Return JSON with this exact structure:
{
  "structure_level": "EXCELLENT" | "GOOD" | "FAIR" | "POOR",
  "has_proper_linebreaks": boolean,
  "has_proper_indentation": boolean,
  "follows_sql_guidelines": boolean,
  "readability_score": float (0.0 to 1.0),
  "feedback": [list of specific structure feedback],
  "suggestions": [list of structure improvement suggestions],
  "structure_explanation": "Brief explanation of why this grade was assigned"
}"""

        user_prompt = f"""Evaluate this SQL code structure:

{user_solution}

Focus on formatting, line breaks, indentation, and overall code organization. Be generous with EXCELLENT ratings for well-formatted simple queries."""

        try:
            response = self.ai_service.get_response(system_prompt, user_prompt)
            if response:
                evaluation = json.loads(response)
                return evaluation
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error evaluating code structure: {e}")
        
        # Fallback evaluation based on simple heuristics
        has_linebreaks = '\n' in user_solution
        has_keywords_on_lines = any(keyword in user_solution.upper() for keyword in ['SELECT', 'FROM', 'WHERE', 'JOIN'])
        
        if has_linebreaks and has_keywords_on_lines:
            structure_level = "GOOD"  # More generous fallback
            readability_score = 0.6
        elif has_linebreaks:
            structure_level = "FAIR"
            readability_score = 0.4
        else:
            structure_level = "POOR"
            readability_score = 0.2
            
        return {
            "structure_level": structure_level,
            "has_proper_linebreaks": has_linebreaks,
            "has_proper_indentation": False,
            "follows_sql_guidelines": has_keywords_on_lines,
            "readability_score": readability_score,
            "feedback": ["Consider adding line breaks for better readability"],
            "suggestions": ["Break long queries into multiple lines", "Use proper indentation"],
            "structure_explanation": f"Structure evaluation failed, defaulting to {structure_level} based on simple heuristics"
        }

    def _calculate_step4_scores(self, correctness_eval: dict, structure_eval: dict, difficulty: str) -> dict:
        """Calculate final scores based on improved 4-level grading rubric."""
        
        # Correctness scoring (35 points) - New 4-level system
        correctness_level = correctness_eval.get('correctness_level', 'FAIR')
        if correctness_level == 'EXCELLENT':
            correctness_score = 35
        elif correctness_level == 'GOOD':
            correctness_score = 32  # 91% of 35
        elif correctness_level == 'FAIR':
            correctness_score = 25  # 71% of 35
        else:  # POOR
            correctness_score = 0
            
        # Structure scoring (15 points) - Updated to match new system
        structure_level = structure_eval.get('structure_level', 'FAIR')
        if structure_level == 'EXCELLENT':
            structure_score = 15
        elif structure_level == 'GOOD':
            structure_score = 13  # 87% of 15
        elif structure_level == 'FAIR':
            structure_score = 10  # 67% of 15
        else:  # POOR
            structure_score = 0
            
        # Difficulty-based bonus scoring - Updated for new system
        bonus_score = 0
        step3_score = getattr(self, 'step3_score', 60)
        
        # Check if hints were used (temporary logic - will be improved when hint tracking is implemented)
        hints_used = False  # For now, assume no hints were used - will be updated in future
        
        if difficulty == 'EASY' and step3_score < 50:
            # Bonus +10 points if completed without hints
            if correctness_level in ['EXCELLENT', 'GOOD'] and not hints_used:
                bonus_score = 10
        elif difficulty == 'MEDIUM':
            # Bonus +5 points if completed without hints
            if correctness_level in ['EXCELLENT', 'GOOD'] and not hints_used:
                bonus_score = 5
        elif difficulty == 'HARD' and step3_score >= 80:
            # Bonus +15 points if solved optimally without hints
            if correctness_level == 'EXCELLENT' and structure_level in ['EXCELLENT', 'GOOD'] and not hints_used:
                bonus_score = 15
        
        total_score = correctness_score + structure_score + bonus_score
        
        # Calculate max possible score based on difficulty
        if difficulty == 'EASY' and step3_score < 50:
            max_possible_score = 50 + 10  # 60 total
        elif difficulty == 'MEDIUM':
            max_possible_score = 50 + 5   # 55 total
        elif difficulty == 'HARD' and step3_score >= 80:
            max_possible_score = 50 + 15  # 65 total
        else:
            max_possible_score = 50       # 50 total (standard)
        
        # Determine overall quality level based on correctness and structure
        # If correctness is POOR, overall is POOR regardless of structure
        if correctness_level == 'POOR':
            overall_quality = 'POOR'
        # If correctness is FAIR, overall is at most FAIR
        elif correctness_level == 'FAIR':
            overall_quality = 'FAIR'
        # If correctness is GOOD or EXCELLENT, consider structure
        elif correctness_level == 'GOOD':
            # GOOD correctness can be downgraded by poor structure
            if structure_level == 'POOR':
                overall_quality = 'FAIR'
            else:
                overall_quality = 'GOOD'
        else:  # correctness_level == 'EXCELLENT'
            # EXCELLENT correctness can be downgraded by poor structure
            if structure_level == 'POOR':
                overall_quality = 'GOOD'
            elif structure_level == 'FAIR':
                overall_quality = 'GOOD'
            else:
                overall_quality = 'EXCELLENT'
        
        return {
            'correctness_score': correctness_score,
            'structure_score': structure_score,
            'bonus_score': bonus_score,
            'total_score': total_score,
            'max_possible_score': max_possible_score,
            'difficulty': difficulty,
            'step3_score': step3_score,
            'correctness_level': correctness_level,
            'structure_level': structure_level,
            'overall_quality': overall_quality
        }

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
        
        # Calculate session metrics from Firestore
        step_interactions = list_collection("step_interactions")
        session_interactions = [
            interaction for interaction in step_interactions
            if interaction.get("session_id") == self.session_id
        ]
        
        total_steps = len(session_interactions)
        successful_steps = sum(1 for interaction in session_interactions if interaction.get("success"))
        total_duration = sum(interaction.get("duration", 0) for interaction in session_interactions if interaction.get("duration"))
        
        # Calculate learning efficiency
        concepts_attempted = [self.concept_id] if self.concept_id else []
        learning_efficiency = successful_steps / total_steps if total_steps > 0 else 0
        
        # Update session
        update_document("learning_sessions", self.session_id, {
            "session_end": datetime.now().isoformat(),
            "total_duration": total_session_time,
            "completed": True
        })
        
        # Store learning analytics
        analytics_data = {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "concepts_attempted": json.dumps(concepts_attempted),
            "learning_efficiency": learning_efficiency,
            "engagement_score": 0.85,  # Simplified engagement score
            "timestamp": datetime.now().isoformat()
        }
        
        analytics_id = f"analytics_{self.session_id}_{int(time.time())}"
        add_document("learning_analytics", analytics_data, analytics_id)
        
        # Display session summary
        print(f"\n📈 Enhanced Session Summary:")
        print(f"   📚 Concept: {self.concept_id}")
        print(f"   ⏱️  Total Time: {total_session_time//60}m {total_session_time%60}s")
        print(f"   🎯 Steps Completed: {total_steps}")
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