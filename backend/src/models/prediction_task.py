"""
Prediction task model for prediction-based learning activities
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from src.core.database import Base


class PredictionTask(Base):
    """Prediction task entity for learning activities"""
    
    __tablename__ = "prediction_tasks"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to student
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True)
    
    # Task content
    query_to_predict = Column(Text, nullable=False)
    database_schema = Column(JSONB, nullable=False)  # Table structures and sample data
    expected_result = Column(JSONB, nullable=False)  # Correct prediction result
    
    # Task metadata
    difficulty_level = Column(String(20), nullable=False)
    concepts_tested = Column(JSONB, default=[])
    learning_objectives = Column(JSONB, default=[])
    estimated_time_minutes = Column(Integer, nullable=True)
    
    # Student interaction
    student_prediction = Column(JSONB, nullable=True)  # Student's prediction
    prediction_submitted_at = Column(DateTime(timezone=True), nullable=True)
    time_spent_seconds = Column(Integer, nullable=True)
    
    # Evaluation results
    is_correct = Column(Boolean, nullable=True)
    accuracy_score = Column(Float, nullable=True)  # 0.0 - 1.0
    feedback_provided = Column(Text, nullable=True)
    evaluation_details = Column(JSONB, nullable=True)
    
    # Learning impact
    concepts_reinforced = Column(JSONB, default=[])
    misconceptions_identified = Column(JSONB, default=[])
    follow_up_recommendations = Column(JSONB, default=[])
    
    # Task status
    status = Column(String(20), default="assigned")  # assigned, in_progress, completed, skipped
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", backref="prediction_tasks")
    
    def __repr__(self):
        return f"<PredictionTask(id={self.id}, student_id={self.student_id}, status={self.status})>" 