"""
Learning-related schemas for the AI SQL Learning System
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


# Enums
class DifficultyLevel(str, Enum):
    """Difficulty levels for learning content"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ActivityType(str, Enum):
    """Types of learning activities"""
    QUERY_ANALYSIS = "query_analysis"
    PREDICTION_TASK = "prediction_task"
    CONCEPT_PRACTICE = "concept_practice"
    HINT_REQUEST = "hint_request"
    STREAK_BONUS = "streak_bonus"
    MILESTONE = "milestone_achievement"


# Learning Context and Activities
class LearningContext(BaseModel):
    """Context for learning activities"""
    student_level: str
    current_concepts: List[str]
    objectives: List[str]
    session_duration: Optional[int] = None
    recent_performance: Optional[float] = None


class LearningActivity(BaseModel):
    """Learning activity information"""
    activity_type: str
    description: str
    difficulty_level: str = "normal"
    concepts_involved: List[str] = []
    estimated_duration: Optional[int] = None


class PerformanceMetrics(BaseModel):
    """Performance metrics for learning activities"""
    overall_score: float = Field(..., ge=0.0, le=1.0)
    difficulty_multiplier: float = Field(default=1.0, ge=0.5, le=3.0)
    time_efficiency: Optional[float] = None
    streak_multiplier: Optional[float] = None
    current_difficulty_level: str = "beginner"


class PerformanceScore(BaseModel):
    """Detailed performance score with evidence"""
    score: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: Dict[str, Any]


# Concept Mastery
class ConceptMasteryMap(BaseModel):
    """Complete concept mastery map for a student"""
    student_id: str
    total_concepts: int
    mastered_concepts: int
    learning_concepts: int
    not_started_concepts: int
    overall_progress: float = Field(..., ge=0.0, le=1.0)
    concept_scores: Dict[str, Dict[str, Any]]
    last_updated: datetime


class MasteryUpdate(BaseModel):
    """Result of concept mastery update"""
    student_id: str
    concept: str
    old_mastery_level: float
    new_mastery_level: float
    confidence_change: float
    status_changed: bool
    new_status: str
    evidence: Dict[str, Any]


# Learning Paths
class LearningPath(BaseModel):
    """Adaptive learning path for a student"""
    student_id: str
    path_id: str
    target_objectives: List[str]
    concept_sequence: List[str]
    activities: List[Dict[str, Any]]
    estimated_duration_days: int
    difficulty_level: str
    created_at: datetime
    last_updated: datetime


class ActivityResult(BaseModel):
    """Result of completed learning activity"""
    student_id: str
    activity_type: str
    concept: str
    performance: PerformanceScore
    time_spent_seconds: int
    completed_at: datetime


class PathUpdate(BaseModel):
    """Update to learning path progress"""
    student_id: str
    completed_concept: str
    mastery_achieved: bool
    next_concept: Optional[str]
    path_completed: bool
    needs_adjustment: bool
    updated_at: datetime


class PathAdjustment(BaseModel):
    """Adjustment to learning path difficulty"""
    student_id: str
    adjustment_needed: bool
    old_difficulty: str
    new_difficulty: Optional[str]
    reason: Optional[str]
    performance_indicators: Dict[str, Any]
    adjusted_activities: List[Dict[str, Any]]
    adjusted_at: datetime


# Hints
class HintContext(BaseModel):
    """Context for hint generation"""
    problem_description: str
    current_query: Optional[str] = None
    error_message: Optional[str] = None
    student_level: str
    relevant_concepts: Optional[List[str]] = None
    database_schema: Optional[Dict[str, Any]] = None
    attempts_count: int = 0


class HintRequest(BaseModel):
    """Request for learning hint"""
    student_id: str
    level: int = Field(..., ge=0, le=4)  # 0 = auto-determine
    context: HintContext


class HintResponse(BaseModel):
    """Response containing generated hint"""
    hint_content: str
    level: int
    cost: int
    generation_time_ms: Optional[int] = None
    cached: bool = False
    hint_id: Optional[str] = None


# Predictions
class PredictionTask(BaseModel):
    """Prediction learning task"""
    task_id: str
    student_id: str
    query_to_predict: str
    database_schema: Dict[str, Any]
    expected_result: Dict[str, Any]
    difficulty_level: str
    concepts_tested: List[str]
    learning_objectives: List[str]
    estimated_time_minutes: int
    created_at: datetime


class PredictionResult(BaseModel):
    """Result of student prediction evaluation"""
    task_id: str
    student_id: str
    is_correct: bool
    accuracy_score: float = Field(..., ge=0.0, le=1.0)
    partial_credit_areas: List[str]
    common_errors_identified: List[str]
    misconceptions_revealed: List[str]
    concepts_reinforced: List[str]
    learning_gains: Dict[str, Any]
    time_efficiency: float
    evaluated_at: datetime


class PredictionFeedback(BaseModel):
    """Feedback for prediction task"""
    task_id: str
    student_id: str
    overall_feedback: str
    conceptual_insights: str
    specific_errors_explained: Dict[str, str]
    improvement_suggestions: List[str]
    follow_up_recommendations: List[Dict[str, Any]]
    encouragement_message: str
    next_steps: List[str]
    generated_at: datetime


# Coins and Economy
class CoinAward(BaseModel):
    """Coin award for learning activity"""
    student_id: str
    amount: int
    activity_type: str
    performance_score: float
    multiplier_applied: float
    new_balance: int
    transaction_id: Optional[str] = None


class CoinTransaction(BaseModel):
    """Coin transaction record"""
    id: str
    student_id: str
    amount: int  # Positive for earning, negative for spending
    service: str
    balance_after: int
    timestamp: datetime
    context: Optional[Dict[str, Any]] = None


class EarningForecast(BaseModel):
    """Forecast of potential coin earnings"""
    student_id: str
    daily_potential: int
    weekly_potential: int
    available_bonuses: int
    streak_potential: int
    milestone_rewards: int
    next_milestone: str
    days_to_milestone: int


# Student Profile
class LearningPattern(BaseModel):
    """Student learning behavior patterns"""
    session_frequency: str  # "daily", "regular", "irregular"
    error_recovery_style: str  # "systematic", "trial_error", "help_seeking"
    help_seeking_tendency: str  # "minimal", "moderate", "frequent"
    learning_pace: str  # "slow", "normal", "fast"
    concept_jumping_tendency: str  # "low", "medium", "high"


class LearningPreferences(BaseModel):
    """Student learning preferences"""
    preferred_hint_level: str  # "minimal", "moderate", "detailed", "adaptive"
    feedback_style: str  # "encouraging", "direct", "analytical"
    learning_pace: str  # "self_paced", "guided", "structured"
    difficulty_preference: str  # "easy_start", "gradual_increase", "challenge_seeking"
    interaction_style: str  # "independent", "guided", "collaborative"


class StudentProfile(BaseModel):
    """Comprehensive student profile"""
    student_id: str
    concept_mastery_map: Dict[str, Any]
    learning_patterns: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    preferences: Dict[str, Any]
    current_difficulty_level: str = "beginner"
    last_updated: Optional[datetime] = None 