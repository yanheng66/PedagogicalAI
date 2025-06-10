"""
Common Pydantic schemas for API responses and error handling
"""

from typing import Any, Optional, Dict, List
from pydantic import BaseModel, Field
from datetime import datetime


class BaseResponse(BaseModel):
    """Base response model for all API responses"""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    

class ErrorResponse(BaseResponse):
    """Error response model"""
    success: bool = False
    error_code: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total_items: int = Field(ge=0)
    total_pages: int = Field(ge=0)
    has_next: bool
    has_previous: bool


class PaginatedResponse(BaseResponse):
    """Paginated response model"""
    data: List[Any] = []
    meta: PaginationMeta


class SuccessResponse(BaseResponse):
    """Simple success response"""
    data: Optional[Any] = None


class ValidationErrorDetail(BaseModel):
    """Validation error detail"""
    field: str
    message: str
    value: Optional[Any] = None


class ValidationErrorResponse(ErrorResponse):
    """Validation error response"""
    error_code: str = "VALIDATION_ERROR"
    validation_errors: List[ValidationErrorDetail] = [] 