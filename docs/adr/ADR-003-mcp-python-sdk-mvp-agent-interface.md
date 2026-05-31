# ADR-003: MCP Python SDK as MVP Agent Interface

Status: Accepted
Date: 2026-05-30
Source: Open Source Repository Review

Reference: EngramMemory MCP implementation patterns

## Context

OmniVia needs an agent-facing interface so tools like Claude Code, Cursor, and other MCP-compatible clients can retrieve and write back project memory. After reviewing open source options, the official MCP Python SDK is the recommended implementation approach.

## Decision

**Adopt MCP Python SDK for MVP as the agent interface package.**

## Rationale

1. **Official SDK:** Maintained by Anthropic, ensures compatibility with MCP protocol
2. **Apache 2.0 license:** Permissive open source license
3. **Production usage:** Used by EngramMemory and other production systems
4. **Rich tool support:** Built-in support for MCP tools, resources, and prompts
5. **Python-native:** Matches OmniVia's Python backend architecture
6. **Active development:** Regular updates aligned with MCP protocol evolution

## Alternatives Considered

- **Custom MCP implementation:** REJECTED—Protocol complexity, maintenance burden
- **REST-only approach:** REJECTED—Loses MCP client compatibility (Claude Code, Cursor, etc.)
- **Graphiti MCP:** Not adopted—too tightly coupled to Graphiti architecture

## Reference Patterns from EngramMemory

The EngramMemory MCP server (15 tools) provides patterns for:
- Tool definitions with descriptions and schemas
- Request/response handling
- Error management
- Logging agent requests

## Placement

```python
# services/mcp-server/requirements.txt
mcp>=1.0.0
```

## Implementation Pattern

```python
from mcp.server import Server
from mcp.types import Tool

server = Server("omnivia-mcp")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="memory_search",
            description="Search memories by semantic query",
            inputSchema={...}
        ),
        # ... additional tools
    ]
```

## MCP Tools for MVP

1. `memory_search` — Semantic search over memories
2. `memory_recall` — Direct memory retrieval by ID
3. `memory_store` — Create new memory (marked as proposed by default)
4. `memory_forget` — Delete memory
5. `memory_propose` — Submit proposed memory for review
6. `source_search` — Search ingested sources
7. `context_get` — Get agent preflight context

## Consequences

**Positive:**
- Compatible with Claude Code, Cursor, and other MCP clients
- Official SDK with protocol compatibility guarantees
- Rich tool ecosystem built-in
- Proven in production (EngramMemory reference)

**Negative:**
- MCP protocol adds overhead for simple operations
- Need to maintain server lifecycle
- Version updates may require code changes

## Review Date

Re-evaluate after MCP server MVP completion.

## Definition of Done

This ADR is done when:

1. **Documentation Updated:** Implementation docs reflect the MCP SDK choice.
2. **Comment Pass Complete:** Changed code has plain-English comments for complex logic.
3. **Peer Review Complete:** A review report exists in `docs/quality/reviews/`. Critical and High findings are fixed or explicitly accepted.
4. **Tests Pass:** Unit tests pass, integration tests pass, or manual validation is documented.
5. **Dependency Register Updated:** `mcp>=1.0.0` is recorded if not already present.
6. **External Code Boundary Check:** No implementation code imports from `external/reference/`.
7. **Final Summary:** The completion summary includes what changed, tests run, review result, docs updated, remaining risks, and commands to run.

See also: `docs/quality/definition-of-done.md`, `docs/templates/task-dod-template.md`