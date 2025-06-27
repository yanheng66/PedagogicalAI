from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, func

from database import Base

# ---------------------------------------------------------------------------
# Simplified models for initial testing
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    user_id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    level = Column(String(20), default="Beginner")
    created_at = Column(DateTime, default=func.now())
    last_active = Column(DateTime, onupdate=func.now())
    total_learning_time = Column(Integer, default=0)
    preferred_language = Column(String(10), default="en")


class Concept(Base):
    __tablename__ = "concepts"

    concept_id = Column(String(50), primary_key=True)
    concept_name = Column(String(100), nullable=False)
    category = Column(String(50))
    difficulty_base = Column(Integer)
    prerequisites = Column(JSON)
    estimated_time = Column(Integer)
    description = Column(String)


class LearningSession(Base):
    __tablename__ = "learning_sessions"

    session_id = Column(String(50), primary_key=True)
    user_id = Column(String(50), ForeignKey("users.user_id"))
    concept_id = Column(String(50), ForeignKey("concepts.concept_id"))
    session_start = Column(DateTime, default=func.now())
    session_end = Column(DateTime)
    completed = Column(Boolean, default=False)
    total_duration = Column(Integer)
    mastery_before = Column(Float)
    mastery_after = Column(Float)
    device_type = Column(String(20))
    ip_address = Column(String(45))


class ConceptMastery(Base):
    __tablename__ = "concept_mastery"

    mastery_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey("users.user_id"))
    concept_id = Column(String(50), ForeignKey("concepts.concept_id"))
    mastery_level = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    total_attempts = Column(Integer, default=0)
    successful_attempts = Column(Integer, default=0)
    retention_score = Column(Float, default=0.0)


class StepInteraction(Base):
    __tablename__ = "step_interactions"

    interaction_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(50), ForeignKey("learning_sessions.session_id"))
    step_number = Column(Integer, nullable=False)
    start_time = Column(DateTime, default=func.now())
    end_time = Column(DateTime)
    duration = Column(Integer)
    success = Column(Boolean)
    metadata = Column(JSON) 