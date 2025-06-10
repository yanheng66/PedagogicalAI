"""
SQL Analysis Pydantic schemas for request/response validation
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime

from .common import BaseResponse


class AnalysisContext(BaseModel):
    """Context information for SQL analysis"""
    student_id: str
    learning_context: Optional[str] = None
    chapter: Optional[str] = None
    exercise_id: Optional[str] = None
    difficulty_level: Optional[str] = "beginner"
    learning_objectives: List[str] = []


class SQLError(BaseModel):
    """SQL error information"""
    error_type: str  # syntax, logical, performance
    message: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    severity: str = "error"  # error, warning, info
    suggestion: Optional[str] = None


class ConceptUsage(BaseModel):
    """SQL concept usage information"""
    concept_name: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    usage_type: str  # correct, incorrect, missing
    context: Optional[str] = None


class SQLAnalysisRequest(BaseModel):
    """Request model for SQL analysis"""
    query: str = Field(..., min_length=1, max_length=10000)
    context: Optional[AnalysisContext] = None
    analysis_type: str = "hybrid"  # quick, llm, hybrid
    
    @validator('query')
    def validate_query(cls, v):
        """Validate SQL query format"""
        if not v.strip():
            raise ValueError("Query cannot be empty")
        # TODO: Add more SQL-specific validation
        return v.strip()


class QuickAnalysisResult(BaseModel):
    """Quick rule-based analysis result"""
    syntax_valid: bool
    syntax_errors: List[SQLError] = []
    basic_structure_valid: bool
    estimated_complexity: Optional[float] = None
    processing_time_ms: int


class LLMAnalysisResult(BaseModel):
    """LLM-based analysis result"""
    educational_feedback: Optional[str] = None
    concepts_identified: List[ConceptUsage] = []
    improvement_suggestions: List[str] = []
    alternative_approaches: List[str] = []
    complexity_assessment: Optional[str] = None
    learning_opportunities: List[str] = []
    model_used: Optional[str] = None
    confidence_score: Optional[float] = None


class SQLAnalysisResult(BaseModel):
    """Complete SQL analysis result"""
    analysis_id: str
    query_hash: str
    syntax_valid: bool
    errors: List[SQLError] = []
    warnings: List[SQLError] = []
    
    # Quality metrics
    complexity_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    readability_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    performance_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    
    # Educational insights
    concepts_used: List[ConceptUsage] = []
    difficulty_level: Optional[str] = None
    educational_insights: List[str] = []
    suggestions: List[str] = []
    
    # Metadata
    analysis_type: str
    processing_time_ms: int
    created_at: datetime = Field(default_factory=datetime.now)


class SQLAnalysisResponse(BaseResponse):
    """Response model for SQL analysis"""
    data: SQLAnalysisResult


class SQLAnalysisListResponse(BaseResponse):
    """Response model for SQL analysis history"""
    data: List[SQLAnalysisResult]
    total_count: int 