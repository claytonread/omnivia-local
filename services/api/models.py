"""Database models for OmniVia.

This module defines the domain entities for the knowledge graph:
- Source: Origin artefacts (files, URLs) for provenance tracking
- Memory: Embedding-based knowledge units with approval status
- Node: Structured knowledge entities with explicit types
- Edge: Relationships between nodes in the knowledge graph

The approval status lifecycle for Memory:
- proposed: AI-created, requires human review before use
- observed: Human-created or reviewed, visible to agents
- approved: Verified, trusted knowledge for business decisions
"""

from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel
from sqlalchemy import Column, String, Text, DateTime, Integer, Float

from services.api.database import Base


class Source(Base):
    """A source document or artefact ingested into OmniVia.

    Tracks the origin of knowledge for provenance and attribution.
    Every memory and node can reference its source(s) to trace
    back to the original file, URL, or document.

    Example sources:
    - A markdown file in a local vault
    - A web article URL
    - An exported AI conversation
    - A manual note entered by the user
    """
    __tablename__ = "sources"

    id = Column(String(36), primary_key=True)
    # Type distinguishes file, URL, chat_export, manual, etc.
    source_type = Column(String(50), nullable=False)
    # URI: file path, URL, or other identifier
    uri = Column(String(1000), nullable=False)
    title = Column(String(500), nullable=True)  # Human-readable label
    # SHA-256 hash for content deduplication
    file_hash = Column(String(64), nullable=True)
    file_size = Column(Integer, nullable=True)  # Bytes
    imported_at = Column(DateTime, default=datetime.utcnow)
    last_indexed_at = Column(DateTime, nullable=True)  # Last content parse
    # Arbitrary metadata: title, author, tags, etc.
    metadata_json = Column(Text, nullable=True)


class Node(Base):
    """A unit of structured knowledge in the graph.

    Nodes represent discrete entities in the knowledge graph:
    - concepts: Abstract ideas or principles
    - persons: Human individuals with expertise
    - projects: Work efforts or initiatives
    - decisions: Choices made with rationale
    - constraints: Limitations or requirements
    - systems: Technical or organizational structures

    Nodes are connected via Edges to form a traversable knowledge graph.
    The source_ids field links back to Source records for provenance.
    """
    __tablename__ = "nodes"

    id = Column(String(36), primary_key=True)
    # Category: concept, person, project, decision, etc.
    node_type = Column(String(50), nullable=False)
    title = Column(String(500), nullable=False)  # Short label
    body = Column(Text, nullable=True)  # Rich content or summary
    tags = Column(String(500), nullable=True)  # Comma-separated keywords
    # JSON array of source IDs for provenance tracking
    source_ids = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Type-specific metadata: dates, links, references, etc.
    metadata_json = Column(Text, nullable=True)


class Edge(Base):
    """A relationship between two nodes in the knowledge graph.

    Edges connect nodes and define the nature of their relationship.
    The relationship_type field specifies the semantic connection type.

    Common relationship types:
    - relates_to: General association
    - depends_on: Dependency or prerequisite
    - supports: Evidence or backing
    - contradicts: Opposition or conflict
    - implements: Realization of a specification
    - derived_from: Transformation or derivation

    The weight field (0-1) can represent confidence or strength of relationship.
    """
    __tablename__ = "edges"

    id = Column(String(36), primary_key=True)
    source_node_id = Column(String(36), nullable=False)  # Subject
    target_node_id = Column(String(36), nullable=False)  # Object
    relationship_type = Column(String(50), nullable=False)  # e.g. "relates_to"
    direction = Column(String(20), default="directed")  # "directed" | "bidirectional"
    weight = Column(Float, default=0.5)  # Confidence 0-1
    # JSON array of source IDs for provenance
    source_ids = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# =============================================================================
# Pydantic Schemas (API Request/Response Validation)
# =============================================================================

class MemoryCreate(BaseModel):
    """Request schema for creating a memory."""
    content: str
    source: Optional[str] = None
    memory_type: Optional[str] = "general"
    created_by: Literal["human", "agent"] = "human"


class Memory(BaseModel):
    """Response schema for a memory entity."""
    id: str
    content: str
    source: Optional[str]
    memory_type: str
    # Approval lifecycle: proposed -> observed -> approved
    approval_status: Literal["proposed", "observed", "approved"]
    created_by: Literal["human", "agent"]
    created_at: datetime
    embedding_id: Optional[str] = None  # Reference to Qdrant vector

    class Config:
        from_attributes = True


class NodeCreate(BaseModel):
    """Request schema for creating a node."""
    node_type: str
    title: str
    body: Optional[str] = None
    tags: Optional[str] = None
    source_ids: Optional[list[str]] = None
    metadata: Optional[dict] = None


class NodeResponse(BaseModel):
    """Response schema for a node entity."""
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
    """Request schema for creating an edge."""
    source_node_id: str
    target_node_id: str
    relationship_type: str
    direction: Literal["directed", "bidirectional"] = "directed"
    weight: Optional[float] = 0.5
    source_ids: Optional[list[str]] = None


class EdgeResponse(BaseModel):
    """Response schema for an edge entity."""
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
    """Request schema for registering a source."""
    source_type: str
    uri: str
    title: Optional[str] = None
    file_hash: Optional[str] = None
    file_size: Optional[int] = None
    metadata: Optional[dict] = None


class SourceResponse(BaseModel):
    """Response schema for a source entity."""
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