# OmniVia Dev Task List

**Status:** In Progress
**Date:** 2026-05-31
**Owner:** OmniVia Team

---

## Overview

This document tracks implementation tasks for OmniVia Dev MVP. Tasks are organized by phase and priority.

The MVP spec is the controlling source of truth for Phase 1 scope. Phase 1 is Memory Core only. Project Source Ingestion begins in Phase 2. Graph and semantic work begins in Phase 3. OmniVia Local productisation begins in Phase 5.

---

## Phase 1: Memory Core (MVP)

### 1.1 Python Service Structure

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Create `services/omnivia-memory` | P0 | Pending | Python memory/intelligence service |
| Set up `pyproject.toml` | P0 | Pending | Package metadata, test tooling |
| Create `src/omnivia_memory/` package | P0 | Pending | memory, search, provenance, lifecycle, mcp, cli |
| Create `tests/` | P0 | Pending | Basic unit/integration coverage |

### 1.2 Memory Domain

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Define Memory model with lifecycle state | P0 | Pending | proposed, observed, approved, rejected |
| Define Source/provenance model | P0 | Pending | file, url, adr, human |
| Define memory create/update inputs | P0 | Pending | Validate required fields |
| Define memory lifecycle transition rules | P0 | Pending | Agent-created memories start unapproved |
| Define Node/Edge types for graph | P1 | Deferred | Phase 3 |
| Define ADR interface | P1 | Deferred | Use existing ADR format |
| Create memory repository/service interface | P0 | Pending | Local persistence boundary |
| Create utility functions | P1 | Pending | serialization, validation |

### 1.3 Memory Operations

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Implement create/store memory | P0 | Pending | Store with required source reference |
| Implement list memories | P0 | Pending | Support local inspection |
| Implement retrieve memory | P0 | Pending | Retrieve by ID |
| Implement update memory | P0 | Pending | Controlled field updates |
| Implement delete memory | P0 | Pending | Local deletion |
| Implement keyword search | P0 | Pending | No vector store in Phase 1 |
| Implement lifecycle transitions | P0 | Pending | approve/reject/observe where applicable |
| Add error handling | P0 | Pending | Clear error messages |
| Add logging | P1 | Pending | Debug support |

### 1.4 Local Persistence

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Set up SQLite for memories | P0 | Pending | File-based, portable |
| Create memory table schema | P0 | Pending | id, content, source, status, etc. |
| Implement memory repository with SQLite | P0 | Pending | CRUD operations |
| Add transaction support | P1 | Pending | Concurrent safety |

### 1.5 CLI and MCP

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Implement basic Python CLI | P0 | Pending | create, list, get, update, delete, search |
| Set up Python MCP server with stdio transport | P0 | Pending | Core agent interface |
| Implement memory_store tool | P0 | Pending | Store with source reference |
| Implement memory_search tool | P0 | Pending | Keyword search |
| Implement memory_get tool | P0 | Pending | Retrieve by ID |
| Implement memory_update tool | P0 | Pending | Update memory |
| Implement memory_delete tool | P0 | Pending | Delete memory |
| Implement memory_approve tool | P0 | Pending | proposed/observed → approved |
| Implement memory_reject tool | P0 | Pending | Reject memory |

### 1.6 Testing

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Set up Python test infrastructure | P0 | Pending | pytest or repo-standard equivalent |
| Write unit tests for memory models | P0 | Pending | Validation and defaults |
| Write unit tests for lifecycle rules | P0 | Pending | Agent/human approval behavior |
| Write integration tests for store | P0 | Pending | SQLite operations |
| Test CLI behavior | P1 | Pending | Smoke coverage |
| Test stdio MCP transport | P0 | Pending | Verify MCP protocol |

---

## Phase 2: Project Source Ingestion

### 2.1 Scanner

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Implement repo/document scanner | P1 | Done | Implemented via IngestionPipeline |
| Index existing ADRs | P1 | Done | Via `omnivia-memory ingest --source-type adr` |
| Index task and ops documents | P1 | Done | Via `omnivia-memory ingest --memory-type task` |
| Index service definitions | P2 | Deferred | After service structure exists |
| Index package relationships | P2 | Deferred | Later product structure |

### 2.2 Source-Backed Recall

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Store source records | P1 | Done | sources and chunks tables |
| Link sources to memories | P1 | Done | SourceType.FILE and SourceType.ADR |
| Implement project ontology | P2 | Done | memory-type categories (decision, task, pattern, general) |
| Implement project context ingestion command | P1 | Done | `omnivia-memory ingest` |
| Link decisions and tasks to sources | P1 | Done | get_by_source_reference() method |

