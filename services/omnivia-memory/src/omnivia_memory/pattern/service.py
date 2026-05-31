"""Pattern detection service for OmniVia.

Analyzes stored memories to identify recurring patterns in:
- Content: Similar knowledge appearing multiple times
- Sources: Same source generating multiple related memories
- Lifecycle: Common state transition patterns

Agent-created patterns default to "proposed" so humans can verify
detected patterns before they influence agent reasoning.
"""

from __future__ import annotations

import re
from collections import defaultdict
from difflib import SequenceMatcher
from typing import TYPE_CHECKING, Any

from omnivia_memory.pattern.models import (
    PatternCreate,
    PatternEntity,
    PatternOccurrence,
    PatternType,
)

if TYPE_CHECKING:
    from omnivia_memory.pattern.repository import PatternRepository


class PatternServiceError(Exception):
    """Base exception for pattern service errors."""

    pass


class PatternNotFoundError(PatternServiceError):
    """Raised when a requested pattern does not exist."""

    pass


class PatternValidationError(PatternServiceError):
    """Raised when pattern validation fails."""

    pass


class PatternService:
    """Service for detecting and managing patterns in memories.

    Analyzes stored memories to identify recurring patterns across:
    - Content similarity (similar knowledge being stored)
    - Source patterns (same source generating multiple memories)
    - Lifecycle transitions (common approval paths)

    Detected patterns are stored as PatternEntity objects in "proposed"
    state for human review before they influence agent reasoning.

    Attributes:
        pattern_repository: Optional repository for pattern persistence
        memory_service: Service for accessing stored memories
    """

    # Minimum similarity threshold for content similarity detection
    SIMILARITY_THRESHOLD = 0.7

    # Minimum occurrences to create a pattern
    MIN_OCCURRENCES = 2

    def __init__(
        self,
        pattern_repository: PatternRepository | None = None,
        memory_service: Any | None = None,
    ) -> None:
        self.pattern_repository = pattern_repository
        self.memory_service = memory_service

    def detect_all_patterns(
        self,
        memories: list[Any],
        min_occurrences: int | None = None,
    ) -> list[PatternEntity]:
        """Detect all pattern types in the provided memories.

        Runs all detection algorithms and returns patterns that meet
        the minimum occurrence threshold.

        Args:
            memories: List of memory objects to analyze
            min_occurrences: Override for minimum occurrence count (default: 2)

        Returns:
            List of detected patterns in proposed state
        """
        if min_occurrences is None:
            min_occurrences = self.MIN_OCCURRENCES

        patterns: list[PatternEntity] = []

        # Detect content similarity patterns
        content_patterns = self._detect_content_similarity(memories, min_occurrences)
        patterns.extend(content_patterns)

        # Detect source cluster patterns
        source_patterns = self._detect_source_clusters(memories, min_occurrences)
        patterns.extend(source_patterns)

        # Detect lifecycle transition patterns
        lifecycle_patterns = self._detect_lifecycle_transitions(memories, min_occurrences)
        patterns.extend(lifecycle_patterns)

        return patterns

    def _detect_content_similarity(
        self,
        memories: list[Any],
        min_occurrences: int,
    ) -> list[PatternEntity]:
        """Detect memories with similar content.

        Groups memories by content similarity using sequence matching.
        Memories with similarity above threshold are grouped together.

        Args:
            memories: List of memory objects
            min_occurrences: Minimum group size to create a pattern

        Returns:
            List of content similarity patterns
        """
        patterns: list[PatternEntity] = []
        processed: set[str] = set()

        for i, memory in enumerate(memories):
            if memory.id in processed:
                continue

            # Find similar memories
            similar_group = [memory]
            similar_ids: set[str] = {memory.id}

            for j, other in enumerate(memories):
                if i >= j or other.id in processed:
                    continue

                similarity = self._calculate_similarity(memory.content, other.content)

                if similarity >= self.SIMILARITY_THRESHOLD:
                    similar_group.append(other)
                    similar_ids.add(other.id)

            # Only create pattern if enough similar memories found
            if len(similar_group) >= min_occurrences:
                # Extract common terms for the pattern name
                common_terms = self._extract_common_terms([m.content for m in similar_group])

                pattern = PatternEntity(
                    name=f"Similar content: {common_terms}",
                    pattern_type=PatternType.CONTENT_SIMILARITY,
                    description=(
                        f"Found {len(similar_group)} memories with similar content "
                        f"(similarity >= {self.SIMILARITY_THRESHOLD:.0%}). "
                        f"This may indicate duplicate or related knowledge."
                    ),
                    confidence=sum(
                        self._calculate_similarity(m.content, similar_group[0].content)
                        for m in similar_group
                    )
                    / len(similar_group),
                    occurrence_count=len(similar_group),
                    source_id=memory.source.reference if hasattr(memory, "source") else None,
                )
                patterns.append(pattern)

                # Mark all memories in group as processed
                processed.update(similar_ids)

        return patterns

    def _detect_source_clusters(
        self,
        memories: list[Any],
        min_occurrences: int,
    ) -> list[PatternEntity]:
        """Detect memories from the same source.

        Groups memories by their source reference. Sources generating
        multiple memories may indicate a pattern in how knowledge is
        being captured.

        Args:
            memories: List of memory objects
            min_occurrences: Minimum memories from same source

        Returns:
            List of source cluster patterns
        """
        patterns: list[PatternEntity] = []

        # Group memories by source reference
        source_groups: dict[str, list[Any]] = defaultdict(list)
        for memory in memories:
            if hasattr(memory, "source") and hasattr(memory.source, "reference"):
                source_groups[memory.source.reference].append(memory)

        # Create patterns for sources with multiple memories
        for source_ref, group in source_groups.items():
            if len(group) >= min_occurrences:
                memory_types = [m.memory_type for m in group if hasattr(m, "memory_type")]
                type_counts: dict[str, int] = defaultdict(int)
                for t in memory_types:
                    type_counts[t] += 1

                most_common_type = max(type_counts.items(), key=lambda x: x[1])[0]

                pattern = PatternEntity(
                    name=f"Source cluster: {source_ref}",
                    pattern_type=PatternType.SOURCE_CLUSTER,
                    description=(
                        f"Source '{source_ref}' generated {len(group)} memories. "
                        f"Most common type: {most_common_type} ({type_counts[most_common_type]} occurrences). "
                        f"This indicates consistent knowledge capture from this source."
                    ),
                    confidence=min(1.0, len(group) / 5.0),  # Higher count = higher confidence
                    occurrence_count=len(group),
                    source_id=source_ref,
                )
                patterns.append(pattern)

        return patterns

    def _detect_lifecycle_transitions(
        self,
        memories: list[Any],
        min_occurrences: int,
    ) -> list[PatternEntity]:
        """Detect common lifecycle state transitions.

        Analyzes how memories move between lifecycle states (proposed ->
        approved, proposed -> rejected, etc.) to identify common paths.

        Args:
            memories: List of memory objects
            min_occurrences: Minimum occurrences of a transition path

        Returns:
            List of lifecycle transition patterns
        """
        patterns: list[PatternEntity] = []

        # Count transitions by source state
        transition_counts: dict[tuple[str, str], int] = defaultdict(int)
        transition_memories: dict[tuple[str, str], list[str]] = defaultdict(list)

        for memory in memories:
            if hasattr(memory, "lifecycle_state") and hasattr(memory, "created_by"):
                # Group by creation state and creator
                key = (memory.lifecycle_state.value, memory.created_by.value)
                transition_counts[key] += 1
                transition_memories[key].append(memory.id)

        # Create patterns for common transitions
        for (state, creator), count in transition_counts.items():
            if count >= min_occurrences:
                pattern = PatternEntity(
                    name=f"Lifecycle pattern: {creator} creates {state}",
                    pattern_type=PatternType.LIFECYCLE_TRANSITION,
                    description=(
                        f"Creator type '{creator}' frequently creates memories "
                        f"in '{state}' state. Observed {count} times. "
                        f"This reflects the knowledge capture workflow."
                    ),
                    confidence=min(1.0, count / 10.0),
                    occurrence_count=count,
                )
                patterns.append(pattern)

        return patterns

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings.

        Uses sequence matching to find common subsequences. Returns
        a value between 0.0 (completely different) and 1.0 (identical).

        Args:
            text1: First text string
            text2: Second text string

        Returns:
            Similarity ratio (0.0 to 1.0)
        """
        # Normalize whitespace and convert to lowercase
        norm1 = re.sub(r"\s+", " ", text1.lower().strip())
        norm2 = re.sub(r"\s+", " ", text2.lower().strip())

        # Use SequenceMatcher for efficient similarity calculation
        matcher = SequenceMatcher(None, norm1, norm2)
        return matcher.ratio()

    def _extract_common_terms(self, contents: list[str]) -> str:
        """Extract common terms from a list of content strings.

        Identifies the most frequent meaningful words (excluding common
        stop words) to create a descriptive pattern name.

        Args:
            contents: List of content strings

        Returns:
            String of common terms joined by spaces
        """
        # Common English stop words to exclude
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "as",
            "is",
            "was",
            "are",
            "were",
            "been",
            "be",
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
            "that",
            "this",
            "these",
            "those",
            "it",
            "its",
            "they",
            "them",
            "their",
            "we",
            "us",
            "our",
            "you",
            "your",
            "he",
            "she",
            "him",
            "her",
        }

        # Count word frequencies across all contents
        word_counts: dict[str, int] = defaultdict(int)
        for content in contents:
            # Extract words (alphabetic sequences)
            words = re.findall(r"[a-z]+", content.lower())
            for word in words:
                if word not in stop_words and len(word) > 2:
                    word_counts[word] += 1

        # Get top terms by frequency
        sorted_terms = sorted(word_counts.items(), key=lambda x: -x[1])
        top_terms = [term for term, _ in sorted_terms[:3]]

        return " ".join(top_terms) if top_terms else "various topics"

    def create_pattern(self, pattern_create: PatternCreate) -> PatternEntity:
        """Create a new pattern from detection results.

        Agent-created patterns default to "proposed" so humans can
        verify the detected pattern is accurate.

        Args:
            pattern_create: Pattern creation input

        Returns:
            The created pattern in proposed state
        """
        # Validate confidence is in valid range
        if not 0.0 <= pattern_create.confidence <= 1.0:
            raise PatternValidationError(
                f"Confidence must be between 0.0 and 1.0, got {pattern_create.confidence}"
            )

        pattern = PatternEntity(
            name=pattern_create.name,
            pattern_type=pattern_create.pattern_type,
            description=pattern_create.description,
            confidence=pattern_create.confidence,
            occurrence_count=pattern_create.occurrence_count,
            source_id=pattern_create.source_id,
        )

        # Persist if repository is configured
        if self.pattern_repository:
            self.pattern_repository.create(pattern)

        return pattern

    def get_pattern(self, pattern_id: str) -> PatternEntity:
        """Retrieve a pattern by its ID.

        Args:
            pattern_id: The unique identifier of the pattern

        Returns:
            The pattern

        Raises:
            PatternNotFoundError: If the pattern doesn't exist
        """
        if not self.pattern_repository:
            raise PatternServiceError("Pattern repository not configured")

        pattern = self.pattern_repository.get(pattern_id)
        if pattern is None:
            raise PatternNotFoundError(f"Pattern {pattern_id} not found")
        return pattern

    def list_patterns(
        self,
        pattern_type: PatternType | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[PatternEntity]:
        """List patterns with optional filtering.

        Args:
            pattern_type: Optional filter by pattern type
            limit: Maximum number of patterns to return
            offset: Number of patterns to skip

        Returns:
            List of patterns matching the criteria
        """
        if not self.pattern_repository:
            raise PatternServiceError("Pattern repository not configured")

        if pattern_type:
            return self.pattern_repository.list_by_type(pattern_type)
        return self.pattern_repository.list_all(limit=limit, offset=offset)

    def get_pattern_occurrences(
        self,
        pattern_id: str,
    ) -> list[PatternOccurrence]:
        """Get all occurrences of a pattern.

        Returns the memories or evidence that triggered this pattern's
        detection.

        Args:
            pattern_id: The ID of the pattern

        Returns:
            List of occurrences for this pattern

        Raises:
            PatternNotFoundError: If the pattern doesn't exist
        """
        if not self.pattern_repository:
            raise PatternServiceError("Pattern repository not configured")

        # Verify pattern exists
        self.get_pattern(pattern_id)

        return self.pattern_repository.list_occurrences(pattern_id)

    def approve_pattern(self, pattern_id: str) -> PatternEntity:
        """Approve a pattern (transition to approved state).

        Args:
            pattern_id: The ID of the pattern to approve

        Returns:
            The approved pattern

        Raises:
            PatternNotFoundError: If the pattern doesn't exist
        """
        pattern = self.get_pattern(pattern_id)

        if pattern.approval_status == "rejected":
            raise PatternValidationError("Cannot approve pattern in rejected state")

        if pattern.approval_status == "approved":
            raise PatternValidationError("Pattern is already approved")

        pattern.approve()

        if self.pattern_repository:
            self.pattern_repository.update(pattern)

        return pattern

    def reject_pattern(self, pattern_id: str) -> PatternEntity:
        """Reject a pattern.

        Args:
            pattern_id: The ID of the pattern to reject

        Returns:
            The rejected pattern

        Raises:
            PatternNotFoundError: If the pattern doesn't exist
        """
        pattern = self.get_pattern(pattern_id)
        pattern.reject()

        if self.pattern_repository:
            self.pattern_repository.update(pattern)

        return pattern

    def delete_pattern(self, pattern_id: str) -> bool:
        """Delete a pattern and its occurrences.

        Args:
            pattern_id: The ID of the pattern to delete

        Returns:
            True if the pattern was deleted

        Raises:
            PatternNotFoundError: If the pattern doesn't exist
        """
        if not self.pattern_repository:
            raise PatternServiceError("Pattern repository not configured")

        # Verify pattern exists
        self.get_pattern(pattern_id)

        return self.pattern_repository.delete(pattern_id)

    def record_occurrence(
        self,
        pattern_id: str,
        memory_id: str,
        evidence: str | None = None,
    ) -> PatternOccurrence:
        """Record that a pattern was detected in a memory.

        Links a specific memory to a pattern, enabling queries like
        "which memories exemplify this pattern?"

        Args:
            pattern_id: The pattern that was detected
            memory_id: The memory that triggered detection
            evidence: Optional description of what matched

        Returns:
            The created occurrence record

        Raises:
            PatternNotFoundError: If the pattern doesn't exist
        """
        if not self.pattern_repository:
            raise PatternServiceError("Pattern repository not configured")

        # Verify pattern exists
        self.get_pattern(pattern_id)

        occurrence = PatternOccurrence(
            pattern_id=pattern_id,
            memory_id=memory_id,
            evidence=evidence,
        )

        return self.pattern_repository.create_occurrence(occurrence)
