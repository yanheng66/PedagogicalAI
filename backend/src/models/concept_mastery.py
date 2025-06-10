"""
Concept mastery model for tracking student understanding of SQL concepts
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from src.core.database import Base


class ConceptMastery(Base):
    """Student concept mastery tracking entity"""
    
    __tablename__ = "concept_mastery"
    
    # Composite primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True)
    concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id"), nullable=False, index=True)
    
    # Mastery metrics
    mastery_level = Column(Float, nullable=False, default=0.0)  # 0.0 - 1.0 scale
    confidence_score = Column(Float, nullable=True)             # Bayesian confidence
    mastery_status = Column(String(20), default="not_started")  # not_started, learning, mastered, expert
    
    # Learning evidence
    total_attempts = Column(Integer, default=0)
    successful_attempts = Column(Integer, default=0)
    recent_performance = Column(JSONB, default=[])  # Last N attempts with scores
    
    # Time tracking
    total_study_time_minutes = Column(Integer, default=0)
    first_exposure_at = Column(DateTime(timezone=True), nullable=True)
    mastery_achieved_at = Column(DateTime(timezone=True), nullable=True)
    last_practice_at = Column(DateTime(timezone=True), nullable=True)
    
    # Learning patterns
    learning_velocity = Column(Float, nullable=True)    # Rate of improvement
    retention_rate = Column(Float, nullable=True)       # Knowledge retention over time
    error_patterns = Column(JSONB, default=[])          # Common mistakes for this concept
    
    # Adaptive learning data
    recommended_practice_frequency = Column(String(20), nullable=True)  # daily, weekly, etc
    next_review_due = Column(DateTime(timezone=True), nullable=True)
    difficulty_adjustment = Column(Float, default=0.0)  # -1.0 to 1.0 for easier/harder content
    
    # Evidence and context
    mastery_evidence = Column(JSONB, default=[])        # Evidence supporting mastery level
    learning_context = Column(Text, nullable=True)      # Context when concept was learned
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    student = relationship("Student")
    concept = relationship("Concept")
    
    def __repr__(self):
        return f"<ConceptMastery(student_id={self.student_id}, concept_id={self.concept_id}, level={self.mastery_level})>" 