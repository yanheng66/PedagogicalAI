"""
Database configuration and connection management
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
import redis.asyncio as redis

from src.config.settings import get_settings

# Database base class for models
Base = declarative_base()

# Global variables for database connections
async_engine = None
async_session_maker = None
redis_client = None


async def init_db():
    """Initialize database connections"""
    global async_engine, async_session_maker, redis_client
    
    settings = get_settings()
    
    # PostgreSQL async engine
    async_engine = create_async_engine(
        settings.database_url,
        poolclass=NullPool,
        echo=settings.debug,
    )
    
    # Session maker
    async_session_maker = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # Redis connection
    redis_client = redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True
    )
    
    # Create tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    """Dependency to get database session"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_redis() -> redis.Redis:
    """Dependency to get Redis client"""
    return redis_client


async def close_db():
    """Close database connections"""
    global async_engine, redis_client
    
    if async_engine:
        await async_engine.dispose()
    
    if redis_client:
        await redis_client.close() 