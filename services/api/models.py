"""
Database models for OmniVia.

Extends the core database module with domain-specific models.
"""

from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel
from sqlalchemy import Column, String, Text, DateTime, Integer, Float

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
    file_hash = Column(String(64), nullable=True)        # SHA-256 of content (for dedup)
    file_size = Column(Integer, nullable=True)           # Size in bytes
    imported_at = Column(DateTime, default=datetime.utcnow)
    last_indexed_at = Column(DateTime, nullable=True)   # When content was last parsed
    metadata_json = Column(Text, nullable=True)          # Arbitrary metadata as JSON


class Node(Base):
    """A unit of structured knowledge in the graph.

    Nodes represent discrete concepts, entities, or pieces of knowledge
    that can be connected through edges to form a knowledge graph.
    """
    __tablename__ = "nodes"

    id = Column(String(36), primary_key=True)
    node_type = Column(String(50), nullable=False)       # e.g. "concept", "person", "project", "decision"
    title = Column(String(500), nullable=False)          # Short label
    body = Column(Text, nullable=True)                   # Rich content or summary
    tags = Column(String(500), nullable=True)           # Comma-separated tags
    source_ids = Column(Text, nullable=True)             # JSON array of source IDs for provenance
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata_json = Column(Text, nullable=True)          # Type-specific metadata as JSON


class Edge(Base):
    """A relationship between two nodes in the knowledge graph.

    Edges connect nodes and define the nature of their relationship,
    enabling graph traversal and relationship-based queries.
    """
    __tablename__ = "edges"

    id = Column(String(36), primary_key=True)
    source_node_id = Column(String(36), nullable=False)  # The subject node
    target_node_id = Column(String(36), nullable=False)  # The object node
    relationship_type = Column(String(50), nullable=False)  # e.g. "relates_to", "depends_on"
    direction = Column(String(20), default="directed")  # "directed" | "bidirectional"
    weight = Column(Float, default=0.5)                  # Confidence 0-1
    source_ids = Column(Text, nullable=True)             # JSON array of source IDs for provenance
    created_at = Column(DateTime, default=datetime.utcnow)


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


class NodeCreate(BaseModel):
    node_type: str
    title: str
    body: Optional[str] = None
    tags: Optional[str] = None
    source_ids: Optional[list[str]] = None
    metadata: Optional[dict] = None


class NodeResponse(BaseModel):
    id: str
    node_type: str
    title: str
    body: Optional[str]
    tags: Optional[str]
    source_ids: Optional[list[str]]
    created_at: datetime
    updated_at: datetime
    metadata: Optional[dict]

    class Config:
        from_attributes = True


class EdgeCreate(BaseModel):
    source_node_id: str
    target_node_id: str
    relationship_type: str
    direction: Literal["directed", "bidirectional"] = "directed"
    weight: Optional[float] = 0.5
    source_ids: Optional[list[str]] = None


class EdgeResponse(BaseModel):
    id: str
    source_node_id: str
    target_node_id: str
    relationship_type: str
    direction: str
    weight: float
    source_ids: Optional[list[str]]
    created_at: datetime

    class Config:
        from_attributes = True


class SourceCreate(BaseModel):
    source_type: str
    uri: str
    title: Optional[str] = None
    file_hash: Optional[str] = None
    file_size: Optional[int] = None
    metadata: Optional[dict] = None


class SourceResponse(BaseModel):
    id: str
    source_type: str
    uri: str
    title: Optional[str]
    file_hash: Optional[str]
    file_size: Optional[int]
    imported_at: datetime
    last_indexed_at: Optional[datetime]
    metadata: Optional[dict]

    class Config:
        from_attributes = True