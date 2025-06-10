"""
Hint request model for tracking student hint usage and effectiveness
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from src.core.database import Base


class HintRequest(Base):
    """Hint request entity for tracking hint usage"""
    
    __tablename__ = "hint_requests"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True)
    query_submission_id = Column(UUID(as_uuid=True), ForeignKey("query_submissions.id"), nullable=True, index=True)
    
    # Hint request details
    hint_level = Column(Integer, nullable=False)  # 1-4 levels
    hint_type = Column(String(50), nullable=False)  # concept, syntax, logic, complete
    requested_context = Column(JSONB, nullable=True)  # Context provided by student
    
    # Generated hint content
    hint_content = Column(Text, nullable=False)
    hint_generation_time_ms = Column(Integer, nullable=True)
    llm_model_used = Column(String(100), nullable=True)
    
    # Cost and usage
    coins_spent = Column(Integer, nullable=False, default=0)
    is_free_hint = Column(Boolean, default=False)  # First hint or other free conditions
    
    # Effectiveness tracking
    was_helpful = Column(Boolean, nullable=True)  # Student feedback
    helpfulness_score = Column(Integer, nullable=True)  # 1-5 rating
    student_feedback = Column(Text, nullable=True)
    
    # Follow-up analysis
    led_to_solution = Column(Boolean, nullable=True)
    time_to_solution_after_hint = Column(Integer, nullable=True)  # seconds
    additional_hints_needed = Column(Integer, default=0)
    
    # Learning impact
    concepts_clarified = Column(JSONB, default=[])
    learning_progress_impact = Column(String(20), nullable=True)  # positive, neutral, negative
    
    # Hint personalization data
    student_learning_style = Column(String(50), nullable=True)
    adapted_to_preferences = Column(Boolean, default=False)
    personalization_factors = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    responded_at = Column(DateTime(timezone=True), nullable=True)
    feedback_submitted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    student = relationship("Student", backref="hint_requests")
    query_submission = relationship("QuerySubmission", backref="hint_requests")
    
    def __repr__(self):
        return f"<HintRequest(id={self.id}, student_id={self.student_id}, level={self.hint_level})>" 