# Post-Review Spec Update Summary

Date: 2026-05-30
Source: Open Source Repository Review
Reviewer: Claude (following PROMPTS/CLAUDE_RUN_REPO_REVIEWS.md)

## Overview

After completing the open source repository review per the SPEC.md instructions, the following files were created or updated to reflect the decisions made during the review.

## Decisions Applied

| Decision | Applied To |
|----------|------------|
| Adopt Qdrant for MVP as Docker service | ADRs, Specs |
| Adopt FastEmbed for MVP as package | ADRs, Specs |
| Adopt MCP Python SDK for MVP as package | ADRs, Specs |
| External graph/memory repos reference-only | ADRs, dependency-register |
| Reject Kuzu for MVP (archived) | ADRs, Specs |
| Tiptap/React Flow deferred to future | dependency-register, adoption-plan |

## Files Created

### Architecture Decision Records (5 new)

| File | Purpose |
|------|---------|
| `docs/adr/ADR-001-qdrant-mvp-vector-database.md` | Documents Qdrant adoption as MVP vector database |
| `docs/adr/ADR-002-fastembed-mvp-embedding-layer.md` | Documents FastEmbed adoption as MVP embedding layer |
| `docs/adr/ADR-003-mcp-python-sdk-mvp-agent-interface.md` | Documents MCP Python SDK adoption as MVP agent interface |
| `docs/adr/ADR-004-kuzu-rejected-mvp.md` | Documents Kuzu rejection due to archived status |
| `docs/adr/ADR-005-external-repos-reference-only.md` | Documents reference-only status for graph/memory repos |

### Evaluation Files (7 new)

| File | Repository Reviewed |
|------|---------------------|
| `docs/open-source/engram-memory-evaluation.md` | EngramMemory |
| `docs/open-source/markitdown-evaluation.md` | MarkItDown |
| `docs/open-source/unstructured-evaluation.md` | Unstructured |
| `docs/open-source/graphrag-evaluation.md` | GraphRAG |
| `docs/open-source/graphiti-evaluation.md` | Graphiti |
| `docs/open-source/cognee-evaluation.md` | Cognee |
| `docs/open-source/kuzu-evaluation.md` | Kuzu |

### Summary Documents (4 new)

| File | Purpose |
|------|---------|
| `docs/open-source/dependency-register.md` | Consolidated dependency decisions |
| `docs/open-source/open-source-adoption-plan.md` | Implementation roadmap |
| `docs/open-source/licence-risk-register.md` | License risk tracking |
| `docs/open-source/spec-update-summary.md` | Required spec updates |

## Files Updated

### Spec Plans Updated (6 files)

| File | Changes |
|------|---------|
| `specs/001-local-runtime/plan.md` | Added ADR-001 alignment, Qdrant Docker details |
| `specs/002-memory-engine/plan.md` | Added ADR-001/002 alignment, EngramMemory reference note |
| `specs/003-agent-interface/plan.md` | Added ADR-003 alignment, MCP tools list, EngramMemory patterns |
| `specs/004-ingestion-normalisation/plan.md` | Added ADR-005 alignment, MarkItDown/Unstructured reference patterns |
| `specs/005-vector-search/plan.md` | Added ADR-001/002 alignment, reference patterns from external repos |
| `specs/007-knowledge-graph/plan.md` | **Major update:** Changed from Kuzu to SQLite placeholders, added ADR-004/005 alignment, future spike items |

### Open Source Documents Updated (2 files)

| File | Changes |
|------|---------|
| `docs/open-source/dependency-register.md` | Updated Tiptap/React Flow to "spike later", removed from MVP |
| `docs/open-source/open-source-adoption-plan.md` | Removed Tiptap/React Flow from adopt for MVP section, updated build sequence |

## Spec Updates by Area

### Local Runtime (Spec 001)
- **Added:** Qdrant Docker service configuration
- **Added:** ADR-001 alignment reference

### Memory Engine (Spec 002)
- **Added:** ADR-001/ADR-002 alignment (Qdrant + FastEmbed)
- **Added:** Reference to EngramMemory tiered caching patterns (do not import)
- **Added:** Note to implement own tiered caching

### Agent Interface (Spec 003)
- **Added:** ADR-003 alignment (MCP Python SDK)
- **Added:** MCP tools list for MVP
- **Added:** Reference to EngramMemory MCP patterns (do not import)

