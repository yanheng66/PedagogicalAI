"""
Application settings and configuration management
"""

from typing import List
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Database configuration
    database_url: str = Field(..., env="DATABASE_URL")
    redis_url: str = Field(..., env="REDIS_URL")
    
    # Security
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    
    # External APIs
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openrouter_api_key: str = Field(..., env="OPENROUTER_API_KEY")
    
    # LLM configuration
    llm_model: str = "openai/gpt-4o-mini"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 500
    llm_timeout: int = 30
    
    # Cache configuration
    cache_ttl_analysis: int = 3600  # 1 hour
    cache_ttl_profile: int = 900    # 15 minutes
    cache_ttl_hints: int = 1800     # 30 minutes
    
    # CORS settings
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    rate_limit_burst: int = 10
    
    # Celery configuration
    celery_broker_url: str = Field(..., env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(..., env="CELERY_RESULT_BACKEND")
    
    # Application settings
    debug: bool = False
    log_level: str = "INFO"
    max_query_length: int = 10000
    max_hint_requests: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings instance"""
    return Settings() 