# OmniVia Test Strategy

## Test Levels

### Smoke Tests

Prove the local runtime starts and the main workflow works.

Examples:

- API health check works.
- Memory can be stored.
- Memory can be searched.
- MCP tool can be called.
- Qdrant is reachable.
- SQLite persists data after restart.

### Unit Tests

Validate isolated business logic.

Examples:

- memory status transitions
- source hashing
- chunk hashing
- search filters
- approval status filtering
- restricted memory filtering

### Integration Tests

Validate service interactions.

Examples:

- API to SQLite
- API to Qdrant
- FastEmbed to Qdrant
- MCP tool to memory service
- ingestion to chunk store to vector search

### Regression Tests

Protect known behaviours.

Examples:

- agent-created memory stays proposed
- rejected memory is excluded
- superseded memory is historical
- re-ingesting unchanged file does not duplicate chunks

## Minimum Test Requirement by Feature

### Local Runtime

- Health check test
- persistence smoke test

### Memory Engine

- create memory
- search memory
- recall memory
- approve memory
- reject memory
- supersede memory

### Agent Interface

- MCP connection test
- MCP memory store
- MCP memory search
- MCP memory recall
- proposed default status

### Ingestion

- ingest Markdown
- ingest text
- chunk creation
- re-ingestion without duplication

### Vector Search

- chunk embedding
- memory embedding
- semantic search
- metadata filtering

## If Tests Cannot Be Run

Claude must document:

1. Which tests could not be run.
2. Why they could not be run.
3. What manual validation was performed instead.
4. What should be fixed to make tests runnable.
