"""
LLM integration Pydantic schemas
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class LLMRequest(BaseModel):
    """LLM request model"""
    prompt: str
    model: str = "openai/gpt-4o-mini"
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    max_tokens: int = Field(default=500, ge=1, le=4000)
    context: Optional[Dict[str, Any]] = None


class LLMResponse(BaseModel):
    """LLM response model"""
    content: str
    model: str
    usage: Dict[str, Any] = {}
    finish_reason: Optional[str] = None
    created_at: datetime
    request_id: Optional[str] = None 