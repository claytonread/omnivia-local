# OmniVia Open Source Adoption Plan

## 1. Executive Recommendation

OmniVia should adopt **Qdrant**, **FastEmbed**, and **MCP Python SDK** for MVP. All seven evaluated repositories should be kept as reference material for architectural patterns. Kuzu should be rejected due to project archival status. UI components (Tiptap, React Flow) are deferred to future phases.

## 2. Adopt for MVP

### Qdrant
- **Purpose:** Vector database for semantic search
- **Integration:** Docker service
- **Placement:** `infra/docker/docker-compose.local.yml`
- **Rationale:** Production-grade, actively maintained, Apache 2.0 license

### FastEmbed
- **Purpose:** Local ONNX-based embedding generation
- **Integration:** Package dependency
- **Placement:** `services/embedding-service/requirements.txt`
- **Rationale:** Zero API costs, local processing, nomic-embed-text-v1.5 model

### MCP Python SDK
- **Purpose:** Model Context Protocol server implementation
- **Integration:** Package dependency
- **Placement:** `services/mcp-server/requirements.txt`
- **Rationale:** Official MCP SDK, required for OmniVia MCP integration

## 3. Install as Package Dependencies

```
# services/embedding-service/requirements.txt
fastembed>=0.7.0

# services/mcp-server/requirements.txt
mcp>=1.0.0
```

**Note:** UI components (Tiptap, React Flow) are deferred to future phases. See Section 6 for spike later items.

## 4. Run as Docker Services

```yaml
# infra/docker/docker-compose.local.yml
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_storage:/qdrant/storage
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 5. Keep as Reference Only

### EngramMemory
- **Key Patterns:** Three-tiered ACT-R caching, Multi-head LSH, Hive-based sharing
- **Spec Updates:** `specs/memory-architecture.md`, `specs/mcp-integration.md`

### MarkItDown
- **Key Patterns:** Plugin architecture via entry points, Priority-based converter ordering
- **Spec Updates:** `specs/document-ingestion.md`, `docs/architecture/plugin-architecture.md`

### Unstructured
- **Key Patterns:** Element model hierarchy, Dynamic metadata, Lazy loading
- **Spec Updates:** `specs/document-ingestion.md`, `specs/chunking-strategy.md`

### GraphRAG
- **Key Patterns:** Factory pattern, Workflow pipelines, Four search strategies
- **Spec Updates:** `specs/graph-indexing.md`, `specs/query-strategies.md`

### Graphiti
- **Key Patterns:** Temporal validity windows, Episode-based provenance, Hybrid retrieval
- **Spec Updates:** `specs/temporal-graph.md`, `specs/hybrid-retrieval.md`

### Cognee
- **Key Patterns:** ECL pipeline, Interface-based database adapters, Multi-tenant access control
- **Spec Updates:** `specs/pipeline-architecture.md`, `specs/multi-tenancy.md`

## 6. Spike Later

1. **FalkorDB vs Neo4j comparison** — Select graph database for production
2. **Custom LLM Gateway** — litellm integration patterns from Cognee
3. **Graphiti temporal patterns** — Evaluate for audit trail requirements
4. **GraphRAG community detection** — Leiden algorithm for graph clustering
5. **Tiptap integration** — Rich text editor for web-based memory entry
6. **React Flow integration** — Knowledge graph visualization

## 7. Licence Review Required

No additional license reviews required. All adopted packages use permissive licenses:
- Qdrant: Apache 2.0
- FastEmbed: Apache 2.0
- MCP Python SDK: Apache 2.0

**Note:** EngramMemory uses BSL 1.1 which restricts SaaS usage. This is acceptable for MVP phase but requires licensing discussion before commercial deployment.

## 8. Reject for MVP

### Kuzu
- **Reason:** Project is archived (v0.11.x is final release)
- **Alternative:** SQLite graph placeholders for MVP; spike FalkorDB/Neo4j for production
- **Replacement:** Spike required to evaluate FalkorDB and Neo4j alternatives

## 9. Spec Kit Updates Required

### New Specs to Create
- `specs/memory-architecture.md` — Tiered caching patterns from EngramMemory
- `specs/plugin-architecture.md` — Entry point pattern from MarkItDown
- `specs/chunking-strategy.md` — Chunking strategies from Unstructured
- `specs/graph-indexing.md` — Workflow pipelines from GraphRAG
- `specs/query-strategies.md` — Search strategy options from GraphRAG/Graphiti
- `specs/temporal-graph.md` — Validity window patterns from Graphiti
- `specs/pipeline-architecture.md` — ECL pipeline from Cognee
- `specs/database-abstraction.md` — Interface-based adapters from Cognee

### Existing Specs to Update
- `specs/mcp-integration.md` — Add MCP tool patterns from EngramMemory
- `specs/document-ingestion.md` — Add converter registry pattern
- `specs/search-patterns.md` — Add ACT-R model and LSH concepts
- `specs/graph-database.md` — Update recommendations (exclude Kuzu)
- `specs/driver-abstraction.md` — Design pluggable driver interface

## 10. Architecture Decisions Required

1. **Graph Database Selection:** FalkorDB vs Neo4j for production
2. **Memory Caching Strategy:** Implement tiered caching similar to EngramMemory
3. **Search Strategy Mix:** Which of the 12+ search strategies to implement first
4. **Temporal vs. Immutable:** Whether to use Graphiti-style validity windows
5. **Pipeline Orchestration:** Build custom ECL pipeline or use simpler approach

## 11. First Implementation Tasks

1. **Setup Qdrant Docker service** — Add to docker-compose.local.yml
2. **Integrate FastEmbed** — Add embedding service with local ONNX model
3. **Integrate MCP Python SDK** — Build MCP server with initial tools
4. **Design document converter registry** — Implement MarkItDown-inspired plugin system
5. **Implement SQLite graph placeholders** — Entity/relationship tables for MVP

## 12. Recommended Build Sequence

```
Phase 1: Foundation
├── Set up Docker Compose with Qdrant
├── Build MCP server with MCP Python SDK
├── Implement embedding service with FastEmbed
└── Design document converter plugin architecture

Phase 2: Core Memory
├── Implement vector storage with Qdrant
├── Build memory store/retrieve MCP tools
├── Add search endpoint with basic retrieval
└── Implement SQLite graph placeholders

Phase 3: Ingestion Pipeline
├── Build document converter registry
├── Implement chunking strategies
├── Add source tracking and content hashing
└── Integrate with Qdrant for chunk embeddings

Phase 4: Governance Layer
├── Implement approval workflow
├── Add audit logging
├── Build review queue
└── Add permission-based access

Phase 5: Future Work (Post-MVP)
├── Spike FalkorDB vs Neo4j for graph DB
├── Implement Graphiti-inspired temporal model
├── Add React Flow for visualization
└── Integrate Tiptap for web-based entry
```