# DEC-0003: Build OmniVia Dev Phase 1 Memory Core in Python

**Status:** Accepted
**Date:** 2026-05-31
**Owner:** OmniVia Team

---

## Context

The initial OmniVia Dev MVP plan implied TypeScript for the MCP server and memory core because DreamGraph is TypeScript-heavy and the first MVP planning documents referenced TypeScript package structures.

OmniVia's long-term intelligence layer will likely require document ingestion, embeddings, graph extraction, vector search, AI processing, memory consolidation, and GraphRAG-style workflows. Python is a stronger fit for that long-term core.

---

## Decision

Build the Phase 1 OmniVia Dev memory core, CLI, and MCP server in Python.

Reserve TypeScript, React, and Tauri for future UI, desktop app, graph visualisation, dashboards, connector setup screens, and review interfaces.

---

## Rationale

This avoids creating a throwaway TypeScript memory core that would later need to be rebuilt in Python.

Phase 1 should build the smallest useful version of the long-term memory/intelligence engine, not a temporary prototype.

---

## Consequences

The Phase 1 repo structure changes from TypeScript packages such as `packages/omnivia-core` and `packages/omnivia-mcp` to a Python service under `services/omnivia-memory`.

Phase 1 includes:

- Create, store, list, retrieve, update, and delete memories
- Keyword memory search
- Memory lifecycle states
- Local persistence
- Source and provenance fields
- Basic Python CLI
- Basic Python MCP server
- Basic test coverage

Phase 1 excludes:

- Project indexing
- Repo scanning
- Semantic search
- Vector store
- Graph enrichment
- Dashboard UI
- Desktop app
- Cloud sync
- External connectors
- Agent workflow automation

TypeScript remains part of the broader OmniVia stack but is deferred until UI and product surfaces are required.

---

## Review Criteria

Revisit this decision only if Python blocks MCP integration or if OmniVia's memory/intelligence core requirements change enough that another runtime clearly becomes the better long-term foundation.
