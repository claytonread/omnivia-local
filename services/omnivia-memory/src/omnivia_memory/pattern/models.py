"""Pattern domain models for OmniVia.

Represents recurring patterns detected in memories and the knowledge graph.
Patterns are themselves knowledge that can be stored, approved, and queried.

Agent-created patterns default to "proposed" state for human review before
they influence agent reasoning about recurring knowledge.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class PatternType(str, Enum):
    """Categories of patterns that can be detected in memories.

    Each pattern type represents a different kind of recurring knowledge
    that agents can learn from.

    CONTENT_SIMILARITY: Multiple memories contain similar knowledge
    SOURCE_CLUSTER: Same source generates multiple related memories
    LIFECYCLE_TRANSITION: Common state change paths (proposed->approved)
    CONCEPT_REFERENCE: Same concept mentioned across different memories
    DECISION_RECURRENCE: Similar decisions being made repeatedly
    """

    CONTENT_SIMILARITY = "content_similarity"
    SOURCE_CLUSTER = "source_cluster"
    LIFECYCLE_TRANSITION = "lifecycle_transition"
    CONCEPT_REFERENCE = "concept_reference"
    DECISION_RECURRENCE = "decision_recurrence"


@dataclass
class PatternEntity:
    """A detected pattern in the knowledge graph.

    Patterns represent recurring knowledge or behavior observed across
    memories. For example, "the same decision about logging appears
    in multiple ADRs" or "files in docs/ folder always generate
    memory-type=task memories".

    Agent-created patterns default to "proposed" so humans can verify
    the detected pattern is accurate before it influences reasoning.

    Attributes:
        id: Unique identifier for this pattern
        name: Human-readable name describing the pattern
        pattern_type: Category of pattern detected
        description: Detailed explanation of what the pattern represents
        confidence: How strongly this pattern is confirmed (0.0-1.0)
        occurrence_count: Number of times this pattern was observed
        source_id: Reference to the evidence/memory that detected this pattern
        approval_status: Governance state (proposed/approved/rejected/superseded)
        created_at: When this pattern was created (ISO 8601 timestamp)
        updated_at: When this pattern was last modified (ISO 8601 timestamp)
    """

    name: str
    pattern_type: PatternType
    description: str
    confidence: float
    occurrence_count: int
    source_id: str | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    approval_status: str = "proposed"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert pattern to dictionary for serialization.

        Returns:
            Dictionary representation of the pattern
        """
        return {
            "id": self.id,
            "name": self.name,
            "pattern_type": self.pattern_type.value,
            "description": self.description,
            "confidence": self.confidence,
            "occurrence_count": self.occurrence_count,
            "source_id": self.source_id,
            "approval_status": self.approval_status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PatternEntity:
        """Create a pattern from a dictionary.

        Args:
            data: Dictionary with pattern fields

        Returns:
            PatternEntity instance
        """
        return cls(
            id=data["id"],
            name=data["name"],
            pattern_type=PatternType(data["pattern_type"]),
            description=data["description"],
            confidence=data["confidence"],
            occurrence_count=data["occurrence_count"],
            source_id=data.get("source_id"),
            approval_status=data["approval_status"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )

    def approve(self) -> None:
        """Mark this pattern as approved by human review."""
        self.approval_status = "approved"
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def reject(self) -> None:
        """Mark this pattern as rejected."""
        self.approval_status = "rejected"
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def touch(self) -> None:
        """Update the updated_at timestamp without changing content."""
        self.updated_at = datetime.now(timezone.utc).isoformat()


@dataclass
class PatternRelationship:
    """A relationship between two patterns or between a pattern and a memory.

    Enables tracking connections like:
    - Pattern A is a specialization of Pattern B
    - Memory X exemplifies Pattern Y
    - Pattern A frequently precedes Pattern B

    Agent-created relationships default to "proposed" state.

    Attributes:
        id: Unique identifier for this relationship
        source_pattern_id: ID of the pattern where the relationship originates
        target_pattern_id: ID of the pattern being connected
        related_memory_id: Optional memory ID that relates to this pattern
        relationship_type: Semantic meaning of the connection
        source_id: Reference to the evidence/source document
        approval_status: Governance state
        created_at: When created (ISO 8601 timestamp)
        updated_at: When last modified (ISO 8601 timestamp)
    """

    source_pattern_id: str
    target_pattern_id: str | None = None
    related_memory_id: str | None = None
    relationship_type: str = "exemplifies"
    source_id: str | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    approval_status: str = "proposed"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert relationship to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            "id": self.id,
            "source_pattern_id": self.source_pattern_id,
            "target_pattern_id": self.target_pattern_id,
            "related_memory_id": self.related_memory_id,
            "relationship_type": self.relationship_type,
            "source_id": self.source_id,
            "approval_status": self.approval_status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PatternRelationship:
        """Create a relationship from a dictionary.

        Args:
            data: Dictionary with relationship fields

        Returns:
            PatternRelationship instance
        """
        return cls(
            id=data["id"],
            source_pattern_id=data["source_pattern_id"],
            target_pattern_id=data.get("target_pattern_id"),
            related_memory_id=data.get("related_memory_id"),
            relationship_type=data.get("relationship_type", "exemplifies"),
            source_id=data.get("source_id"),
            approval_status=data["approval_status"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )

    def approve(self) -> None:
        """Mark this relationship as approved by human review."""
        self.approval_status = "approved"
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def reject(self) -> None:
        """Mark this relationship as rejected."""
        self.approval_status = "rejected"
        self.updated_at = datetime.now(timezone.utc).isoformat()


@dataclass
class PatternOccurrence:
    """An occurrence of a pattern being detected in memories.

    Links a pattern to the specific memory or evidence that triggered
    its detection. Used to track which memories exemplify which patterns.

    Attributes:
        pattern_id: The pattern that was detected
        memory_id: The memory that triggered this detection
        evidence: The specific content or metadata that matched the pattern
        detected_at: When the occurrence was detected (ISO 8601 timestamp)
    """

    pattern_id: str
    memory_id: str
    evidence: str | None = None
    detected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert occurrence to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            "pattern_id": self.pattern_id,
            "memory_id": self.memory_id,
            "evidence": self.evidence,
            "detected_at": self.detected_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PatternOccurrence:
        """Create an occurrence from a dictionary.

        Args:
            data: Dictionary with occurrence fields

        Returns:
            PatternOccurrence instance
        """
        return cls(
            pattern_id=data["pattern_id"],
            memory_id=data["memory_id"],
            evidence=data.get("evidence"),
            detected_at=data["detected_at"],
        )


@dataclass
class PatternCreate:
    """Input model for creating a new pattern.

    Used by the detection algorithm to create patterns from observed
    recurring knowledge.

    Attributes:
        name: Human-readable name for the pattern
        pattern_type: Category of pattern detected
        description: Explanation of what the pattern represents
        confidence: How strongly confirmed (0.0-1.0)
        occurrence_count: Number of observations
        source_id: Reference to detection evidence
    """

    name: str
    pattern_type: PatternType
    description: str
    confidence: float
    occurrence_count: int
    source_id: str | None = None
