"""
Query submission model for storing SQL queries and execution context
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from src.core.database import Base


class QuerySubmission(Base):
    """SQL query submission entity"""
    
    __tablename__ = "query_submissions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to student
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True)
    
    # Query content
    query_text = Column(Text, nullable=False)
    query_hash = Column(String(64), nullable=False, index=True)  # For caching and deduplication
    
    # Submission context
    chapter_context = Column(String(100), nullable=True)
    exercise_id = Column(String(100), nullable=True)
    learning_objective = Column(String(200), nullable=True)
    
    # Execution metadata
    execution_time_ms = Column(Integer, nullable=True)
    rows_returned = Column(Integer, nullable=True)
    syntax_valid = Column(Boolean, nullable=True)
    execution_successful = Column(Boolean, nullable=True)
    
    # Analysis status
    analysis_completed = Column(Boolean, default=False)
    analysis_requested_at = Column(DateTime(timezone=True), nullable=True)
    
    # Learning context (stored as JSON)
    submission_context = Column(JSONB, nullable=True)  # Additional context data
    user_intent = Column(Text, nullable=True)  # What the student was trying to accomplish
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", backref="query_submissions")
    
    def __repr__(self):
        return f"<QuerySubmission(id={self.id}, student_id={self.student_id})>" 