"""
Learning profile model for storing student learning analytics and preferences
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from src.core.database import Base


class LearningProfile(Base):
    """Student learning profile with analytics and preferences"""
    
    __tablename__ = "learning_profiles"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to student
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True)
    
    # Learning analytics stored as JSON
    concept_mastery_map = Column(JSONB, nullable=True)  # Concept -> mastery level mapping
    learning_patterns = Column(JSONB, nullable=True)    # Behavioral patterns analysis
    performance_metrics = Column(JSONB, nullable=True)  # Performance statistics
    error_patterns = Column(JSONB, nullable=True)       # Common error analysis
    
    # Learning preferences
    preferred_hint_level = Column(String(20), default="adaptive")  # adaptive, minimal, detailed
    learning_pace = Column(String(20), default="normal")           # slow, normal, fast
    preferred_feedback_style = Column(String(20), default="balanced") # encouraging, direct, balanced
    
    # Current learning state
    current_chapter = Column(String(100), nullable=True)
    current_difficulty_level = Column(String(20), default="beginner")
    active_learning_path = Column(Text, nullable=True)
    
    # Gamification data
    total_queries_submitted = Column(JSONB, default={})
    achievements_earned = Column(JSONB, default=[])
    streak_data = Column(JSONB, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", backref="learning_profile")
    
    def __repr__(self):
        return f"<LearningProfile(id={self.id}, student_id={self.student_id})>" 