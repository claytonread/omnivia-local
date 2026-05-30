"""Database connection and core models for OmniVia.

This module provides:
- SQLAlchemy Base for ORM model definitions
- Memory model for embedding-based knowledge
- Database initialization and engine creation

The database is SQLite for local-first operation. Data persists in a single
file specified by OMNIVIA_DB_PATH environment variable.
"""

from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# SQLAlchemy declarative base - all ORM models inherit from this
Base = declarative_base()


class Memory(Base):
    """A unit of knowledge with vector embedding for semantic search.

    Memories are the core knowledge unit in OmniVia. Each memory:
    - Stores text content that gets embedded for similarity search
    - Has an approval_status controlling visibility and trust
    - References a source for provenance
    - Is stored in both SQLite (structured) and Qdrant (vector search)

    The approval_status lifecycle prevents unverified AI observations from
    silently becoming trusted business knowledge:
    - proposed: AI-created, requires human review
    - observed: Human-created or reviewed, visible to agents
    - approved: Verified, trusted for business decisions
    """
    __tablename__ = "memories"

    id = Column(String(36), primary_key=True)
    content = Column(Text, nullable=False)  # The knowledge content
    source = Column(String(500), nullable=True)  # Provenance reference
    memory_type = Column(String(50), default="general")  # Category
    approval_status = Column(String(20), default="proposed")  # Trust level
    created_by = Column(String(10), default="human")  # "human" or "agent"
    created_at = Column(DateTime, default=datetime.utcnow)
    embedding_id = Column(String(100), nullable=True)  # Qdrant reference


def get_engine(db_path: str):
    """Create a SQLAlchemy engine for the given SQLite database path.

    Automatically creates the database directory if it doesn't exist.
    Uses SQLite for local-first operation without external dependencies.

    Args:
        db_path: Full path to the SQLite database file

    Returns:
        SQLAlchemy Engine instance
    """
    db_dir = db_path.rsplit("/", 1)[0]
    import os
    os.makedirs(db_dir, exist_ok=True)
    return create_engine(f"sqlite:///{db_path}", echo=False)


def init_db(engine):
    """Initialize the database by creating all tables.

    Uses SQLAlchemy's create_all() which is idempotent - safe to call
    multiple times. Creates tables for all models that inherit from Base.

    Args:
        engine: SQLAlchemy Engine instance
    """
    Base.metadata.create_all(engine)