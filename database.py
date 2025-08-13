import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ---------------------------------------------------------------------------
# Database configuration
# ---------------------------------------------------------------------------
# Prefer DATABASE_URL environment variable, else fall back to local default.

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///pedagogical_ai.db",  # Changed to SQLite for testing
)

# Create SQLAlchemy engine. Pre-ping to avoid stale connections.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Scoped session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Declarative base for ORM models
Base = declarative_base()


@contextmanager
def get_db_session():
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close() 