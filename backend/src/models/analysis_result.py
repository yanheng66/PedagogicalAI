"""
Analysis result model for storing SQL query analysis outcomes
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Float, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from src.core.database import Base


class AnalysisResult(Base):
    """SQL query analysis result entity"""
    
    __tablename__ = "analysis_results"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to query submission
    query_submission_id = Column(UUID(as_uuid=True), ForeignKey("query_submissions.id"), nullable=False, index=True)
    
    # Analysis metadata
    analysis_type = Column(String(50), nullable=False)  # quick, llm, hybrid
    analysis_version = Column(String(20), default="1.0")
    processing_time_ms = Column(Integer, nullable=False)
    
    # Syntax and structure analysis
    syntax_errors = Column(JSONB, default=[])      # List of syntax errors
    logical_errors = Column(JSONB, default=[])     # List of logical issues
    performance_issues = Column(JSONB, default=[]) # Performance concerns
    
    # Educational insights
    concepts_used = Column(JSONB, default=[])      # SQL concepts identified
    difficulty_level = Column(String(20), nullable=True)
    complexity_score = Column(Float, nullable=True)
    educational_feedback = Column(Text, nullable=True)
    
    # Improvement suggestions
    suggestions = Column(JSONB, default=[])        # Structured suggestions
    alternative_approaches = Column(JSONB, default=[])  # Different ways to solve
    learning_opportunities = Column(JSONB, default=[])  # What student can learn
    
    # Quality metrics
    code_quality_score = Column(Float, nullable=True)
    readability_score = Column(Float, nullable=True)
    efficiency_score = Column(Float, nullable=True)
    
    # LLM specific data
    llm_model_used = Column(String(100), nullable=True)
    llm_prompt_tokens = Column(Integer, nullable=True)
    llm_completion_tokens = Column(Integer, nullable=True)
    llm_confidence_score = Column(Float, nullable=True)
    
    # Analysis context and results
    analysis_context = Column(JSONB, nullable=True)  # Context used for analysis
    raw_analysis_output = Column(Text, nullable=True)  # Raw LLM output
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    query_submission = relationship("QuerySubmission", backref="analysis_results")
    
    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, query_submission_id={self.query_submission_id})>" 