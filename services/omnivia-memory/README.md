# OmniVia Memory Core

OmniVia Dev Phase 1: local memory and persistence core for AI coding agents.

## Overview

This package provides the memory core for OmniVia Dev, enabling AI coding agents to store and retrieve source-backed project memories through both a CLI and MCP server interface.

## Features

- Memory CRUD operations (create, list, retrieve, update, delete)
- Keyword search for Phase 1
- Lifecycle states (proposed, observed, approved, rejected)
- Source/provenance tracking
- SQLite-backed local persistence
- Python CLI for local operation
- MCP server over stdio for AI agent integration

## Installation

```bash
pip install -e ".[dev]"
```

## CLI Usage

The CLI provides local memory operations for debugging and human use.

### Create a memory

```bash
omnivia-memory create \
  --content "This service uses Python for the memory core" \
  --source-type file \
  --source-ref services/omnivia-memory/pyproject.toml \
  --created-by agent
```

### List memories

```bash
# List all memories
omnivia-memory list

# Filter by lifecycle state
omnivia-memory list --state proposed

# Limit results
omnivia-memory list --limit 10 --offset 0
```

### Get a memory

```bash
omnivia-memory get <memory-id>
```

### Update a memory

```bash
omnivia-memory update <memory-id> --content "Updated content"
```

### Delete a memory

```bash
omnivia-memory delete <memory-id>
```

### Search memories

```bash
omnivia-memory search "Python"
```

### Approve or reject memories

```bash
omnivia-memory approve <memory-id>
omnivia-memory reject <memory-id>
```

### Show statistics

```bash
omnivia-memory stats
```

## MCP Server

The MCP server provides stdio transport for AI coding agent integration.

### Start the MCP server

```bash
omnivia-memory-mcp
```

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `memory_store` | Store a new memory with source reference |
| `memory_list` | List memories with optional filtering |
| `memory_get` | Retrieve a memory by ID |
| `memory_update` | Update a memory's content or type |
| `memory_delete` | Delete a memory by ID |
| `memory_search` | Search memories by keyword |
| `memory_approve` | Approve a memory |
| `memory_reject` | Reject a memory |

### MCP Tool Schemas

#### memory_store

```json
{
  "content": "string (required)",
  "source_type": "file|url|adr|human (required)",
  "source_reference": "string (required)",
  "source_description": "string (optional)",
  "memory_type": "string (default: general)",
  "created_by": "human|agent (default: agent)"
}
```

#### memory_list

```json
{
  "limit": "integer (default: 100)",
  "offset": "integer (default: 0)",
  "lifecycle_state": "proposed|observed|approved|rejected"
}
```

#### memory_get

```json
{
  "memory_id": "string (required)"
}
```

#### memory_update

```json
{
  "memory_id": "string (required)",
  "content": "string (optional)",
  "memory_type": "string (optional)"
}
```

#### memory_delete

```json
{
  "memory_id": "string (required)"
}
```

#### memory_search

```json
{
  "query": "string (required)",
  "limit": "integer (default: 20)"
}
```

#### memory_approve

```json
{
  "memory_id": "string (required)"
}
```

#### memory_reject

```json
{
  "memory_id": "string (required)"
}
```

## Lifecycle States

Memories have lifecycle states that control how AI-created knowledge becomes approved:

| State | Meaning |
|-------|---------|
| `proposed` | AI-created, unverified (default for agent-created) |
| `observed` | Partially validated |
| `approved` | Validated by human or source (default for human-created) |
| `rejected` | Explicitly disproved |

## Testing

```bash
python -m pytest
```

With coverage:

```bash
python -m pytest --cov=omnivia_memory
```

## Architecture

```
services/omnivia-memory/
├── src/omnivia_memory/
│   ├── memory/        # Memory models and service layer
│   ├── search/        # Keyword search
│   ├── provenance/    # Source/provenance tracking
│   ├── lifecycle/     # Lifecycle state management
│   ├── persistence/    # SQLite persistence
│   ├── cli/           # Command-line interface
│   └── mcp/           # MCP server
└── tests/             # Test suite
```

## Data Storage

Memories are stored in SQLite at `~/.omnivia/memories.db`.

## Phase 1 Scope

Implemented:
- Memory CRUD operations
- Keyword search
- Lifecycle states
- Source/provenance tracking
- SQLite persistence
- CLI and MCP interfaces

Not implemented (Phase 2+):
- Project indexing
- Semantic/vector search
- Graph layer
- Decision tracking
- Context generation