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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user profile to dictionary format."""
        return {
            "name": self.name,
            "level": self.level,
            "learned_concepts": self.learned_concepts,
        }
    
    def update_from_grading_data(self, grading_data: Dict[str, Any]) -> None:
        """Simplified: no-op in minimal version."""
        return
    
    def add_learned_concept(self, concept: str) -> None:
        """Add a concept to the learned concepts list if not already present."""
        if concept not in self.learned_concepts:
            self.learned_concepts.append(concept) 