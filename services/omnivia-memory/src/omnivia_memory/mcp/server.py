"""MCP server for OmniVia memory operations.

Exposes memory CRUD and lifecycle operations as MCP tools via stdio transport.
AI coding agents can use these tools to store and retrieve source-backed memories.

Usage:
    python -m omnivia_memory.mcp.server
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, TextContent, Tool

from omnivia_memory.lifecycle.models import LifecycleState
from omnivia_memory.lifecycle.rules import CreatedBy
from omnivia_memory.memory.models import Memory, MemoryCreate, MemoryUpdate
from omnivia_memory.memory.service import (
    InvalidTransitionError,
    MemoryNotFoundError,
    MemoryService,
    MemoryServiceError,
)
from omnivia_memory.persistence.database import Database, DatabaseConfig
from omnivia_memory.persistence.repositories import MemoryRepository
from omnivia_memory.provenance.models import Source, SourceType

# Import graph modules
from omnivia_memory.graph.models import Entity, Relationship
from omnivia_memory.graph.repository import EntityRepository, RelationshipRepository
from omnivia_memory.graph.service import (
    GraphService,
)


# Server instance name
SERVER_NAME = "omnivia-memory"


def create_graph_service() -> GraphService:
    """Create a configured graph service with SQLite persistence.

    Returns:
        Configured GraphService instance
    """
    # Import graph modules here to avoid circular imports
    from omnivia_memory.graph.service import GraphService

    home = Path.home()
    db_dir = home / ".omnivia"
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / "memories.db"

    config = DatabaseConfig(db_path=db_path)
    db = Database(config)
    db.connect()

    entity_repo = EntityRepository(db)
    relationship_repo = RelationshipRepository(db)
    return GraphService(entity_repository=entity_repo, relationship_repository=relationship_repo)


def entity_to_dict(entity: Entity) -> dict[str, Any]:
    """Convert an entity to a JSON-serializable dictionary.

    Args:
        entity: Entity object

    Returns:
        Dictionary representation
    """
    return {
        "id": entity.id,
        "name": entity.name,
        "entity_type": entity.entity_type.value,
        "source_id": entity.source_id,
        "approval_status": entity.approval_status.value,
        "created_at": entity.created_at,
        "updated_at": entity.updated_at,
    }


def relationship_to_dict(relationship: Relationship) -> dict[str, Any]:
    """Convert a relationship to a JSON-serializable dictionary.

    Args:
        relationship: Relationship object

    Returns:
        Dictionary representation
    """
    return {
        "id": relationship.id,
        "source_entity_id": relationship.source_entity_id,
        "target_entity_id": relationship.target_entity_id,
        "relationship_type": relationship.relationship_type.value,
        "source_id": relationship.source_id,
        "approval_status": relationship.approval_status.value,
        "created_at": relationship.created_at,
        "updated_at": relationship.updated_at,
    }


def create_memory_service() -> MemoryService:
    """Create a configured memory service with SQLite persistence.

    Returns:
        Configured MemoryService instance
    """
    home = Path.home()
    db_dir = home / ".omnivia"
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / "memories.db"

    config = DatabaseConfig(db_path=db_path)
    db = Database(config)
    db.connect()

    repository = MemoryRepository(db)
    return MemoryService(repository=repository)


def memory_to_dict(memory: Memory) -> dict[str, Any]:
    """Convert a memory to a JSON-serializable dictionary.

    Args:
        memory: Memory object

    Returns:
        Dictionary representation
    """
    return {
        "id": memory.id,
        "content": memory.content,
        "source": memory.source.to_dict(),
        "lifecycle_state": memory.lifecycle_state.value,
        "memory_type": memory.memory_type,
        "created_by": memory.created_by.value,
        "created_at": memory.created_at,
        "updated_at": memory.updated_at,
    }


def error_result(message: str) -> CallToolResult:
    """Create a structured error result using MCP SDK types.

    Args:
        message: Error message to return

    Returns:
        CallToolResult with isError=True
    """
    return CallToolResult(
        content=[TextContent(type="text", text=message)],
        isError=True,
    )


def success_result(data: Any) -> CallToolResult:
    """Create a success result using MCP SDK types.

    Args:
        data: Data to return (will be JSON serialized)

    Returns:
        CallToolResult with isError=False
    """
    return CallToolResult(
        content=[TextContent(type="text", text=json.dumps(data, indent=2))],
        isError=False,
    )


# MCP Tool definitions
TOOLS: list[Tool] = [
    Tool(
        name="memory_store",
        description="Store a new memory with source reference. Agent-created memories start as 'proposed', human-created start as 'approved'.",
        inputSchema={
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The knowledge content to store",
                },
                "source_type": {
                    "type": "string",
                    "enum": ["file", "url", "adr", "human"],
                    "description": "Type of source (file, url, adr, human)",
                },
                "source_reference": {
                    "type": "string",
                    "description": "The source reference (file path, URL, ADR ID, or description)",
                },
                "source_description": {
                    "type": "string",
                    "description": "Optional description of the source",
                },
                "memory_type": {
                    "type": "string",
                    "description": "Type of memory (general, decision, pattern, constraint)",
                    "default": "general",
                },
                "created_by": {
                    "type": "string",
                    "enum": ["human", "agent"],
                    "description": "Who created this memory",
                    "default": "agent",
                },
            },
            "required": ["content", "source_type", "source_reference"],
        },
    ),
    Tool(
        name="memory_list",
        description="List stored memories with optional filtering by lifecycle state.",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of memories to return",
                    "default": 100,
                },
                "offset": {
                    "type": "integer",
                    "description": "Number of memories to skip",
                    "default": 0,
                },
                "lifecycle_state": {
                    "type": "string",
                    "enum": ["proposed", "observed", "approved", "rejected"],
                    "description": "Filter by lifecycle state",
                },
            },
        },
    ),
    Tool(
        name="memory_get",
        description="Retrieve a specific memory by its ID.",
        inputSchema={
            "type": "object",
            "properties": {
                "memory_id": {
                    "type": "string",
                    "description": "The unique identifier of the memory",
                },
            },
            "required": ["memory_id"],
        },
    ),
    Tool(
        name="memory_update",
        description="Update an existing memory's content or type.",
        inputSchema={
            "type": "object",
            "properties": {
                "memory_id": {
                    "type": "string",
                    "description": "The ID of the memory to update",
                },
                "content": {
                    "type": "string",
                    "description": "New content for the memory",
                },
                "memory_type": {
                    "type": "string",
                    "description": "New type for the memory",
                },
            },
            "required": ["memory_id"],
        },
    ),
    Tool(
        name="memory_delete",
        description="Delete a memory by its ID.",
        inputSchema={
            "type": "object",
            "properties": {
                "memory_id": {
                    "type": "string",
                    "description": "The ID of the memory to delete",
                },
            },
            "required": ["memory_id"],
        },
    ),
    Tool(
        name="memory_search",
        description="Search memories by keyword. Phase 1 uses simple text matching.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query string",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results",
                    "default": 20,
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="memory_approve",
        description="Approve a memory, moving it from 'proposed' or 'observed' to 'approved'.",
        inputSchema={
            "type": "object",
            "properties": {
                "memory_id": {
                    "type": "string",
                    "description": "The ID of the memory to approve",
                },
            },
            "required": ["memory_id"],
        },
    ),
    Tool(
        name="memory_reject",
        description="Reject a memory, moving it to 'rejected' state.",
        inputSchema={
            "type": "object",
            "properties": {
                "memory_id": {
                    "type": "string",
                    "description": "The ID of the memory to reject",
                },
            },
            "required": ["memory_id"],
        },
    ),
    # Graph knowledge base tools
    Tool(
        name="graph_create_entity",
        description="Create a new entity in the knowledge graph. Agent-created entities start as 'proposed' for human review.",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Human-readable name for the entity",
                },
                "entity_type": {
                    "type": "string",
                    "enum": [
                        "person",
                        "organization",
                        "concept",
                        "document",
                        "project",
                        "system",
                        "product",
                        "location",
                        "technology",
                        "event",
                        "custom",
                    ],
                    "description": "Category of entity",
                },
                "source_id": {
                    "type": "string",
                    "description": "Optional reference to the evidence/source (e.g., memory_id)",
                },
            },
            "required": ["name", "entity_type"],
        },
    ),
    Tool(
        name="graph_get_entity",
        description="Retrieve a specific entity by its ID.",
        inputSchema={
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "The unique identifier of the entity",
                },
            },
            "required": ["entity_id"],
        },
    ),
    Tool(
        name="graph_list_entities",
        description="List entities in the knowledge graph with optional filtering.",
        inputSchema={
            "type": "object",
            "properties": {
                "entity_type": {
                    "type": "string",
                    "description": "Optional filter by entity type",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of entities to return",
                    "default": 100,
                },
                "offset": {
                    "type": "integer",
                    "description": "Number of entities to skip",
                    "default": 0,
                },
            },
        },
    ),
    Tool(
        name="graph_create_relationship",
        description="Create a relationship between two entities. Agent-created relationships start as 'proposed' for human review.",
        inputSchema={
            "type": "object",
            "properties": {
                "source_entity_id": {
                    "type": "string",
                    "description": "ID of the source entity (where the relationship starts)",
                },
                "target_entity_id": {
                    "type": "string",
                    "description": "ID of the target entity (where the relationship ends)",
                },
                "relationship_type": {
                    "type": "string",
                    "enum": [
                        "relates_to",
                        "depends_on",
                        "part_of",
                        "uses",
                        "implements",
                        "created_by",
                        "maintains",
                        "knows",
                        "leads",
                        "occurs_in",
                    ],
                    "description": "Type of relationship",
                },
                "source_id": {
                    "type": "string",
                    "description": "Optional reference to the evidence/source",
                },
            },
            "required": ["source_entity_id", "target_entity_id", "relationship_type"],
        },
    ),
    Tool(
        name="graph_get_neighbors",
        description="Get all entities directly connected to a given entity (graph traversal).",
        inputSchema={
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "The ID of the entity to get neighbors for",
                },
                "relationship_type": {
                    "type": "string",
                    "description": "Optional filter by relationship type",
                },
            },
            "required": ["entity_id"],
        },
    ),
    Tool(
        name="graph_search",
        description="Search the knowledge graph by keyword and optionally traverse relationships. Returns matching entities with relevance scores and optional neighbor context.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query to match against entity names",
                },
                "entity_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional filter by entity types",
                },
                "depth": {
                    "type": "integer",
                    "description": "Depth of graph traversal to include neighbor context (0=no neighbors, 1=direct neighbors, etc.)",
                    "default": 0,
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of matching entities to return",
                    "default": 20,
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="graph_get_context",
        description="Get an entity with its surrounding graph context. Returns the entity and all connected entities up to the specified depth.",
        inputSchema={
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "The unique identifier of the entity",
                },
                "depth": {
                    "type": "integer",
                    "description": "Depth of graph traversal (1=direct neighbors, 2=neighbors of neighbors, etc.)",
                    "default": 1,
                },
            },
            "required": ["entity_id"],
        },
    ),
]


def handle_memory_store(args: dict[str, Any]) -> CallToolResult:
    """Handle memory_store tool call.

    Args:
        args: Tool arguments

    Returns:
        MCP CallToolResult
    """
    # Validate required fields
    if "source_type" not in args:
        return error_result("Missing required field: source_type")
    if "source_reference" not in args:
        return error_result("Missing required field: source_reference")

    try:
        service = create_memory_service()

        source_type = SourceType(args["source_type"])
        source = Source(
            type=source_type,
            reference=args["source_reference"],
            description=args.get("source_description"),
        )

        created_by = CreatedBy.HUMAN if args.get("created_by") == "human" else CreatedBy.AGENT

        memory_input = MemoryCreate(
            content=args["content"],
            source=source,
            memory_type=args.get("memory_type", "general"),
            created_by=created_by,
        )

        memory = service.create(memory_input)
        return success_result(memory_to_dict(memory))

    except (ValueError, TypeError) as e:
        return error_result(str(e))
    except MemoryServiceError as e:
        return error_result(str(e))


def handle_memory_list(args: dict[str, Any]) -> CallToolResult:
    """Handle memory_list tool call.

    Args:
        args: Tool arguments

    Returns:
        MCP CallToolResult
    """
    try:
        service = create_memory_service()

        state_filter = None
        if args.get("lifecycle_state"):
            state_filter = LifecycleState(args["lifecycle_state"])

        memories = service.list(
            limit=args.get("limit", 100),
            offset=args.get("offset", 0),
            lifecycle_state=state_filter,
        )

        return success_result([memory_to_dict(m) for m in memories])

    except ValueError as e:
        return error_result(str(e))
    except MemoryServiceError as e:
        return error_result(str(e))


def handle_memory_get(args: dict[str, Any]) -> CallToolResult:
    """Handle memory_get tool call.

    Args:
        args: Tool arguments

    Returns:
        MCP CallToolResult
    """
    if "memory_id" not in args:
        return error_result("Missing required field: memory_id")

    try:
        service = create_memory_service()
        memory = service.get(args["memory_id"])
        return success_result(memory_to_dict(memory))

    except MemoryNotFoundError as e:
        return error_result(str(e))
    except MemoryServiceError as e:
        return error_result(str(e))


def handle_memory_update(args: dict[str, Any]) -> CallToolResult:
    """Handle memory_update tool call.

    Args:
        args: Tool arguments

    Returns:
        MCP CallToolResult
    """
    if "memory_id" not in args:
        return error_result("Missing required field: memory_id")

    try:
        service = create_memory_service()

        update_input = MemoryUpdate(
            content=args.get("content"),
            memory_type=args.get("memory_type"),
        )

        memory = service.update(args["memory_id"], update_input)
        return success_result(memory_to_dict(memory))

    except MemoryNotFoundError as e:
        return error_result(str(e))
    except InvalidTransitionError as e:
        return error_result(str(e))
    except MemoryServiceError as e:
        return error_result(str(e))


def handle_memory_delete(args: dict[str, Any]) -> CallToolResult:
    """Handle memory_delete tool call.

    Args:
        args: Tool arguments

    Returns:
        MCP CallToolResult
    """
    if "memory_id" not in args:
        return error_result("Missing required field: memory_id")

    try:
        service = create_memory_service()
        deleted = service.delete(args["memory_id"])

        if deleted:
            return success_result({"deleted": True, "memory_id": args["memory_id"]})
        else:
            return error_result(f"Memory '{args['memory_id']}' not found")

    except MemoryNotFoundError as e:
        return error_result(str(e))
    except MemoryServiceError as e:
        return error_result(str(e))


def handle_memory_search(args: dict[str, Any]) -> CallToolResult:
    """Handle memory_search tool call.

    Args:
        args: Tool arguments

    Returns:
        MCP CallToolResult
    """
    if "query" not in args:
        return error_result("Missing required field: query")

    try:
        service = create_memory_service()
        memories = service.search(
            args["query"],
            limit=args.get("limit", 20),
        )
        return success_result([memory_to_dict(m) for m in memories])

    except MemoryServiceError as e:
        return error_result(str(e))


def handle_memory_approve(args: dict[str, Any]) -> CallToolResult:
    """Handle memory_approve tool call.

    Args:
        args: Tool arguments

    Returns:
        MCP CallToolResult
    """
    if "memory_id" not in args:
        return error_result("Missing required field: memory_id")

    try:
        service = create_memory_service()
        memory = service.approve(args["memory_id"])
        return success_result(memory_to_dict(memory))

    except MemoryNotFoundError as e:
        return error_result(str(e))
    except InvalidTransitionError as e:
        return error_result(str(e))
    except MemoryServiceError as e:
        return error_result(str(e))


def handle_memory_reject(args: dict[str, Any]) -> CallToolResult:
    """Handle memory_reject tool call.

    Args:
        args: Tool arguments

    Returns:
        MCP CallToolResult
    """
    if "memory_id" not in args:
        return error_result("Missing required field: memory_id")

    try:
        service = create_memory_service()
        memory = service.reject(args["memory_id"])
        return success_result(memory_to_dict(memory))

    except MemoryNotFoundError as e:
        return error_result(str(e))
    except InvalidTransitionError as e:
        return error_result(str(e))
    except MemoryServiceError as e:
        return error_result(str(e))


# Graph tool handlers


def handle_graph_create_entity(args: dict[str, Any]) -> CallToolResult:
    """Handle graph_create_entity tool call.

    Creates a new entity in the knowledge graph. Agent-created entities
    start as "proposed" so humans can review before they become authoritative.

    Args:
        args: Tool arguments

    Returns:
        MCP CallToolResult
    """
    if "name" not in args:
        return error_result("Missing required field: name")
    if "entity_type" not in args:
        return error_result("Missing required field: entity_type")

    try:
        service = create_graph_service()

        entity = service.create_entity(
            name=args["name"],
            entity_type=args["entity_type"],
            source_id=args.get("source_id"),
        )

        return success_result(entity_to_dict(entity))

    except Exception as e:
        return error_result(str(e))


def handle_graph_get_entity(args: dict[str, Any]) -> CallToolResult:
    """Handle graph_get_entity tool call.

    Args:
        args: Tool arguments

    Returns:
        MCP CallToolResult
    """
    if "entity_id" not in args:
        return error_result("Missing required field: entity_id")

    try:
        from omnivia_memory.graph.service import EntityNotFoundError

        service = create_graph_service()
        entity = service.get_entity(args["entity_id"])
        return success_result(entity_to_dict(entity))

    except EntityNotFoundError as e:
        return error_result(str(e))
    except Exception as e:
        return error_result(str(e))


def handle_graph_list_entities(args: dict[str, Any]) -> CallToolResult:
    """Handle graph_list_entities tool call.

    Args:
        args: Tool arguments

    Returns:
        MCP CallToolResult
    """
    try:
        service = create_graph_service()

        entities = service.list_entities(
            entity_type=args.get("entity_type"),
            limit=args.get("limit", 100),
            offset=args.get("offset", 0),
        )

        return success_result([entity_to_dict(e) for e in entities])

    except Exception as e:
        return error_result(str(e))


def handle_graph_create_relationship(args: dict[str, Any]) -> CallToolResult:
    """Handle graph_create_relationship tool call.

    Creates a relationship between two entities. Agent-created relationships
    start as "proposed" so humans can review before they become authoritative.

    Args:
        args: Tool arguments

    Returns:
        MCP CallToolResult
    """
    if "source_entity_id" not in args:
        return error_result("Missing required field: source_entity_id")
    if "target_entity_id" not in args:
        return error_result("Missing required field: target_entity_id")
    if "relationship_type" not in args:
        return error_result("Missing required field: relationship_type")

    try:
        from omnivia_memory.graph.service import EntityNotFoundError

        service = create_graph_service()

        relationship = service.create_relationship(
            source_entity_id=args["source_entity_id"],
            target_entity_id=args["target_entity_id"],
            relationship_type=args["relationship_type"],
            source_id=args.get("source_id"),
        )

        return success_result(relationship_to_dict(relationship))

    except EntityNotFoundError as e:
        return error_result(str(e))
    except Exception as e:
        return error_result(str(e))


def handle_graph_get_neighbors(args: dict[str, Any]) -> CallToolResult:
    """Handle graph_get_neighbors tool call.

    Returns all entities directly connected to a given entity, enabling
    graph traversal for queries like "what does this entity depend on?".

    Args:
        args: Tool arguments

    Returns:
        MCP CallToolResult
    """
    if "entity_id" not in args:
        return error_result("Missing required field: entity_id")

    try:
        service = create_graph_service()

        neighbors = service.get_neighbors(
            entity_id=args["entity_id"],
            relationship_type=args.get("relationship_type"),
        )

        return success_result(
            [
                {
                    "entity": entity_to_dict(entity),
                    "relationship": relationship_to_dict(rel),
                }
                for entity, rel in neighbors
            ]
        )

    except Exception as e:
        return error_result(str(e))


def handle_graph_search(args: dict[str, Any]) -> CallToolResult:
    """Handle graph_search tool call.

    Searches the knowledge graph by entity name with optional filtering
    and graph traversal to include neighbor context. Results include
    relevance scores based on name matching.

    Args:
        args: Tool arguments

    Returns:
        MCP CallToolResult
    """
    if "query" not in args:
        return error_result("Missing required field: query")

    try:
        service = create_graph_service()
        depth = args.get("depth", 0)
        limit = args.get("limit", 20)
        entity_types = args.get("entity_types")

        # List all entities and filter by name match with relevance scoring
        all_entities = service.list_entities(limit=1000)

        # Score and filter by query match on entity name
        query_lower = args["query"].lower()
        scored_entities: list[tuple[Entity, float]] = []

        for entity in all_entities:
            name_lower = entity.name.lower()
            if query_lower in name_lower:
                # Calculate relevance score: exact match = 1.0, contains = 0.5
                score = 1.0 if name_lower == query_lower else 0.5
                scored_entities.append((entity, score))

        # Filter by entity types if specified
        if entity_types:
            scored_entities = [
                (e, s) for e, s in scored_entities if e.entity_type.value in entity_types
            ]

        # Sort by relevance score descending, then take limit
        scored_entities.sort(key=lambda x: (-x[1], x[0].name))
        scored_entities = scored_entities[:limit]

        # Build response with optional neighbor context
        results = []
        for entity, score in scored_entities:
            result: dict[str, Any] = {
                "entity": entity_to_dict(entity),
                "relevance_score": score,
            }

            # Include neighbor context if depth > 0
            if depth > 0:
                neighbors = _get_entity_neighbors_at_depth(service, entity.id, depth)
                result["neighbors"] = neighbors

            results.append(result)

        return success_result(results)

    except Exception as e:
        return error_result(str(e))


def _get_entity_neighbors_at_depth(
    service: GraphService, entity_id: str, depth: int
) -> list[dict[str, Any]]:
    """Get neighbors of an entity up to a specified depth.

    Recursively traverses the graph to collect all connected entities
    at the given depth level.

    Args:
        service: The graph service to use for traversal
        entity_id: The starting entity
        depth: Maximum traversal depth (1 = direct neighbors only)

    Returns:
        List of neighbor information dictionaries
    """
    if depth <= 0:
        return []

    neighbors = service.get_neighbors(entity_id)
    result: list[dict[str, Any]] = []

    for neighbor_entity, relationship in neighbors:
        result.append(
            {
                "entity": entity_to_dict(neighbor_entity),
                "relationship": relationship_to_dict(relationship),
                "depth": 1,
            }
        )

        # Recursively get neighbors of neighbors if depth > 1
        if depth > 1:
            nested = _get_entity_neighbors_at_depth(service, neighbor_entity.id, depth - 1)
            result.extend(nested)

    return result


def handle_graph_get_context(args: dict[str, Any]) -> CallToolResult:
    """Handle graph_get_context tool call.

    Returns an entity along with all connected entities up to the
    specified traversal depth. This provides the "surrounding context"
    of an entity for understanding its role in the knowledge graph.

    Args:
        args: Tool arguments

    Returns:
        MCP CallToolResult
    """
    if "entity_id" not in args:
        return error_result("Missing required field: entity_id")

    try:
        from omnivia_memory.graph.service import EntityNotFoundError

        service = create_graph_service()
        entity = service.get_entity(args["entity_id"])
        depth = args.get("depth", 1)

        # Get neighbors up to the specified depth
        neighbors = _get_entity_neighbors_at_depth(service, entity.id, depth)

        return success_result(
            {
                "entity": entity_to_dict(entity),
                "neighbors": neighbors,
                "traversal_depth": depth,
            }
        )

    except EntityNotFoundError as e:
        return error_result(str(e))
    except Exception as e:
        return error_result(str(e))


# Tool handlers map
TOOL_HANDLERS: dict[str, Any] = {
    "memory_store": handle_memory_store,
    "memory_list": handle_memory_list,
    "memory_get": handle_memory_get,
    "memory_update": handle_memory_update,
    "memory_delete": handle_memory_delete,
    "memory_search": handle_memory_search,
    "memory_approve": handle_memory_approve,
    "memory_reject": handle_memory_reject,
    "graph_create_entity": handle_graph_create_entity,
    "graph_get_entity": handle_graph_get_entity,
    "graph_list_entities": handle_graph_list_entities,
    "graph_create_relationship": handle_graph_create_relationship,
    "graph_get_neighbors": handle_graph_get_neighbors,
    "graph_search": handle_graph_search,
    "graph_get_context": handle_graph_get_context,
}


async def run_server() -> None:
    """Run the MCP server over stdio."""
    server = Server(SERVER_NAME)

    @server.list_tools()  # type: ignore[no-untyped-call,untyped-decorator]
    async def list_tools() -> list[Tool]:
        """List available MCP tools."""
        return TOOLS

    @server.call_tool()  # type: ignore[untyped-decorator]
    async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:
        """Handle tool calls."""
        handler = TOOL_HANDLERS.get(name)
        if handler is None:
            return error_result(f"Unknown tool: {name}")

        return handler(arguments)  # type: ignore[no-any-return]

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)


def main() -> int:
    """Entry point for MCP server.

    Returns:
        Exit code
    """
    import asyncio

    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
