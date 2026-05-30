"""
OmniVia MCP Server - Model Context Protocol interface for AI agents.

This server exposes OmniVia memory tools through the MCP protocol,
allowing AI agents like Claude Code, Cursor, and others to interact
with OmniVia's memory layer.
"""

import os
import json
import logging
from typing import Any

import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("omnivia-mcp")

# Configuration
API_BASE_URL = os.getenv("OMNIVIA_API_URL", "http://localhost:8080")
TIMEOUT_SECONDS = 30.0


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Define the MCP tools available to clients."""
    return [
        Tool(
            name="omnivia.memory.store",
            description="Store a new memory in OmniVia. Agent-created memories default to 'proposed' status and require human approval before being treated as trusted knowledge.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The content of the memory to store. Should be factual, concise, and clearly stated."
                    },
                    "source": {
                        "type": "string",
                        "description": "Optional source reference (file path, URL, document name, etc.)"
                    },
                    "memory_type": {
                        "type": "string",
                        "description": "Type of memory: 'general', 'decision', 'constraint', 'error', 'context'",
                        "default": "general"
                    }
                },
                "required": ["content"]
            }
        ),
        Tool(
            name="omnivia.memory.search",
            description="Search memories semantically using natural language. Returns memories that are semantically similar to the query, ordered by relevance.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query describing what you're looking for"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="omnivia.memory.recall",
            description="Retrieve a specific memory by its ID. Use this when you have a memory_id from a previous operation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "memory_id": {
                        "type": "string",
                        "description": "The unique ID of the memory to retrieve"
                    }
                },
                "required": ["memory_id"]
            }
        ),
        Tool(
            name="omnivia.context.preflight",
            description="Get preflight context for an agent task. Returns approved and observed memories relevant to the current task. Use this at the start of a task to understand existing context.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Description of the current task or goal"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of context memories to return",
                        "default": 10
                    }
                },
                "required": ["task"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls from MCP clients."""
    logger.info(f"Tool call: {name} with args: {arguments}")

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            if name == "omnivia.memory.store":
                result = await _handle_memory_store(client, arguments)
            elif name == "omnivia.memory.search":
                result = await _handle_memory_search(client, arguments)
            elif name == "omnivia.memory.recall":
                result = await _handle_memory_recall(client, arguments)
            elif name == "omnivia.context.preflight":
                result = await _handle_context_preflight(client, arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

        logger.info(f"Tool result: {result}")
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except httpx.HTTPError as e:
        logger.error(f"HTTP error: {e}")
        return [TextContent(
            type="text",
            text=json.dumps({"error": f"API error: {str(e)}"}, indent=2)
        )]
    except Exception as e:
        logger.error(f"Tool error: {e}")
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]


async def _handle_memory_store(client: httpx.AsyncClient, args: dict) -> dict:
    """Handle memory.store tool."""
    response = await client.post(
        f"{API_BASE_URL}/memories",
        json={
            "content": args["content"],
            "source": args.get("source"),
            "memory_type": args.get("memory_type", "general"),
            "created_by": "agent"
        }
    )
    response.raise_for_status()
    result = response.json()

    # Add helpful message about approval status
    status = result.get("approval_status", "proposed")
    if status == "proposed":
        result["_message"] = "Memory stored as 'proposed'. Human approval required before treatment as trusted knowledge."
    elif status == "observed":
        result["_message"] = "Memory stored as 'observed'. Available for agent recall."

    return result


async def _handle_memory_search(client: httpx.AsyncClient, args: dict) -> dict:
    """Handle memory.search tool."""
    response = await client.get(
        f"{API_BASE_URL}/memories/search",
        params={
            "query": args["query"],
            "limit": args.get("limit", 5)
        }
    )
    response.raise_for_status()
    return response.json()


async def _handle_memory_recall(client: httpx.AsyncClient, args: dict) -> dict:
    """Handle memory.recall tool."""
    memory_id = args["memory_id"]
    response = await client.get(f"{API_BASE_URL}/memories/{memory_id}")
    response.raise_for_status()
    return response.json()


async def _handle_context_preflight(client: httpx.AsyncClient, args: dict) -> dict:
    """Handle context.preflight tool."""
    # Search for relevant memories
    response = await client.get(
        f"{API_BASE_URL}/memories/search",
        params={
            "query": args["task"],
            "limit": args.get("limit", 10)
        }
    )
    response.raise_for_status()
    search_results = response.json()

    # Filter for approved and observed only (trusted knowledge)
    results = search_results.get("results", [])
    trusted_memories = [
        m for m in results
        if m.get("approval_status") in ["approved", "observed"]
    ]

    return {
        "task": args["task"],
        "context": trusted_memories,
        "count": len(trusted_memories),
        "note": "Only showing approved and observed memories. Proposed memories require human approval."
    }


async def main():
    """Main entry point for the MCP server."""
    logger.info(f"Starting OmniVia MCP Server, connecting to API at {API_BASE_URL}")

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())