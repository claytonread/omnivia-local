# Repo Evaluation: graphiti

## 1. Executive Summary
- Graphiti provides temporal context graphs for AI agents with real-time incremental updates—directly relevant to OmniVia's knowledge graph needs
- Apache 2.0 license enables full commercial use—no restrictions
- Temporal data model with validity windows for facts—unique pattern not found elsewhere
- Episode-based provenance tracking—OmniVia should adopt this for audit trails
- Plugable driver architecture for multiple graph databases (Neo4j, FalkorDB, Kuzu, Neptune)
- MCP server included—aligns with OmniVia's MCP integration goals
- Hybrid retrieval (semantic + keyword + graph traversal) with cross-encoder reranking

## 2. What It Does
Graphiti is an open-source Python framework for building and querying temporal context graphs for AI agents. It enables real-time, incremental updates to knowledge graphs without batch recomputation. All derived facts trace back to "episodes" (raw ingested data).

## 3. Technology Stack
- **Language:** Python 3.10+
- **Graph Databases:** Neo4j 5.26, FalkorDB 1.1.2, Kuzu 0.11.2, Amazon Neptune
- **LLM Providers:** OpenAI (default), Anthropic, Google Gemini, Azure OpenAI, Groq, Ollama
- **Embeddings:** OpenAI, Azure OpenAI, Voyage AI, Gemini, sentence-transformers
- **Framework:** Pydantic (data validation), FastAPI (REST server)
- **Package Manager:** uv
- **Testing:** pytest, pytest-asyncio, pytest-xdist

## 4. Architecture
**Core Library (`graphiti_core/`):**

1. **Main Entry Point:** `graphiti_core/graphiti.py` — `Graphiti` class orchestrates all functionality

2. **Graph Data Models:**
   - `nodes.py` — Node types: EntityNode, EpisodicNode, CommunityNode, SagaNode
   - `edges.py` — Edge types: EntityEdge, EpisodicEdge, CommunityEdge, HasEpisodeEdge, NextEpisodeEdge

3. **Database Drivers (`graphiti_core/driver/`):**
   - `neo4j_driver.py` — Neo4j Cypher implementation
   - `falkordb_driver.py` — FalkorDB (Redis-based) implementation
   - `kuzu_driver.py` — Kuzu graph database
   - `neptune_driver.py` — Amazon Neptune support
   - `driver.py` — Abstract base class (`GraphDriver`)

4. **LLM Integration (`graphiti_core/llm_client/`):**
   - Clients for OpenAI, Anthropic, Gemini, Groq, Azure OpenAI, Ollama

5. **Embeddings (`graphiti_core/embedder/`):**
   - OpenAI, Azure OpenAI, Voyage, Gemini, sentence-transformers

6. **Search (`graphiti_core/search/`):**
   - Hybrid retrieval: semantic + keyword (BM25) + graph traversal
   - Cross-encoder reranking support

7. **Supporting Modules:**
   - `prompts/` — LLM prompts for entity extraction, deduplication, summarization
   - `utils/` — Maintenance, bulk processing, datetime handling
   - `telemetry/` — PostHog usage analytics (opt-out via `GRAPHITI_TELEMETRY_ENABLED=false`)

**REST Server (`server/`):** FastAPI service with endpoints in `routers/`

**MCP Server (`mcp_server/`):** Model Context Protocol server for AI assistants

## 5. Important Files and Folders
- `/graphiti_core/graphiti.py` (72KB) — Main Graphiti class, primary orchestrator
- `/graphiti_core/nodes.py` — Node data models
- `/graphiti_core/edges.py` — Edge data models
- `/graphiti_core/driver/driver.py` — Abstract driver interface
- `/graphiti_core/search/search.py` — Hybrid search implementation
- `/server/graph_service/main.py` — FastAPI REST server
- `/mcp_server/` — MCP server implementation
- `/examples/quickstart/` — Working examples
- `/Dockerfile` — Multi-stage Python 3.12-slim container
- `/docker-compose.yml` — Neo4j or FalkorDB + Graphiti

## 6. Licence and Commercial Risk
**Apache License 2.0** — Permissive open-source license from Zep Software, Inc.

- **Allowed:** Commercial use, modification, distribution with attribution
- **Risk Level:** None — safe for MVP, production, and commercial use
- No copyleft restrictions

## 7. What OmniVia Can Learn From It
- **Temporal data model** — Facts have validity windows (when true, when superseded)
- **Episode-based provenance** — All derived facts trace to raw ingested data
- **Pluggable driver architecture** — Abstract `GraphDriver` for multiple backends
- **Hybrid retrieval** — Combines semantic, keyword (BM25), and graph traversal
- **Cross-encoder reranking** — BGE, OpenAI, Gemini rerankers
- **Custom entity types** — Prescribed ontology (Pydantic models) or learned ontology
- **Async/await throughout** — Full async implementation
- **Telemetry opt-out** — `GRAPHITI_TELEMETRY_ENABLED=false`

## 8. What OmniVia Should Not Reuse
- Kuzu driver (archived project)—use FalkorDB or Neo4j instead
- Telemetry collection—even if opt-out exists, consider clean implementation
- Neo4j-only features that don't work on other backends
- Hardcoded entity extraction prompts—make configurable

## 9. Recommended Integration
reference only

## 10. Recommended Placement in OmniVia
external/reference/

## 11. Required Spec Kit Updates
- `specs/temporal-graph.md` — Document validity window pattern
- `specs/provenance-tracking.md` — Add episode-based provenance section
- `specs/driver-abstraction.md` — Design plugable driver interface
- `specs/hybrid-retrieval.md` — Document hybrid search architecture
- `specs/search-strategies.md` — Add cross-encoder reranking pattern

## 12. Implementation Tasks to Add
- Implement temporal data model with fact validity windows
- Design episode-based provenance tracking system
- Create `GraphDriver` abstraction for multiple backends
- Implement hybrid retrieval (semantic + keyword + graph)
- Add cross-encoder reranking support
- Design custom entity type system (prescribed/learned ontology)

## 13. Final Recommendation
reference only

**Rationale:** Graphiti's temporal context graph model and plugable driver architecture are directly relevant to OmniVia's knowledge graph needs. However, it lacks certain features OmniVia requires (e.g., MCP-native memory tools, multi-tenant isolation, credential scrubbing). OmniVia should implement its own graph system inspired by these patterns rather than building on this library.