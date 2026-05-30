# OmniVia Spec Update Summary

This document summarizes the spec updates required based on the open source repository reviews.

## Overview

The seven reviewed repositories provide architectural patterns and design references that should inform OmniVia's specification documents. No code is being adopted; only conceptual patterns are being incorporated.

## New Specs to Create

### 1. specs/memory-architecture.md
**Based on:** EngramMemory (three-tiered ACT-R caching)
**Purpose:** Document tiered memory caching with hot/warm/cold tiers
**Content:**
- ACT-R cognitive model for memory activation and decay
- Multi-head LSH for fast O(1) candidate retrieval
- Matryoshka representation learning (hierarchical vector dimensions)
- Hot-tier cache with configurable max entries and decay rates
- Credential scrubbing patterns

### 2. specs/plugin-architecture.md
**Based on:** MarkItDown (entry point pattern)
**Purpose:** Define document converter plugin system
**Content:**
- Entry point registration for third-party converters
- Priority-based converter ordering
- Stream-based processing with position preservation
- Graceful fallback chains for format conversion

### 3. specs/chunking-strategy.md
**Based on:** Unstructured, GraphRAG
**Purpose:** Define document chunking approaches
**Content:**
- Chunking strategies: basic, by_title, token-based
- Configurable overlap, header repetition, table isolation
- Consolidation strategies: FIRST, DROP, LIST_CONCATENATE
- Metadata propagation during chunking

### 4. specs/graph-indexing.md
**Based on:** GraphRAG, Graphiti
**Purpose:** Document knowledge graph construction workflow
**Content:**
- Workflow-based pipeline pattern
- Document → text units → entities → relationships → communities
- Community detection (Leiden algorithm)
- Community report generation

### 5. specs/temporal-graph.md
**Based on:** Graphiti
**Purpose:** Document temporal data model for knowledge graphs
**Content:**
- Fact validity windows (when true, when superseded)
- Episode-based provenance tracking
- Temporal query patterns
- Spreading activation algorithms

### 6. specs/pipeline-architecture.md
**Based on:** Cognee (ECL pipeline)
**Purpose:** Define extraction, cognify, load workflow
**Content:**
- ECL (Extract, Cognify, Load) pipeline pattern
- Pipeline orchestration with task execution layer
- Sequential and parallel task execution
- Pipeline state management

### 7. specs/database-abstraction.md
**Based on:** Cognee, Graphiti
**Purpose:** Define database adapter interfaces
**Content:**
- GraphDBInterface abstract class
- VectorDBInterface abstract class
- Driver registration and factory pattern
- Adapters for Qdrant, FalkorDB, Neo4j, LanceDB

### 8. specs/query-strategies.md
**Based on:** GraphRAG, Graphiti, Cognee
**Purpose:** Document search strategy options
**Content:**
- Local search (entity-focused)
- Global search (community-based map-reduce)
- Drift search (multi-hop)
- Basic vector similarity
- Hybrid retrieval (semantic + keyword + graph)
- Cross-encoder reranking

## Existing Specs to Update

### 1. specs/mcp-integration.md
**Changes:**
- Add MCP tool patterns from EngramMemory (15 tool patterns)
- Document credential scrubbing during memory store
- Add conflict detection patterns for memory consolidation

### 2. specs/document-ingestion.md
**Changes:**
- Add converter registry pattern from MarkItDown
- Document Element model hierarchy concept
- Add file type detection with Magika pattern

### 3. specs/search-patterns.md
**Changes:**
- Add ACT-R cognitive model and LSH concepts
- Document BM25 sparse vector integration
- Add Reciprocal Rank Fusion for re-ranking

### 4. specs/graph-database.md
**Changes:**
- Remove Kuzu as recommended option (archived project)
- Add FalkorDB as primary recommendation
- Add Neo4j as enterprise alternative
- Document extension framework pattern

### 5. specs/driver-abstraction.md
**Changes:**
- Design pluggable GraphDriver interface
- Define adapter implementations for supported databases
- Document connection pooling and failover patterns

### 6. specs/llm-integration.md
**Changes:**
- Add LLM Gateway pattern from Cognee
- Document litellm integration for multi-provider support
- Add Instructor for structured output patterns

## Specs for Consideration (Future)

These specs may be needed based on patterns discovered but not immediately required:

- `specs/multi-tenancy.md` — User/Dataset/Data hierarchy with permission filtering
- `specs/telemetry-design.md` — Opt-out telemetry patterns
- `specs/conflict-resolution.md` — Memory conflict detection and resolution
- `specs/noise-filtering.md` — Short message and code block filtering

## Priority Order for Spec Updates

1. **High Priority (MVP requirements):**
   - specs/database-abstraction.md (for Qdrant integration)
   - specs/mcp-integration.md (for MCP server)
   - specs/document-ingestion.md (for converter registry)

2. **Medium Priority (Core features):**
   - specs/plugin-architecture.md
   - specs/chunking-strategy.md
   - specs/query-strategies.md

3. **Lower Priority (Advanced features):**
   - specs/memory-architecture.md
   - specs/temporal-graph.md
   - specs/pipeline-architecture.md

## Implementation Note

These spec updates should inform implementation but should not directly result in code. The specs guide architectural decisions; implementation follows after spec approval.