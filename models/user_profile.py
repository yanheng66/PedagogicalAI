"""
Legacy user profile wrapper for backward compatibility with the new user modeling system.
"""

from typing import List, Dict, Any
from .user_modeling import UserModel


class UserProfile:
    """
    Legacy wrapper for backward compatibility.
    Provides simplified interface while using the new UserModel internally.
    """
    
    def __init__(self, name: str = "Alex", level: str = "Beginner", user_id: str = None):
        self.name = name
        self.level = level
        self.user_id = user_id or f"user_{hash(name)}"
        
        # Create internal UserModel instance
        self._user_model = UserModel(userId=self.user_id, name=name)
        
        # Legacy fields for backward compatibility
        self.learned_concepts: List[str] = []
        self.mastered_concepts: List[str] = []
        self.misconceptions: List[str] = []
        self.error_patterns: List[str] = []
    
    @property
    def strengths(self) -> List[str]:
        """Get strength areas from the user model."""
        return self._user_model.get_strength_areas()
    
    @property
    def focus_areas(self) -> List[str]:
        """Get focus areas from the user model."""
        return self._user_model.get_focus_areas()
    
    def get_user_model(self) -> UserModel:
        """Get the internal UserModel instance."""
        return self._user_model
    
    def update_user_model(self, user_model: UserModel) -> None:
        """Update the internal UserModel instance."""
        self._user_model = user_model
        self.learned_concepts = user_model.get_concept_progress()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user profile to dictionary format."""
        return {
            "name": self.name,
            "level": self.level,
            "user_id": self.user_id,
            "learned_concepts": self.learned_concepts,
            "mastered_concepts": self.mastered_concepts,
            "misconceptions": self.misconceptions,
            "error_patterns": self.error_patterns,
            "strengths": self.strengths,
            "focus_areas": self.focus_areas,
            "overall_mastery": self._user_model.get_overall_mastery_level(),
            "recent_performance": self._user_model.get_recent_performance(),
        }
    
    def update_from_grading_data(self, grading_data: Dict[str, Any]) -> None:
        """Legacy method for backward compatibility - simplified implementation."""
        if not grading_data:
            return
        
        # Update basic misconceptions and error patterns for legacy compatibility
        if "learning_profile_update" in grading_data:
            update_data = grading_data["learning_profile_update"]
            self.misconceptions.extend(update_data.get("add_to_misconceptions", []))
            self.error_patterns.extend(update_data.get("error_patterns", []))
        
        # Update learned concepts based on grading status
        if grading_data.get("submission_analysis", {}).get("query_status") == "CORRECT":
            concept = grading_data.get("concept_tracking", {}).get("concepts_attempted", [])
            if concept and concept[0]:
                self.add_learned_concept(concept[0])
                if concept[0] not in self.mastered_concepts:
                    self.mastered_concepts.append(concept[0])
    
    def add_learned_concept(self, concept: str) -> None:
        """Add a concept to the learned concepts list if not already present."""
        if concept not in self.learned_concepts:
            self.learned_concepts.append(concept) 