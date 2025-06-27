import uuid
from typing import Optional, Any, Dict

from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from database import get_db_session
from models.db_models import (
    User,
    Concept,
    LearningSession,
    ConceptMastery,
    StepInteraction,
)


class StudentTracker:
    """Service that handles user model triggers and logs interactions."""

    def __init__(self, db: Optional[Session] = None):
        # Allow manual session injection for tests. Otherwise open context manager.
        self._external_session = db is not None
        self.db = db or get_db_session().__enter__()

    # ---------------------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------------------
    @staticmethod
    def _default_id() -> str:
        """Generate a deterministic UUID4 string."""
        return str(uuid.uuid4())

    # ---------------------------------------------------------------------
    # High-level API mirroring spec in the design document
    # ---------------------------------------------------------------------

    def start_concept(self, user_id: str, topic: str) -> str:
        """Initialize concept tracking and create a new learning session.

        Returns the new session_id.
        """
        # Ensure user exists (for MVP we create if missing)
        user = self._get_or_create_user(user_id)

        # Ensure concept exists
        concept = self._get_or_create_concept(topic)

        session_id = self._default_id()
        session = LearningSession(
            session_id=session_id,
            user_id=user.user_id,
            concept_id=concept.concept_id,
            mastery_before=self._get_current_mastery(user.user_id, concept.concept_id),
        )
        self.db.add(session)
        self._commit()
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
        interaction = StepInteraction(
            session_id=session_id,
            step_number=step_number,
            success=success,
            duration=duration,
            metadata=metadata,
        )
        self.db.add(interaction)
        self._commit()
        return interaction.interaction_id

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_or_create_user(self, user_id: str) -> User:
        """Fetch existing user or create a placeholder."""
        try:
            user = self.db.query(User).filter_by(user_id=user_id).one()
        except NoResultFound:
            user = User(user_id=user_id, name="Anonymous")
            self.db.add(user)
            self._commit()
        return user

    def _get_or_create_concept(self, topic: str) -> Concept:
        cid = topic.upper().replace(" ", "_")
        try:
            concept = self.db.query(Concept).filter_by(concept_id=cid).one()
        except NoResultFound:
            concept = Concept(concept_id=cid, concept_name=topic)
            self.db.add(concept)
            self._commit()
        return concept

    def _get_current_mastery(self, user_id: str, concept_id: str) -> float:
        mastery = (
            self.db.query(ConceptMastery)
            .filter_by(user_id=user_id, concept_id=concept_id)
            .first()
        )
        return mastery.mastery_level if mastery else 0.0

    def _commit(self):
        if not self._external_session:
            # inside context manager, commit manually
            self.db.commit()

    # ------------------------------------------------------------------
    # Context manager support when created without external session
    # ------------------------------------------------------------------

    def close(self):
        if not self._external_session:
            self.db.close() 