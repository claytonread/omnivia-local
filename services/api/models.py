"""
Database models for OmniVia.

Extends the core database module with domain-specific models.
"""

from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel
from sqlalchemy import Column, String, Text, DateTime, Integer

from services.api.database import Base


class Source(Base):
    """A source document or file that has been ingested into OmniVia.

    Tracks the origin artefact so we can preserve provenance back to
    the original file, URL, or document for every memory and node.
    """
    __tablename__ = "sources"

    id = Column(String(36), primary_key=True)
    source_type = Column(String(50), nullable=False)       # e.g. "file", "url", "chat_export"
    uri = Column(String(1000), nullable=False)           # File path, URL, or identifier
    title = Column(String(500), nullable=True)           # Human-readable title
    file_hash = Column(String(64), nullable=True)        # SHA-256 of file content
    file_size = Column(Integer, nullable=True)           # Size in bytes
    imported_at = Column(DateTime, default=datetime.utcnow)
    last_indexed_at = Column(DateTime, nullable=True)   # When content was last parsed
    metadata_json = Column(Text, nullable=True)          # Arbitrary metadata as JSON


# =============================================================================
# Pydantic schemas for API request/response validation
# =============================================================================

class MemoryCreate(BaseModel):
    content: str
    source: Optional[str] = None
    memory_type: Optional[str] = "general"
    created_by: Literal["human", "agent"] = "human"


class Memory(BaseModel):
    id: str
    content: str
    source: Optional[str]
    memory_type: str
    approval_status: Literal["proposed", "observed", "approved"]
    created_by: Literal["human", "agent"]
    created_at: datetime
    embedding_id: Optional[str] = None

    class Config:
        from_attributes = True


class MemorySearch(BaseModel):
    query: str
    limit: int = 5
    approval_status: Optional[str] = None