from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Memory(Base):
    __tablename__ = "memories"

    id = Column(String(36), primary_key=True)
    content = Column(Text, nullable=False)
    source = Column(String(500), nullable=True)
    memory_type = Column(String(50), default="general")
    approval_status = Column(String(20), default="proposed")
    created_by = Column(String(10), default="human")
    created_at = Column(DateTime, default=datetime.utcnow)
    embedding_id = Column(String(100), nullable=True)


def get_engine(db_path: str):
    """Create SQLAlchemy engine for the given database path."""
    db_dir = db_path.rsplit("/", 1)[0]
    import os
    os.makedirs(db_dir, exist_ok=True)
    return create_engine(f"sqlite:///{db_path}", echo=False)


def init_db(engine):
    """Initialize database tables."""
    Base.metadata.create_all(engine)