---

## Phase 3: Graph and Semantic Intelligence

### 3.1 Node/Edge Model

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Implement Node storage | P1 | Done | Entity model and EntityRepository |
| Implement Edge storage | P1 | Done | Relationship model and RelationshipRepository |
| Add bidirectional edge support | P2 | Deferred | |
| Implement graph traversal | P1 | Done | GraphService.get_neighbors, get_context |
| Add semantic search | P2 | Deferred | After Phase 2 source ingestion |
| Add vector store | P2 | Deferred | Not part of MVP |
| Add graph enrichment | P2 | Deferred | |

### 3.2 Relationship Tools

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Implement graph_get_node | P1 | Done | MCP tool: get_entity |
| Implement graph_search | P1 | Done | MCP tool: search_entities |
| Implement graph_get_neighbors | P1 | Done | MCP tool: get_entity_context |
| Implement graph_get_path | P2 | Deferred | |

### 3.3 Decision Tracking

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Implement ADR storage | P1 | Done | Via ingest with --source-type adr |
| Implement decision_search | P1 | Done | Via memory search |
| Link decisions to nodes | P2 | Deferred | |

### 3.4 Context Tools

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Implement context_get_project | P2 | Deferred | |
| Implement context_get_service | P2 | Deferred | |
| Implement context_get_dependencies | P2 | Deferred | |

---

## Phase 4: Dev Agent Workflow Support

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Implement pattern detection | P2 | Deferred | |
| Implement knowledge consolidation | P2 | Deferred | |
| Implement tension surfacing | P3 | Deferred | Future |
| Implement recommendations | P3 | Deferred | Future |
| Implement agent workflow support | P3 | Deferred | Future |

---

## Phase 5: OmniVia Local Productisation

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Build local desktop/workspace UI | P3 | Deferred | Future |
| Build TypeScript / React / Tauri product surface | P3 | Deferred | Future |
| Build graph visualisation | P3 | Deferred | Future |
| Build dashboard | P3 | Deferred | Future |
| Build connector setup screens | P3 | Deferred | Future |
| Build review workflows | P3 | Deferred | Future |
| Define business ontology | P3 | Deferred | Future |
| Define local-to-cloud upgrade path | P3 | Deferred | Future |

---

## Dependencies

### External Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | TBD | Memory/intelligence core runtime |
| MCP Python SDK | TBD | MCP server implementation |
| SQLite | stdlib or package-backed | Local memory storage |
| pytest | TBD | Test coverage |

### Internal Dependencies

| Dependency | Source | Purpose |
|------------|--------|---------|
| omnivia-memory | services/omnivia-memory | Phase 1 memory core |

---

## Task Dependencies

```
Phase 1:
├── 1.1 Python Service Structure (prerequisite for all)
│   ├── 1.2 Memory Domain (requires 1.1)
│   │   ├── 1.3 Memory Operations (requires 1.2)
│   │   ├── 1.4 Local Persistence (parallel with 1.3)
│   │   └── 1.5 CLI and MCP (requires 1.3 and 1.4)
│   │       └── 1.6 Testing (runs throughout)

Phase 2: Requires Phase 1 complete
Phase 3: Requires Phase 2 complete
Phase 4: Requires Phase 3 complete
Phase 5: Requires Phase 4 complete
```

---

## Progress Tracking

### Completed

- [x] Decision: Build OmniVia Dev First (ADR-0001)
- [x] Decision: Use DreamGraph as Reference, Not Dependency (ADR-0002)
- [x] Decision: Build Phase 1 memory core in Python (DEC-0003)
- [x] Research: DreamGraph analysis complete
- [x] Strategy: OmniVia Dev First strategy documented

### In Progress

- [x] This task list created

### Next Up

1. Create `services/omnivia-memory` service
2. Define Python memory and source/provenance models
3. Implement local persistence and keyword search
4. Set up Python CLI and MCP server scaffold

---

## Related Documents

- [OmniVia Dev MVP Spec](../specs/omnivia-dev-mvp-spec.md)
- [OmniVia Dev First Strategy](../strategy/omnivia-dev-first-strategy.md)
- [OmniVia Core Architecture](../architecture/omnivia-core-architecture.md)
- [Definition of Done](../quality/definition-of-done.md)
