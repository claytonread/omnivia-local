"""GraphRAG search models for OmniVia.

Provides query and result models for graph-based retrieval augmented
generation. These models support searching the knowledge graph by
entity types, relationship types, and traversal depth.

GraphRAG enables agents to find connected knowledge beyond what
keyword or vector search alone can discover. For example, an agent
can find "all people who depend on the system that handles payments"
in a single query.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from omnivia_memory.graph.models import Entity, EntityType, RelationshipType


@dataclass
class GraphSearchQuery:
    """A query specification for searching the knowledge graph.

    GraphRAG queries traverse the graph from matching starting nodes,
    following relationships up to a specified depth. This enables
    finding connected entities that share indirect relationships.

    Example use case: "Find all technologies used by projects that
    depend on the authentication system, up to 2 hops away."

    Attributes:
        query: Natural language text describing what to find.
            This is used for semantic matching against entity names.
        entity_types: Filter to only include entities of these types.
            Empty list means no type filter (search all types).
        relationship_types: Filter to only follow these relationship
            types during traversal. Empty list means follow all types.
        depth: How many relationship hops to traverse from matched
            starting entities. Depth1 means immediate neighbors only.
        limit: Maximum number of results to return. Use None for
            service-defined default limit.
    """

    query: str
    entity_types: list[EntityType] = field(default_factory=list)
    relationship_types: list[RelationshipType] = field(default_factory=list)
    depth: int = 1
    limit: int | None = None

    def __post_init__(self) -> None:
        """Validate query parameters after initialization."""
        if self.depth < 0:
            raise ValueError("Depth must be non-negative")
        if self.limit is not None and self.limit < 1:
            raise ValueError("Limit must be at least 1")

    def to_dict(self) -> dict[str, Any]:
        """Convert query to dictionary for serialization.

        Returns:
            Dictionary representation of the query
        """
        return {
            "query": self.query,
            "entity_types": [t.value for t in self.entity_types],
            "relationship_types": [t.value for t in self.relationship_types],
            "depth": self.depth,
            "limit": self.limit,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GraphSearchQuery:
        """Create a query from a dictionary.

        Args:
            data: Dictionary with query fields

        Returns:
            GraphSearchQuery instance
        """
        return cls(
            query=data["query"],
            entity_types=[EntityType(t) for t in data.get("entity_types", [])],
            relationship_types=[RelationshipType(t) for t in data.get("relationship_types", [])],
            depth=data.get("depth", 1),
            limit=data.get("limit"),
        )


@dataclass
class GraphSearchResult:
    """A single result from a GraphRAG search.

    Contains a matched entity along with relevance scoring and
    contextual information about related entities found during
    graph traversal.

    Attributes:
        entity: The matched entity that satisfied the search query
        score: Relevance score between 0.0 (not relevant) and 1.0
            (perfect match). Based on name match, relationship count,
            and neighbor overlap with the query.
        matched_on: What caused this entity to match. Typically
            the entity name or a relationship path description.
        context_entities: Other entities found during traversal that
            are connected to the matched entity. These provide
            surrounding context for the result.
    """

    entity: Entity
    score: float
    matched_on: str
    context_entities: list[Entity] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate result fields after initialization."""
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("Score must be between 0.0 and 1.0")

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary for serialization.

        Returns:
            Dictionary representation of the result
        """
        return {
            "entity": self.entity.to_dict(),
            "score": self.score,
            "matched_on": self.matched_on,
            "context_entities": [e.to_dict() for e in self.context_entities],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GraphSearchResult:
        """Create a result from a dictionary.

        Args:
            data: Dictionary with result fields

        Returns:
            GraphSearchResult instance
        """
        return cls(
            entity=Entity.from_dict(data["entity"]),
            score=data["score"],
            matched_on=data["matched_on"],
            context_entities=[Entity.from_dict(e) for e in data.get("context_entities", [])],
        )


@dataclass
class GraphSearchResultSet:
    """A collection of GraphRAG search results with query metadata.

    Provides a complete response to a GraphSearchQuery, including
    all matched results, total count information, and a reference
    back to the original query for context.

    Attributes:
        results: The ordered list of results, sorted by score
            (highest relevance first)
        total_count: Total number of entities that matched the query,
            before applying the limit. Useful for pagination UI.
        query: The original search query that produced these results.
            Useful for result context and debugging.
    """

    results: list[GraphSearchResult]
    total_count: int
    query: GraphSearchQuery

    def to_dict(self) -> dict[str, Any]:
        """Convert result set to dictionary for serialization.

        Returns:
            Dictionary representation of the result set
        """
        return {
            "results": [r.to_dict() for r in self.results],
            "total_count": self.total_count,
            "query": self.query.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GraphSearchResultSet:
        """Create a result set from a dictionary.

        Args:
            data: Dictionary with result set fields

        Returns:
            GraphSearchResultSet instance
        """
        return cls(
            results=[GraphSearchResult.from_dict(r) for r in data["results"]],
            total_count=data["total_count"],
            query=GraphSearchQuery.from_dict(data["query"]),
        )


# ---------------------------------------------------------------------------
# Relevance Scoring Helpers
# ---------------------------------------------------------------------------
# These helper functions compute relevance scores for GraphRAG search.
# Scores combine multiple signals: name match quality, relationship
# density, and neighbor overlap with the query intent.


def score_name_match(query: str, entity_name: str) -> float:
    """Score how well an entity name matches the query text.

    Uses case-insensitive substring matching. A perfect match (query
    equals name) scores 1.0, while a partial match scores proportionally
    to the match length relative to the query.

    This provides a baseline signal that can be combined with other
    signals for a composite relevance score.

    Args:
        query: The search query text
        entity_name: The name of the entity to score

    Returns:
        Match score between 0.0 and 1.0
    """
    if not query or not entity_name:
        return 0.0

    query_lower = query.lower()
    name_lower = entity_name.lower()

    # Exact match gets full score
    if query_lower == name_lower:
        return 1.0

    # Substring match gets partial score based on coverage
    if query_lower in name_lower:
        return len(query_lower) / len(name_lower)

    # Check for word-level overlap
    query_words = set(query_lower.split())
    name_words = set(name_lower.split())

    if query_words and name_words:
        overlap = len(query_words & name_words)
        return overlap / len(query_words)

    return 0.0


def score_relationship_count(outgoing: int, incoming: int) -> float:
    """Score based on the number of relationships an entity has.

    Entities with more connections are often more central to the
    knowledge graph and thus potentially more relevant. However,
    we cap the score to avoid overly weighting highly-connected
    "hub" entities that might be too general.

    Args:
        outgoing: Number of outgoing (source) relationships
        incoming: Number of incoming (target) relationships

    Returns:
        Relationship density score between 0.0 and 1.0
    """
    total = outgoing + incoming

    # Score increases logarithmically, capped at 1.0
    # 10 relationships = ~0.5, 100 = ~0.7, 1000 = ~0.8
    if total <= 0:
        return 0.0

    import math

    return min(1.0, math.log2(total + 1) / 10.0)


def score_neighbor_overlap(neighbors: list[str], query_keywords: list[str]) -> float:
    """Score based on overlap between entity neighbors and query keywords.

    When neighboring entities share keywords with the query, the matched
    entity is likely more contextually relevant. This captures the
    "surrounding context" signal in graph traversal.

    Args:
        neighbors: List of names of neighboring entities
        query_keywords: Extracted keywords from the search query

    Returns:
        Neighbor overlap score between 0.0 and 1.0
    """
    if not neighbors or not query_keywords:
        return 0.0

    # Convert neighbors to lowercase for comparison
    neighbor_set = set(n.lower() for n in neighbors)
    keyword_set = set(k.lower() for k in query_keywords)

    overlap = len(neighbor_set & keyword_set)
    return overlap / len(keyword_set) if keyword_set else 0.0


def compute_relevance_score(
    query: str,
    entity_name: str,
    outgoing_relationships: int = 0,
    incoming_relationships: int = 0,
    neighbor_names: list[str] | None = None,
    name_weight: float = 0.5,
    relationship_weight: float = 0.25,
    neighbor_weight: float = 0.25,
) -> float:
    """Compute a composite relevance score for a GraphRAG result.

    Combines multiple signals into a single score that reflects how
    well an entity matches the search query:
    - Name match: How well the entity name matches the query text
    - Relationship count: How connected the entity is in the graph
    - Neighbor overlap: How many neighboring entities share query keywords

    Weights are normalized to sum to 1.0, so the weights parameter
    is only used to distribute importance across signals.

    Args:
        query: The search query text
        entity_name: The name of the entity being scored
        outgoing_relationships: Count of outgoing relationships
        incoming_relationships: Count of incoming relationships
        neighbor_names: Names of neighboring entities for context scoring
        name_weight: Weight for name match signal (default 0.5)
        relationship_weight: Weight for relationship count signal (default 0.25)
        neighbor_weight: Weight for neighbor overlap signal (default 0.25)

    Returns:
        Composite relevance score between 0.0 and 1.0
    """
    # Normalize weights to sum to 1.0
    total_weight = name_weight + relationship_weight + neighbor_weight
    if total_weight <= 0:
        return 0.0

    name_weight /= total_weight
    relationship_weight /= total_weight
    neighbor_weight /= total_weight

    # Extract keywords from query for neighbor matching
    query_keywords = query.lower().split()

    # Compute individual scores
    name_score = score_name_match(query, entity_name)
    rel_score = score_relationship_count(outgoing_relationships, incoming_relationships)
    neighbor_score = score_neighbor_overlap(neighbor_names or [], query_keywords)

    # Weighted combination
    composite = (
        name_score * name_weight
        + rel_score * relationship_weight
        + neighbor_score * neighbor_weight
    )

    return round(composite, 4)
