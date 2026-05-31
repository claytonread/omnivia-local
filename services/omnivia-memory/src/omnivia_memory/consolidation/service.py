"""Knowledge consolidation service for OmniVia.

Provides high-level operations for:
- Aggregating related memories into consolidated knowledge units
- Detecting conflicts between memories on the same topic
- Creating synthesized views of related knowledge

This service works with the existing memory layer, extracting and grouping
memories by topic, source, or decision context.
"""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

from omnivia_memory.memory.models import Memory
from omnivia_memory.persistence.repositories import MemoryRepository

from omnivia_memory.consolidation.models import (
    ConflictSeverity,
    ConsolidationStrategy,
    KnowledgeUnit,
    MemoryConflict,
    MemoryRef,
    extract_topic_keywords,
)


class ConsolidationServiceError(Exception):
    """Base exception for consolidation service errors."""

    pass


class KnowledgeUnitNotFoundError(ConsolidationServiceError):
    """Raised when a requested knowledge unit does not exist."""

    pass


class ConsolidationService:
    """Service for knowledge consolidation operations.

    Aggregates related memories into knowledge units and detects conflicts
    between memories on the same topic. Works with existing memories from
    the memory repository.

    Attributes:
        repository: Optional memory repository for persistence
        min_conflicts_for_detection: Minimum memories needed to check for conflicts
    """

    def __init__(
        self,
        repository: MemoryRepository | None = None,
        min_conflicts_for_detection: int = 2,
    ) -> None:
        self.repository = repository
        self.min_conflicts_for_detection = min_conflicts_for_detection
        # In-memory storage for knowledge units (persistence can be added later)
        self._knowledge_units: dict[str, KnowledgeUnit] = {}
        self._conflicts: list[MemoryConflict] = []

    def _memory_to_ref(self, memory: Memory) -> MemoryRef:
        """Convert a memory to a memory reference.

        Args:
            memory: The memory to convert

        Returns:
            MemoryRef with provenance information
        """
        return MemoryRef(
            memory_id=memory.id,
            memory_content=memory.content,
            source_reference=memory.source.reference,
            created_at=memory.created_at,
            contribution_weight=1.0,
        )

    def _extract_topic(self, memory: Memory) -> str:
        """Extract the primary topic from a memory.

        Uses the memory_type and content to determine topic.
        Can be enhanced with NLP or keyword extraction.

        Args:
            memory: The memory to extract topic from

        Returns:
            Topic string
        """
        # Use memory type as primary topic identifier
        memory_type = memory.memory_type

        # Extract significant keywords for more specific topic
        keywords = extract_topic_keywords(memory.content)

        # Build topic from memory type and key terms
        topic_parts = [memory_type]

        # Add first significant keyword if present
        if keywords:
            topic_parts.append(keywords[0])

        return "/".join(topic_parts)

    def _calculate_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two memory contents.

        Uses keyword overlap to determine similarity score.
        Returns value between 0.0 (no overlap) and 1.0 (identical).

        Args:
            content1: First memory content
            content2: Second memory content

        Returns:
            Similarity score
        """
        keywords1 = set(extract_topic_keywords(content1))
        keywords2 = set(extract_topic_keywords(content2))

        if not keywords1 or not keywords2:
            return 0.0

        # Calculate Jaccard similarity
        intersection = keywords1 & keywords2
        union = keywords1 | keywords2

        return len(intersection) / len(union) if union else 0.0

    def _detect_conflict(self, memory1: Memory, memory2: Memory) -> bool:
        """Detect if two memories conflict on the same topic.

        Conflicts are detected by looking for contradictory patterns
        like "X is Y" vs "X is not Y" or state changes.

        Args:
            memory1: First memory
            memory2: Second memory

        Returns:
            True if memories appear to conflict
        """
        content1 = memory1.content.lower()
        content2 = memory2.content.lower()

        # Look for negation patterns that indicate potential conflicts
        negation_patterns = [
            (r"\bnot\b", r"\bdoes not\b", r"\bis not\b"),
            (r"\bno longer\b", r"\bnever\b", r"\bwithout\b"),
            (r"\breject(?:ed|ing)?\b", r"\bremove[sd]?\b", r"\bdelete[sd]?\b"),
            (r"\breplace[sd]?\b", r"\bswitch(?:ed|ing)?\b", r"\bmove[sd]?\b"),
        ]

        for pattern_group in negation_patterns:
            has_negation1 = any(re.search(p, content1) for p in pattern_group)
            has_negation2 = any(re.search(p, content2) for p in pattern_group)

            # If one has negation and other doesn't, potential conflict
            if has_negation1 != has_negation2:
                return True

        # Check for state change indicators
        state_indicators = [
            "changed",
            "updated",
            "modified",
            "replaced",
            "from",
            "to",
            "before",
            "after",
            "now",
            "previously",
        ]

        count1 = sum(1 for indicator in state_indicators if indicator in content1)
        count2 = sum(1 for indicator in state_indicators if indicator in content2)

        # If both have state change indicators but different contents, possible conflict
        if count1 >= 1 and count2 >= 1:
            # Check if they're discussing the same thing differently
            keywords1 = set(extract_topic_keywords(memory1.content))
            keywords2 = set(extract_topic_keywords(memory2.content))
            overlap = keywords1 & keywords2

            # If significant overlap but state indicators differ, check for conflict
            if len(overlap) >= 2:
                return True

        return False

    def _calculate_conflict_severity(self, memory1: Memory, memory2: Memory) -> ConflictSeverity:
        """Determine the severity of a conflict between memories.

        Args:
            memory1: First memory
            memory2: Second memory

        Returns:
            ConflictSeverity level
        """
        content1 = memory1.content.lower()
        content2 = memory2.content.lower()

        # High severity: Direct contradiction with negation
        negation_indicators = ["not", "no longer", "never", "without"]
        for indicator in negation_indicators:
            if (indicator in content1) != (indicator in content2):
                return ConflictSeverity.HIGH

        # High severity: Same keywords but opposite actions
        if "approve" in content1 and "reject" in content2:
            return ConflictSeverity.HIGH
        if "approve" in content2 and "reject" in content1:
            return ConflictSeverity.HIGH

        # Medium severity: Different emphasis or perspective
        perspective_words = ["prefer", "suggest", "recommend", "should", "must"]
        if any(word in content1 for word in perspective_words):
            if any(word in content2 for word in perspective_words):
                return ConflictSeverity.MEDIUM

        # Low severity: Minor variations
        similarity = self._calculate_similarity(memory1.content, memory2.content)
        if similarity > 0.5:
            return ConflictSeverity.LOW

        return ConflictSeverity.MEDIUM

    def consolidate_by_topic(
        self,
        topic: str | None = None,
        memory_type: str | None = None,
        limit: int = 50,
    ) -> list[KnowledgeUnit]:
        """Consolidate memories by topic.

        Groups memories sharing topics into knowledge units.
        If topic is specified, only consolidates that topic.
        Otherwise, creates units for all topics found.

        Args:
            topic: Optional specific topic to consolidate
            memory_type: Optional memory type filter
            limit: Maximum memories to consider

        Returns:
            List of created knowledge units
        """
        if not self.repository:
            return []

        # Fetch memories to consolidate
        if topic or memory_type:
            # Search for matching memories
            memories = self.repository.search(
                query=topic or memory_type or "",
                limit=limit,
            )
            # Filter by memory_type if specified
            if memory_type:
                memories = [m for m in memories if m.memory_type == memory_type]
        else:
            memories = self.repository.list_all(limit=limit)

        if len(memories) < self.min_conflicts_for_detection:
            return []

        # Group memories by topic
        topic_groups: dict[str, list[Memory]] = defaultdict(list)
        for memory in memories:
            if topic and topic not in memory.content.lower():
                continue
            memory_topic = self._extract_topic(memory)
            topic_groups[memory_topic].append(memory)

        # Create knowledge units for each topic group
        units: list[KnowledgeUnit] = []
        for topic_key, group_memories in topic_groups.items():
            if len(group_memories) < 1:
                continue

            # Create summary from all memories in group
            summary_parts = [m.content for m in group_memories[:5]]
            summary = " | ".join(summary_parts)

            # Calculate confidence based on memory count and agreement
            confidence = min(0.5 + (len(group_memories) * 0.1), 1.0)

            unit = KnowledgeUnit(
                topic=topic_key,
                summary=summary[:500],  # Truncate long summaries
                memory_refs=[self._memory_to_ref(m) for m in group_memories],
                consolidation_strategy=ConsolidationStrategy.TOPIC,
                confidence_score=confidence,
            )

            self._knowledge_units[unit.id] = unit
            units.append(unit)

        return units

    def consolidate_by_source(
        self,
        source_reference: str | None = None,
        limit: int = 50,
    ) -> list[KnowledgeUnit]:
        """Consolidate memories by source.

        Groups memories originating from the same source file or ADR.

        Args:
            source_reference: Optional specific source to consolidate
            limit: Maximum memories to consider

        Returns:
            List of created knowledge units
        """
        if not self.repository:
            return []

        memories = self.repository.list_all(limit=limit)

        # Group by source
        source_groups: dict[str, list[Memory]] = defaultdict(list)
        for memory in memories:
            if source_reference and memory.source.reference != source_reference:
                continue
            source_groups[memory.source.reference].append(memory)

        # Create knowledge units for each source
        units: list[KnowledgeUnit] = []
        for source_ref, group_memories in source_groups.items():
            if len(group_memories) < 1:
                continue

            summary_parts = [m.content for m in group_memories[:5]]
            summary = " | ".join(summary_parts)

            confidence = min(0.6 + (len(group_memories) * 0.1), 1.0)

            unit = KnowledgeUnit(
                topic=f"source:{source_ref}",
                summary=summary[:500],
                memory_refs=[self._memory_to_ref(m) for m in group_memories],
                consolidation_strategy=ConsolidationStrategy.SOURCE,
                confidence_score=confidence,
            )

            self._knowledge_units[unit.id] = unit
            units.append(unit)

        return units

    def consolidate_by_decision(
        self,
        decision_id: str | None = None,
        limit: int = 50,
    ) -> list[KnowledgeUnit]:
        """Consolidate memories related to decisions.

        Groups memories that document decisions, typically those with
        memory_type='decision' or sourced from ADRs.

        Args:
            decision_id: Optional specific decision to consolidate
            limit: Maximum memories to consider

        Returns:
            List of created knowledge units
        """
        if not self.repository:
            return []

        memories = self.repository.list_all(limit=limit)

        # Filter to decision-related memories
        decision_memories = [
            m for m in memories if m.memory_type == "decision" or m.source.type.value == "adr"
        ]

        if decision_id:
            decision_memories = [
                m
                for m in decision_memories
                if decision_id in m.content or decision_id in m.source.reference
            ]

        if len(decision_memories) < 1:
            return []

        # Create single knowledge unit for all decision memories
        summary_parts = [m.content for m in decision_memories[:10]]
        summary = " | ".join(summary_parts)

        unit = KnowledgeUnit(
            topic=f"decisions/{decision_id or 'all'}",
            summary=summary[:500],
            memory_refs=[self._memory_to_ref(m) for m in decision_memories],
            consolidation_strategy=ConsolidationStrategy.DECISION,
            confidence_score=0.8,  # Decision memories typically high confidence
        )

        self._knowledge_units[unit.id] = unit
        return [unit]

    def detect_conflicts(
        self,
        topic: str | None = None,
        memory_type: str | None = None,
    ) -> list[MemoryConflict]:
        """Detect conflicts between memories on the same topic.

        Analyzes memories looking for contradictory information.
        Returns list of detected conflicts for human review.

        Args:
            topic: Optional specific topic to check
            memory_type: Optional memory type filter

        Returns:
            List of detected conflicts
        """
        if not self.repository:
            return []

        # Fetch relevant memories
        if topic:
            memories = self.repository.search(query=topic, limit=100)
        else:
            memories = self.repository.list_all(limit=100)

        if memory_type:
            memories = [m for m in memories if m.memory_type == memory_type]

        if len(memories) < self.min_conflicts_for_detection:
            return []

        # Group memories by topic keywords
        topic_keywords = defaultdict(list)
        for memory in memories:
            keywords = extract_topic_keywords(memory.content)
            for keyword in keywords[:5]:  # Use top 5 keywords
                topic_keywords[keyword].append(memory)

        # Check for conflicts in each topic group
        conflicts: list[MemoryConflict] = []
        seen_pairs: set[tuple[str, str]] = set()

        for keyword, group_memories in topic_keywords.items():
            if len(group_memories) < self.min_conflicts_for_detection:
                continue

            # Compare each pair of memories
            for i, mem1 in enumerate(group_memories):
                for mem2 in group_memories[i + 1 :]:
                    # Skip already checked pairs
                    # Use frozenset for order-independent comparison
                    pair_key: tuple[str, str] = tuple(sorted([mem1.id, mem2.id]))  # type: ignore[assignment]
                    if pair_key in seen_pairs:
                        continue
                    seen_pairs.add(pair_key)

                    if self._detect_conflict(mem1, mem2):
                        severity = self._calculate_conflict_severity(mem1, mem2)
                        conflict = MemoryConflict(
                            topic=keyword,
                            severity=severity,
                            memory_refs=[
                                self._memory_to_ref(mem1),
                                self._memory_to_ref(mem2),
                            ],
                            conflict_description=f"Memories '{mem1.content[:50]}...' and "
                            f"'{mem2.content[:50]}...' appear to conflict on topic: {keyword}",
                        )
                        conflicts.append(conflict)
                        self._conflicts.append(conflict)

        return conflicts

    def get_knowledge_unit(self, unit_id: str) -> KnowledgeUnit:
        """Retrieve a knowledge unit by ID.

        Args:
            unit_id: The unique identifier of the knowledge unit

        Returns:
            The knowledge unit

        Raises:
            KnowledgeUnitNotFoundError: If the unit doesn't exist
        """
        if unit_id not in self._knowledge_units:
            raise KnowledgeUnitNotFoundError(f"Knowledge unit {unit_id} not found")
        return self._knowledge_units[unit_id]

    def list_knowledge_units(
        self,
        strategy: ConsolidationStrategy | None = None,
        limit: int = 20,
    ) -> list[KnowledgeUnit]:
        """List all knowledge units.

        Args:
            strategy: Optional filter by consolidation strategy
            limit: Maximum number to return

        Returns:
            List of knowledge units
        """
        units = list(self._knowledge_units.values())

        if strategy:
            units = [u for u in units if u.consolidation_strategy == strategy]

        # Sort by creation date, newest first
        units.sort(key=lambda u: u.created_at, reverse=True)

        return units[:limit]

    def get_consolidated_view(
        self,
        topic: str,
        include_conflicts: bool = True,
    ) -> dict[str, Any]:
        """Get a consolidated view of knowledge on a topic.

        Returns a comprehensive view including the knowledge unit,
        related memories, and any detected conflicts.

        Args:
            topic: The topic to get consolidated view for
            include_conflicts: Whether to include conflict information

        Returns:
            Dictionary with consolidated view data
        """
        # Consolidate memories for this topic
        units = self.consolidate_by_topic(topic=topic)

        if not units:
            return {
                "topic": topic,
                "knowledge_units": [],
                "conflicts": [],
                "summary": f"No consolidated knowledge found for topic: {topic}",
            }

        # Detect conflicts if requested
        conflicts = []
        if include_conflicts:
            conflicts = self.detect_conflicts(topic=topic)

        # Build consolidated view
        return {
            "topic": topic,
            "knowledge_units": [u.to_dict() for u in units],
            "conflicts": [c.to_dict() for c in conflicts],
            "summary": self._build_consolidated_summary(units, conflicts),
            "total_memories": sum(len(u.memory_refs) for u in units),
            "conflict_count": len(conflicts),
        }

    def _build_consolidated_summary(
        self,
        units: list[KnowledgeUnit],
        conflicts: list[MemoryConflict],
    ) -> str:
        """Build a human-readable summary of the consolidated view.

        Args:
            units: Knowledge units to summarize
            conflicts: Any detected conflicts

        Returns:
            Summary string
        """
        if not units:
            return "No knowledge units found."

        unit_count = len(units)
        memory_count = sum(len(u.memory_refs) for u in units)
        conflict_count = len(conflicts)

        parts = [
            f"Found {unit_count} knowledge unit(s) covering {memory_count} memory(s).",
        ]

        if conflict_count > 0:
            high_conflicts = sum(1 for c in conflicts if c.severity == ConflictSeverity.HIGH)
            if high_conflicts > 0:
                parts.append(f"WARNING: {high_conflicts} high-severity conflict(s) detected.")
            else:
                parts.append(f"{conflict_count} conflict(s) detected for review.")

        return " ".join(parts)

    def resolve_conflict(
        self,
        conflict_id: str,
        resolution: str,
    ) -> MemoryConflict:
        """Mark a conflict as resolved.

        Args:
            conflict_id: The ID of the conflict to resolve
            resolution: Resolution description

        Returns:
            Updated MemoryConflict

        Raises:
            ConsolidationServiceError: If conflict not found
        """
        conflict = next((c for c in self._conflicts if c.id == conflict_id), None)

        if not conflict:
            raise ConsolidationServiceError(f"Conflict {conflict_id} not found")

        conflict.resolution_status = "resolved"
        conflict.conflict_description = resolution

        return conflict

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about consolidation state.

        Returns:
            Dictionary with counts and metrics
        """
        total_units = len(self._knowledge_units)
        by_strategy: dict[str, int] = defaultdict(int)

        for unit in self._knowledge_units.values():
            by_strategy[unit.consolidation_strategy.value] += 1

        total_conflicts = len(self._conflicts)
        unresolved = sum(1 for c in self._conflicts if c.resolution_status == "unresolved")

        return {
            "total_knowledge_units": total_units,
            "by_strategy": dict(by_strategy),
            "total_conflicts": total_conflicts,
            "unresolved_conflicts": unresolved,
            "resolved_conflicts": total_conflicts - unresolved,
        }
