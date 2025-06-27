from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship

from database import Base

# ---------------------------------------------------------------------------
# Core tables (MVP)
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    user_id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    level = Column(String(20), default="Beginner")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True), onupdate=func.now())
    total_learning_time = Column(Integer, default=0)
    preferred_language = Column(String(10), default="en")

    sessions = relationship("LearningSession", back_populates="user")


class Concept(Base):
    __tablename__ = "concepts"

    concept_id = Column(String(50), primary_key=True)
    concept_name = Column(String(100), nullable=False)
    category = Column(String(50))
    difficulty_base = Column(Integer)
    prerequisites = Column(JSON)  # Changed from JSONB to JSON for SQLite compatibility
    estimated_time = Column(Integer)
    description = Column(String)

    sessions = relationship("LearningSession", back_populates="concept")


class LearningSession(Base):
    __tablename__ = "learning_sessions"

    session_id = Column(String(50), primary_key=True)
    user_id = Column(String(50), ForeignKey("users.user_id"))
    concept_id = Column(String(50), ForeignKey("concepts.concept_id"))
    session_start = Column(DateTime(timezone=True), server_default=func.now())
    session_end = Column(DateTime(timezone=True))
    completed = Column(Boolean, default=False)
    total_duration = Column(Integer)
    mastery_before = Column(Float)
    mastery_after = Column(Float)
    device_type = Column(String(20))
    ip_address = Column(String(45))

    user = relationship("User", back_populates="sessions")
    concept = relationship("Concept", back_populates="sessions")
    interactions = relationship("StepInteraction", back_populates="session")


class ConceptMastery(Base):
    __tablename__ = "concept_mastery"

    mastery_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey("users.user_id"))
    concept_id = Column(String(50), ForeignKey("concepts.concept_id"))

    mastery_level = Column(Float, default=0.0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    total_attempts = Column(Integer, default=0)
    successful_attempts = Column(Integer, default=0)
    retention_score = Column(Float, default=0.0)


class StepInteraction(Base):
    __tablename__ = "step_interactions"

    interaction_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(50), ForeignKey("learning_sessions.session_id"))
    step_number = Column(Integer, nullable=False)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True))
    duration = Column(Integer)
    success = Column(Boolean)
    metadata = Column(JSON)  # Changed from JSONB to JSON for SQLite compatibility

    session = relationship("LearningSession", back_populates="interactions")


class Step3Error(Base):
    __tablename__ = "step3_errors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey("users.user_id"))
    concept = Column(String(100), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Raw user SQL query
    user_query = Column(String, nullable=False)
    # Store the full GPT analysis JSON as text for flexibility
    error_analysis = Column(String, nullable=False)

    attempts = Column(Integer, nullable=False)
    time_spent_seconds = Column(Integer, nullable=False)
    hints_used = Column(Integer, default=0)
    final_success = Column(Boolean, nullable=False)


class Step4Error(Base):
    __tablename__ = "step4_errors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey("users.user_id"))
    concept = Column(String(100), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    problem_description = Column(String, nullable=False)
    included_concepts = Column(String, nullable=False)  # JSON string
    difficulty = Column(String(20), nullable=False)  # 'easy' | 'medium' | 'hard'

    user_solution = Column(String, nullable=False)
    error_analysis = Column(String, nullable=False)  # Full GPT analysis JSON

    attempts = Column(Integer, nullable=False)
    final_success = Column(Boolean, nullable=False) 