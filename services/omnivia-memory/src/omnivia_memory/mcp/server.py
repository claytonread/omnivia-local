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


# Server instance name
SERVER_NAME = "omnivia-memory"


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
