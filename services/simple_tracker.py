import uuid
from typing import Optional, Any, Dict

from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from database import get_db_session
from models.simple_models import (
    User,
    Concept,
    LearningSession,
    ConceptMastery,
    StepInteraction,
)


class SimpleTracker:
    """Simplified tracker service for testing."""

    def __init__(self):
        self.session_cache = {}

    @staticmethod
    def _default_id() -> str:
        """Generate a UUID4 string."""
        return str(uuid.uuid4())

    def start_concept(self, user_id: str, topic: str) -> str:
        """Initialize concept tracking and create a new learning session."""
        with get_db_session() as db:
            # Ensure user exists
            user = db.query(User).filter_by(user_id=user_id).first()
            if not user:
                user = User(user_id=user_id, name="Test User")
                db.add(user)
                db.commit()

            # Ensure concept exists
            concept_id = topic.upper().replace(" ", "_")
            concept = db.query(Concept).filter_by(concept_id=concept_id).first()
            if not concept:
                concept = Concept(concept_id=concept_id, concept_name=topic)
                db.add(concept)
                db.commit()

            # Get current mastery
            mastery = db.query(ConceptMastery).filter_by(
                user_id=user_id, concept_id=concept_id
            ).first()
            current_mastery = mastery.mastery_level if mastery else 0.0

            # Create session
            session_id = self._default_id()
            session = LearningSession(
                session_id=session_id,
                user_id=user_id,
                concept_id=concept_id,
                mastery_before=current_mastery,
            )
            db.add(session)
            db.commit()
            
            self.session_cache[session_id] = {
                'user_id': user_id,
                'concept_id': concept_id
            }
            
            return session_id

    def log_interaction(
        self,
        session_id: str,
        step_number: int,
        success: Optional[bool] = None,
        duration: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Create a StepInteraction row and return its id."""
        with get_db_session() as db:
            interaction = StepInteraction(
                session_id=session_id,
                step_number=step_number,
                success=success,
                duration=duration,
                metadata=metadata,
            )
            db.add(interaction)
            db.commit()
            return interaction.interaction_id 