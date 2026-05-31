"""GraphRAG search service for querying the knowledge graph.

Provides search capabilities that combine keyword matching on entity
names with graph traversal to retrieve contextual neighborhoods around
matching entities. This enables agents to find connected knowledge
that simple text or vector search cannot discover.

Search features:
- Keyword search on entity names (case-insensitive, partial matching)
- Graph traversal to retrieve connected entities and relationships
- Relevance scoring combining name match and graph connectivity
- Entity type filtering for focused queries
- Contextual results with surrounding graph neighborhood

The search service defaults to approved-only results to ensure
agents only see knowledge that has been verified by humans.
"""

from __future__ import annotations

from omnivia_memory.graph.models import (
    ApprovalStatus,
    Entity,
    EntityType,
)
from omnivia_memory.graph.repository import EntityRepository, RelationshipRepository
from omnivia_memory.graph.search_models import (
    GraphSearchQuery,
    GraphSearchResult,
    GraphSearchResultSet,
    compute_relevance_score,
    score_name_match,
)


class GraphSearchError(Exception):
    """Base exception for search service errors."""

    pass


class GraphSearchService:
    """Search service for GraphRAG queries on the knowledge graph.

    Combines keyword search with graph traversal to provide contextual
    search results. Search results include the matched entity plus
    its surrounding graph neighborhood for rich context.

    The service filters to approved-only entities by default,
    ensuring agents only retrieve human-verified knowledge.

    Attributes:
        entity_repository: Repository for entity queries
        relationship_repository: Repository for relationship queries
        default_limit: Default maximum results when not specified
    """

    # Default limit prevents unbounded queries that could return
    # thousands of results and degrade performance.
    DEFAULT_LIMIT = 10

    # Maximum traversal depth to prevent expensive multi-hop
    # traversals that could degrade query performance.
    MAX_DEPTH = 3

    def __init__(
        self,
        entity_repository: EntityRepository | None = None,
        relationship_repository: RelationshipRepository | None = None,
    ) -> None:
        self.entity_repository = entity_repository
        self.relationship_repository = relationship_repository

    def search_entities(
        self,
        query: str,
        entity_types: list[str | EntityType] | None = None,
        limit: int = 10,
    ) -> list[Entity]:
        """Search for entities by name using keyword matching.

        Performs case-insensitive substring matching on entity names.
        Results are filtered to approved entities only by default.

        Args:
            query: Search text to match against entity names
            entity_types: Optional filter to only these entity types
            limit: Maximum number of results to return (default 10)

        Returns:
            List of matching entities ordered by name match quality

        Raises:
            GraphSearchError: If repositories are not configured
        """
        if not self.entity_repository:
            raise GraphSearchError("Entity repository not configured")

        # Retrieve candidates based on type filter
        candidates = self._get_candidates(entity_types)

        # Score each candidate by name match quality
        scored: list[tuple[Entity, float]] = []
        for entity in candidates:
            score = score_name_match(query, entity.name)
            if score > 0:
                scored.append((entity, score))

        # Sort by score descending, then by name ascending
        scored.sort(key=lambda x: (-x[1], x[0].name))

        # Return top results up to limit
        return [entity for entity, _ in scored[:limit]]

    def search_with_context(
        self,
        query: str,
        depth: int = 1,
        limit: int = 10,
    ) -> GraphSearchResultSet:
        """Search for entities and return results with graph context.

        Combines keyword matching with graph traversal. Each result
        includes the matched entity plus surrounding entities found
        by traversing relationships up to the specified depth.

        Args:
            query: Search text to match against entity names
            depth: How many relationship hops to traverse (default 1)
            limit: Maximum number of primary results (default 10)

        Returns:
            GraphSearchResultSet containing matched results with context

        Raises:
            GraphSearchError: If repositories are not configured
        """
        if not self.entity_repository:
            raise GraphSearchError("Entity repository not configured")

        # Clamp depth to prevent expensive traversals
        depth = min(max(1, depth), self.MAX_DEPTH)

        # Build the search query for metadata
        search_query = GraphSearchQuery(
            query=query,
            depth=depth,
            limit=limit,
        )

        # Get all approved entities as candidates
        all_candidates = self._get_candidates(None)

        # Score and rank candidates
        scored: list[tuple[Entity, float, list[Entity]]] = []
        for entity in all_candidates:
            # Get neighbors for context and scoring
            context = self._traverse_neighbors(entity.id, depth)
            neighbor_names = [e.name for e in context]

            # Compute composite relevance score
            score = compute_relevance_score(
                query=query,
                entity_name=entity.name,
                outgoing_relationships=0,  # Simplified scoring for now
                incoming_relationships=0,
                neighbor_names=neighbor_names,
            )

            if score > 0:
                scored.append((entity, score, context))

        # Sort by score descending
        scored.sort(key=lambda x: -x[1])

        # Build result set
        results: list[GraphSearchResult] = []
        for entity, score, context in scored[:limit]:
            matched_on = self._describe_match(query, entity.name)
            result = GraphSearchResult(
                entity=entity,
                score=score,
                matched_on=matched_on,
                context_entities=context,
            )
            results.append(result)

        return GraphSearchResultSet(
            results=results,
            total_count=len(scored),
            query=search_query,
        )

    def get_entity_context(
        self,
        entity_id: str,
        depth: int = 1,
    ) -> list[tuple[Entity, list[Entity]]]:
        """Get the contextual neighborhood around an entity.

        Traverses the graph from the specified entity, collecting
        connected entities at each depth level. This provides
        rich context about an entity's role in the knowledge graph.

        Args:
            entity_id: ID of the central entity
            depth: How many relationship hops to traverse (default 1)

        Returns:
            List of (entity, neighbors) tuples for each entity in traversal,
            starting with the central entity and expanding outward

        Raises:
            GraphSearchError: If the entity is not found
        """
        if not self.entity_repository or not self.relationship_repository:
            raise GraphSearchError("Repositories not configured")

        # Verify the entity exists
        entity = self.entity_repository.get(entity_id)
        if entity is None:
            raise GraphSearchError(f"Entity {entity_id} not found")

        # Clamp depth
        depth = min(max(1, depth), self.MAX_DEPTH)

        # Traverse the graph
        result: list[tuple[Entity, list[Entity]]] = []
        visited: set[str] = {entity_id}

        # Start with the central entity
        current_level = [(entity, depth)]

        while depth > 0:
            next_level: list[tuple[Entity, int]] = []

            for current_entity, current_depth in current_level:
                neighbors = self._traverse_neighbors(current_entity.id, 1)
                result.append((current_entity, neighbors))

                # Queue neighbors for next level traversal
                if current_depth > 1:
                    for neighbor_entity in neighbors:
                        if neighbor_entity.id not in visited:
                            visited.add(neighbor_entity.id)
                            next_level.append((neighbor_entity, current_depth - 1))

            current_level = next_level
            depth -= 1

        return result

    def _get_candidates(
        self,
        entity_types: list[str | EntityType] | None,
    ) -> list[Entity]:
        """Retrieve candidate entities filtered by type and status.

        Only returns approved entities to ensure agents see verified
        knowledge. Type filtering is optional.

        Args:
            entity_types: Optional list of types to filter by

        Returns:
            List of candidate entities
        """
        if not self.entity_repository:
            return []

        # Convert string types to EntityType if needed
        types: list[EntityType] = []
        if entity_types:
            for et in entity_types:
                if isinstance(et, str):
                    types.append(EntityType(et))
                else:
                    types.append(et)

        # Get candidates by type or all entities
        if types:
            candidates: list[Entity] = []
            for entity_type in types:
                candidates.extend(self.entity_repository.list_by_type(entity_type))
        else:
            candidates = self.entity_repository.list_all(limit=10000)

        # Filter to approved-only by default
        # This ensures agents only see human-verified knowledge
        return [e for e in candidates if e.approval_status == ApprovalStatus.APPROVED]

    def _traverse_neighbors(
        self,
        entity_id: str,
        depth: int,
    ) -> list[Entity]:
        """Traverse the graph from an entity to collect neighbors.

        Args:
            entity_id: Starting entity ID
            depth: Maximum traversal depth

        Returns:
            List of neighboring entities found
        """
        if not self.relationship_repository:
            return []

        visited: set[str] = {entity_id}
        neighbors: list[Entity] = []

        current_ids = {entity_id}
        current_depth = 0

        while current_depth < depth and current_ids:
            next_ids: set[str] = set()

            for current_id in current_ids:
                # Get neighbors via relationships
                related = self.relationship_repository.get_neighbors(current_id)

                for neighbor_entity, _ in related:
                    if neighbor_entity.id not in visited:
                        visited.add(neighbor_entity.id)
                        neighbors.append(neighbor_entity)
                        next_ids.add(neighbor_entity.id)

            current_ids = next_ids
            current_depth += 1

        return neighbors

    def _describe_match(self, query: str, entity_name: str) -> str:
        """Describe how an entity matched the search query.

        Args:
            query: The search query
            entity_name: The entity name that matched

        Returns:
            Human-readable description of the match
        """
        query_lower = query.lower()
        name_lower = entity_name.lower()

        if query_lower == name_lower:
            return "exact name match"
        elif query_lower in name_lower:
            return f"name contains '{query}'"
        elif any(word in name_lower for word in query_lower.split()):
            return "keyword overlap"
        else:
            return "contextual match"
