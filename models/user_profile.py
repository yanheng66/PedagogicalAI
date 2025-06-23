"""
User profile data model for tracking learning progress.
"""

from typing import List, Dict, Any


class UserProfile:
    """Represents a user's learning profile and progress."""
    
    def __init__(self, name: str = "Alex", level: str = "Beginner"):
        self.name = name
        self.level = level
        self.learned_concepts: List[str] = []
        self.mastered_concepts: List[str] = []
        self.misconceptions: List[str] = []
        self.error_patterns: List[str] = []
        self.strengths: List[str] = []
        self.focus_areas: List[str] = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user profile to dictionary format."""
        return {
            "name": self.name,
            "level": self.level,
            "learned_concepts": self.learned_concepts,
            "mastered_concepts": self.mastered_concepts,
            "misconceptions": self.misconceptions,
            "error_patterns": self.error_patterns,
            "strengths": self.strengths,
            "focus_areas": self.focus_areas,
        }
    
    def update_from_grading_data(self, grading_data: Dict[str, Any]) -> None:
        """Update user profile based on grading feedback."""
        if not grading_data or "learning_profile_update" not in grading_data:
            return
            
        update_data = grading_data["learning_profile_update"]
        self.misconceptions.extend(update_data.get("add_to_misconceptions", []))
        self.error_patterns.extend(update_data.get("error_patterns", []))
        self.strengths.extend(update_data.get("strengths_identified", []))
        self.focus_areas.extend(update_data.get("recommended_focus", []))
        
        # Add mastered concepts
        if grading_data.get("submission_analysis", {}).get("query_status") == "CORRECT":
            concept = grading_data.get("concept_tracking", {}).get("concepts_attempted", [])
            if concept and concept[0] and concept[0] not in self.mastered_concepts:
                self.mastered_concepts.append(concept[0])
    
    def add_learned_concept(self, concept: str) -> None:
        """Add a concept to the learned concepts list if not already present."""
        if concept not in self.learned_concepts:
            self.learned_concepts.append(concept) 