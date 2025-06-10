"""
Student-related schemas for API requests and responses
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime


class StudentCreate(BaseModel):
    """Schema for creating a new student"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    learning_goals: Optional[Dict[str, Any]] = None


class StudentResponse(BaseModel):
    """Schema for student response data"""
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    current_level: str = "beginner"
    total_coins: int = 0
    concepts_mastered: int = 0
    total_practice_time: int = 0  # in minutes
    streak_days: int = 0
    created_at: datetime
    last_active: Optional[datetime] = None


class StudentProfile(BaseModel):
    """Detailed student profile schema"""
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    current_level: str
    total_coins: int
    
    # Learning Statistics
    concepts_mastered: int
    total_concepts: int
    overall_progress: float = Field(..., ge=0.0, le=1.0)
    total_practice_time: int
    streak_days: int
    
    # Performance Metrics
    average_accuracy: float = Field(..., ge=0.0, le=1.0)
    recent_performance: float = Field(..., ge=0.0, le=1.0)
    learning_velocity: float  # concepts per week
    
    # Learning Preferences
    preferred_difficulty: str = "adaptive"
    preferred_hint_level: str = "adaptive"
    learning_style: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    last_active: Optional[datetime] = None


class StudentUpdate(BaseModel):
    """Schema for updating student information"""
    full_name: Optional[str] = None
    learning_goals: Optional[Dict[str, Any]] = None
    preferred_difficulty: Optional[str] = None
    preferred_hint_level: Optional[str] = None
    learning_style: Optional[str] = None


class LearningPathResponse(BaseModel):
    """Schema for learning path API response"""
    path_id: str
    student_id: str
    current_concept: str
    next_concepts: list[str]
    progress_percentage: float = Field(..., ge=0.0, le=100.0)
    estimated_completion_days: int
    last_updated: datetime 