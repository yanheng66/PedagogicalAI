"""
Concept model for SQL learning concepts and their relationships
"""

from sqlalchemy import Column, String, Text, ForeignKey, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from src.core.database import Base


class Concept(Base):
    """SQL concept entity"""
    
    __tablename__ = "concepts"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Concept identification
    name = Column(String(100), unique=True, nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)  # basic, intermediate, advanced
    
    # Concept details
    description = Column(Text, nullable=True)
    learning_objectives = Column(JSONB, default=[])
    keywords = Column(JSONB, default=[])
    
    # Hierarchy and dependencies
    parent_concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id"), nullable=True)
    difficulty_level = Column(Integer, default=1)  # 1-10 scale
    prerequisite_concepts = Column(JSONB, default=[])  # List of concept IDs
    
    # Educational metadata
    estimated_learning_time_minutes = Column(Integer, nullable=True)
    practice_exercises_available = Column(Boolean, default=False)
    has_video_content = Column(Boolean, default=False)
    has_interactive_examples = Column(Boolean, default=False)
    
    # Content references
    documentation_url = Column(String(500), nullable=True)
    example_queries = Column(JSONB, default=[])
    common_errors = Column(JSONB, default=[])
    
    # Tracking and analytics
    total_students_attempted = Column(Integer, default=0)
    average_mastery_time_hours = Column(Integer, nullable=True)
    common_misconceptions = Column(JSONB, default=[])
    
    # Status
    is_active = Column(Boolean, default=True)
    is_deprecated = Column(Boolean, default=False)
    
    # Relationships
    parent_concept = relationship("Concept", remote_side=[id], backref="child_concepts")
    
    def __repr__(self):
        return f"<Concept(id={self.id}, name={self.name})>" 