### Ingestion and Normalisation (Spec 004)
- **Added:** ADR-005 alignment (MarkItDown/Unstructured reference only)
- **Added:** Plugin architecture patterns from MarkItDown
- **Added:** Element model hierarchy patterns from Unstructured
- **Added:** Implementation approach for own document processing pipeline

### Vector Search (Spec 005)
- **Added:** ADR-001/ADR-002 alignment (Qdrant + FastEmbed)
- **Added:** Technology stack with requirements
- **Added:** Default embedding model (nomic-ai/nomic-embed-text-v1.5)
- **Added:** Reference patterns from GraphRAG/Graphiti/Cognee

### Governance and Trust (Spec 006)
- **No changes:** Review findings don't affect governance spec directly

### Knowledge Graph (Spec 007)
- **Major change:** Replaced Kuzu with SQLite graph placeholders
- **Added:** ADR-004 alignment (Kuzu rejected)
- **Added:** ADR-005 alignment (Graphiti/GraphRAG/Cognee reference only)
- **Added:** SQLite entity/relationship table schemas
- **Added:** Reference patterns from Graphiti temporal model
- **Added:** Future graph database spike items (FalkorDB, Neo4j)

## Key Architecture Changes

### Before Review
```
graphrag plan: "Use Kuzu for local embedded graph storage"
vector-search: "Use FastEmbed for local embeddings and Qdrant"
agent-interface: "Use the MCP Python SDK" (already correct)
```

### After Review
```
graphrag plan: "SQLite graph placeholders for MVP; spike FalkorDB/Neo4j later"
vector-search: "FastEmbed + Qdrant with ADR alignment" ✓
agent-interface: "MCP Python SDK with ADR alignment" ✓
```

## New Directories Created

| Directory | Purpose |
|----------|---------|
| `docs/adr/` | Architecture Decision Records |
| `docs/architecture/` | Architecture documentation (empty, for future use) |

## What Was NOT Changed

- **Implementation code:** No implementation code was written per instructions
- **Features:** Feature files in `features/` were not modified
- **UI components:** Tiptap and React Flow remain in dependency register but marked as "spike later"
- **Cloud Sync:** Spec 010 not affected by review
- **Connectors:** Spec 009 not affected by review

## ADR Index

| ADR | Decision | Status |
|-----|----------|--------|
| ADR-001 | Qdrant as MVP vector database | Accepted |
| ADR-002 | FastEmbed as MVP embedding layer | Accepted |
| ADR-003 | MCP Python SDK as MVP agent interface | Accepted |
| ADR-004 | Kuzu rejected for MVP | Rejected |
| ADR-005 | External repos reference-only | Accepted |

## Next Steps

1. **Implement ADRs in plan phase** — ADRs guide technical decisions
2. **Create infra/docker/docker-compose.local.yml** — Add Qdrant service
3. **Create services/mcp-server/requirements.txt** — Add MCP Python SDK
4. **Create services/embedding-service/requirements.txt** — Add FastEmbed
5. **Design SQLite graph placeholders** — Entity/relationship schema for MVP
6. **Reference external repos** — Use patterns without importing code

## Files Reference Index

All evaluated repositories are located in:
```
external/reference/
├── engram-memory/      # Reference only (BSL license, archived)
├── markitdown/         # Reference only (MIT license)
├── unstructured/       # Reference only (Apache 2.0)
├── graphrag/           # Reference only (MIT license)
├── graphiti/           # Reference only (Apache 2.0)
├── cognee/             # Reference only (Apache 2.0)
└── kuzu/               # Rejected (archived project)
```

All evaluation files are in:
```
docs/open-source/
├── [repo]-evaluation.md (7 files)
├── dependency-register.md
├── open-source-adoption-plan.md
├── licence-risk-register.md
└── spec-update-summary.md
```

All ADRs are in:
```
docs/adr/
├── ADR-001-qdrant-mvp-vector-database.md
├── ADR-002-fastembed-mvp-embedding-layer.md
├── ADR-003-mcp-python-sdk-mvp-agent-interface.md
├── ADR-004-kuzu-rejected-mvp.md
└── ADR-005-external-repos-reference-only.md
```