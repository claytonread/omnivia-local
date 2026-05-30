# ADR-005: External Graph and Memory Repos as Reference Only

Status: Accepted
Date: 2026-05-30
Source: Open Source Repository Review

## Context

OmniVia reviewed seven open source repositories for potential adoption. After detailed evaluation, all six memory and graph repositories should be treated as architectural references only, not as direct dependencies.

## Decision

**Treat EngramMemory, MarkItDown, Unstructured, GraphRAG, Graphiti, and Cognee as reference only for MVP. Do not import these repositories as dependencies.**

## Summary of Decisions

| Repository | Decision | Key Reason |
|------------|----------|------------|
| EngramMemory | Reference Only | BSL 1.1 restricts SaaS; archived project |
| MarkItDown | Reference Only | Patterns valuable; implement own converter pipeline |
| Unstructured | Reference Only | Too opinionated; build own document processing |
| GraphRAG | Reference Only | Azure-centric; extract patterns only |
| Graphiti | Reference Only | Temporal patterns valuable; architecture differs |
| Cognee | Reference Only | Directly competes with OmniVia goals |
| Kuzu | Rejected | Archived project; SQLite fallback for MVP |

## Rationale by Repository

### EngramMemory
- **Value:** Three-tiered ACT-R caching, MCP tool patterns, credential scrubbing
- **Limitation:** BSL license restricts SaaS; archived project
- **Action:** Reference patterns; implement own tiered caching

### MarkItDown
- **Value:** Plugin architecture via entry points, converter registry pattern
- **Limitation:** Not a complete solution; just document conversion
- **Action:** Reference plugin pattern; build own document ingestion

### Unstructured
- **Value:** Element model hierarchy, dynamic metadata, lazy loading
- **Limitation:** Production-grade but too opinionated for OmniVia needs
- **Action:** Reference patterns; build own document processing

### GraphRAG
- **Value:** Factory pattern, workflow pipelines, four search strategies
- **Limitation:** Azure-centric, complex monorepo structure
- **Action:** Reference factory pattern and workflow design

### Graphiti
- **Value:** Temporal validity windows, episode provenance, hybrid retrieval
- **Limitation:** Architecture differs from OmniVia design
- **Action:** Reference temporal concepts; implement own model

### Cognee
- **Value:** ECL pipeline, interface-based database adapters, multi-tenant access
- **Limitation:** Directly competes with OmniVia goals
- **Action:** Reference patterns; do not adopt ECL architecture

## Reference Architecture Patterns

### Memory Layer (from EngramMemory)
- Tiered caching with ACT-R cognitive model
- Multi-head LSH for fast candidate retrieval
- Credential scrubbing in store pipeline

### Document Ingestion (from MarkItDown, Unstructured)
- Entry point plugin registration
- Priority-based converter ordering
- Stream-based processing with position preservation
- Element model hierarchy for document chunks

### Graph Layer (from GraphRAG, Graphiti, Cognee)
- Factory pattern for extensibility
- Workflow-based pipeline orchestration
- Temporal validity windows for facts
- Interface-based database adapters

### Query Strategies (from GraphRAG, Graphiti, Cognee)
- Local search (entity-focused)
- Global search (community-based)
- Hybrid retrieval (semantic + keyword + graph)
- Cross-encoder reranking

## Placement

All reference repositories are located in:
```
external/reference/
├── engram-memory/
├── markitdown/
├── unstructured/
├── graphrag/
├── graphiti/
└── cognee/
```

## Consequences

**Positive:**
- No license complications from BSL or other restrictive licenses
- Full architectural control over implementation
- Avoids opinionated designs that don't fit OmniVia
- Clean separation between reference and implementation

**Negative:**
- More implementation work than direct adoption
- Must validate patterns work for OmniVia use cases
- No production battle-testing of adopted code

## Review Date

Re-evaluate after MVP completion for potential deeper integration with any of these repositories.