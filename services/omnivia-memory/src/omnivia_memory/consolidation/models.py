"""Knowledge consolidation domain models for OmniVia.

Provides models for aggregating related memories into consolidated knowledge
units, and for detecting conflicts between memories on the same topic.

A KnowledgeUnit is a synthesized view of related memories on a topic, preserving
provenance by referencing the original memories. Conflict detection surfaces
cases where memories disagree on the same subject.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ConsolidationStrategy(str, Enum):
    """How related memories are grouped into knowledge units.

    TOPIC: Group by subject/theme (e.g., all memories about "authentication")
    SOURCE: Group by origin (e.g., all memories from the same ADR or file)
    DECISION: Group by decision context (e.g., all memories documenting a decision)
    """

    TOPIC = "topic"
    SOURCE = "source"
    DECISION = "decision"


class ConflictSeverity(str, Enum):
    """Severity level for detected memory conflicts.

    HIGH: Direct contradiction - memories assert incompatible states
    MEDIUM: Partial disagreement - memories emphasize different aspects
    LOW: Minor variance - memories have minor wording differences
    """

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class MemoryRef:
    """A reference to an original memory within a knowledge unit.

    Tracks provenance by pointing to the memory that contributed
    to this consolidated knowledge unit.

    Attributes:
        memory_id: The unique identifier of the referenced memory
        memory_content: The content of the referenced memory
        source_reference: Where this memory came from
        created_at: When the memory was created
        contribution_weight: How much this memory contributed (0.0 to 1.0)
    """

    memory_id: str
    memory_content: str
    source_reference: str
    created_at: str
    contribution_weight: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        """Convert memory reference to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            "memory_id": self.memory_id,
            "memory_content": self.memory_content,
            "source_reference": self.source_reference,
            "created_at": self.created_at,
            "contribution_weight": self.contribution_weight,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MemoryRef:
        """Create a memory reference from a dictionary.

        Args:
            data: Dictionary with memory reference fields

        Returns:
            MemoryRef instance
        """
        return cls(
            memory_id=data["memory_id"],
            memory_content=data["memory_content"],
            source_reference=data["source_reference"],
            created_at=data["created_at"],
            contribution_weight=data.get("contribution_weight", 1.0),
        )


@dataclass
class KnowledgeUnit:
    """A consolidated view of related memories on a topic.

    Knowledge units aggregate multiple memories that share a common topic,
    source, or decision context. The consolidation preserves provenance
    by referencing the original memories.

    This allows agents to get a synthesized view while still being able to
    trace conclusions back to their source memories.

    Attributes:
        id: Unique identifier for this knowledge unit
        topic: The subject/topic this unit covers
        summary: Synthesized summary of the memories
        memory_refs: References to the original memories
        consolidation_strategy: How memories were grouped
        confidence_score: Confidence in the consolidation (0.0 to 1.0)
        created_at: When this unit was created
        updated_at: When this unit was last updated
    """

    topic: str
    summary: str
    memory_refs: list[MemoryRef] = field(default_factory=list)
    consolidation_strategy: ConsolidationStrategy = ConsolidationStrategy.TOPIC
    confidence_score: float = 0.5
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert knowledge unit to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            "id": self.id,
            "topic": self.topic,
            "summary": self.summary,
            "memory_refs": [ref.to_dict() for ref in self.memory_refs],
            "consolidation_strategy": self.consolidation_strategy.value,
            "confidence_score": self.confidence_score,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KnowledgeUnit:
        """Create a knowledge unit from a dictionary.

        Args:
            data: Dictionary with knowledge unit fields

        Returns:
            KnowledgeUnit instance
        """
        return cls(
            id=data["id"],
            topic=data["topic"],
            summary=data["summary"],
            memory_refs=[MemoryRef.from_dict(ref) for ref in data.get("memory_refs", [])],
            consolidation_strategy=ConsolidationStrategy(
                data.get("consolidation_strategy", "topic")
            ),
            confidence_score=data.get("confidence_score", 0.5),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )

    def touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def add_memory_ref(self, ref: MemoryRef) -> None:
        """Add a memory reference to this unit.

        Args:
            ref: The memory reference to add
        """
        self.memory_refs.append(ref)
        self.touch()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, KnowledgeUnit):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return (
            f"KnowledgeUnit(id={self.id[:8]}..., topic={self.topic}, "
            f"strategy={self.consolidation_strategy.value}, "
            f"memories={len(self.memory_refs)})"
        )


@dataclass
class MemoryConflict:
    """A detected conflict between memories on the same topic.

    Conflicts occur when memories assert different states or facts about
    the same subject. This enables surfacing contradictions for human review.

    Attributes:
        id: Unique identifier for this conflict
        topic: The subject both memories relate to
        severity: How severe is this conflict (high/medium/low)
        memory_refs: The conflicting memories
        conflict_description: Human-readable description of the conflict
        resolution_status: Has this conflict been resolved
        created_at: When the conflict was detected
    """

    topic: str
    severity: ConflictSeverity
    memory_refs: list[MemoryRef] = field(default_factory=list)
    conflict_description: str = ""
    resolution_status: str = "unresolved"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert memory conflict to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            "id": self.id,
            "topic": self.topic,
            "severity": self.severity.value,
            "memory_refs": [ref.to_dict() for ref in self.memory_refs],
            "conflict_description": self.conflict_description,
            "resolution_status": self.resolution_status,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MemoryConflict:
        """Create a memory conflict from a dictionary.

        Args:
            data: Dictionary with memory conflict fields

        Returns:
            MemoryConflict instance
        """
        return cls(
            id=data["id"],
            topic=data["topic"],
            severity=ConflictSeverity(data["severity"]),
            memory_refs=[MemoryRef.from_dict(ref) for ref in data.get("memory_refs", [])],
            conflict_description=data.get("conflict_description", ""),
            resolution_status=data.get("resolution_status", "unresolved"),
            created_at=data["created_at"],
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MemoryConflict):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return (
            f"MemoryConflict(id={self.id[:8]}..., topic={self.topic}, "
            f"severity={self.severity.value}, status={self.resolution_status})"
        )


# Type alias for topic keywords used in conflict detection
TopicKeywords = list[str]


def extract_topic_keywords(memory_content: str) -> TopicKeywords:
    """Extract potential topic keywords from memory content.

    This is a simple keyword extraction that identifies nouns and
    significant terms. More sophisticated NLP can be added later.

    Args:
        memory_content: The memory text to extract keywords from

    Returns:
        List of potential topic keywords
    """
    # Simple keyword extraction - remove common words and extract significant terms
    common_words = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "must",
        "shall",
        "can",
        "need",
        "dare",
        "to",
        "of",
        "in",
        "for",
        "on",
        "with",
        "at",
        "by",
        "from",
        "as",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "between",
        "under",
        "again",
        "further",
        "then",
        "once",
        "here",
        "there",
        "when",
        "where",
        "why",
        "how",
        "all",
        "each",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "no",
        "nor",
        "not",
        "only",
        "own",
        "same",
        "so",
        "than",
        "too",
        "very",
        "just",
        "and",
        "but",
        "or",
        "if",
        "because",
        "until",
        "while",
        "although",
        "this",
        "that",
        "these",
        "those",
        "it",
        "its",
    }

    # Split on whitespace and punctuation, filter short words and common words
    words = memory_content.split()
    keywords: list[str] = []

    for word in words:
        # Strip punctuation
        cleaned = word.strip(".,!?;:()[]{}'\"").lower()
        if len(cleaned) > 3 and cleaned not in common_words:
            keywords.append(cleaned)

    return keywords
