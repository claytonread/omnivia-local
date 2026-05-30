# ADR-004: OmniVia Local Knowledge Domain Model

Status: Proposed
Date: 2026-05-30
Owner: Claude
Reviewer: Codex

## Context

OmniVia needs a stable domain model before graph visualisation and AI context features grow further. We have a partial implementation (Memory, Source) and architectural notes that outline future entities (Node, Edge, Workspace, ContextPack). This ADR consolidates the current state and defines the path forward.

## Decision

**Adopt a layered domain model with four core entities: Source, Memory, Node, and Edge.**

The model evolves in three phases:

### Phase 1: Existing (Implemented)

**Source** — An original artefact imported or referenced by OmniVia.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| source_type | String | e.g. "file", "url", "chat_export" |
| uri | String | File path, URL, or identifier |
| title | String | Human-readable title |
| file_hash | String | SHA-256 of content (for dedup) |
| file_size | Integer | Size in bytes |
| imported_at | DateTime | When first imported |
| last_indexed_at | DateTime | When content was last parsed |
| metadata_json | Text | Arbitrary metadata as JSON |

**Memory** — A unit of knowledge with semantic embedding.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| content | Text | The actual knowledge content |
| source | String | Reference to source (URI or description) |
| memory_type | String | e.g. "general", "decision", "constraint" |
| approval_status | String | "proposed" \| "observed" \| "approved" |
| created_by | String | "human" \| "agent" |
| created_at | DateTime | Creation timestamp |
| embedding_id | String | Reference to vector store entry |

**Rationale for Phase 1:**
- Memory is already implemented and working
- Source model provides provenance tracking
- Approval status handles the agent trust problem (proposed → observed → approved)

### Phase 2: Near-term (Next Implementation)

**Node** — A unit of structured knowledge with explicit type.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| node_type | String | e.g. "concept", "person", "project", "decision" |
| title | String | Short label |
| body | Text | Rich content or summary |
| tags | String | Comma-separated tags |
| source_ids | String | JSON array of source IDs |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last modification |
| metadata_json | Text | Type-specific metadata |

**Edge** — A relationship between nodes.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| source_node_id | UUID | The subject node |
| target_node_id | UUID | The object node |
| relationship_type | String | e.g. "relates_to", "depends_on", "supports" |
| direction | String | "directed" \| "bidirectional" |
| weight | Float | Confidence 0-1 (default 0.5) |
| source_ids | String | JSON array of source IDs |
| created_at | DateTime | Creation timestamp |

**Predefined Relationship Types:**

| Type | Description | Direction |
|------|-------------|-----------|
| relates_to | General association | bidirectional |
| depends_on | Dependency relationship | directed |
| supports | Evidence or backing | directed |
| contradicts | Opposition or conflict | bidirectional |
| belongs_to | Membership or containment | directed |
| references | Citation or link | directed |
| implements | Realization of specification | directed |
| derived_from | Transformation or derivation | directed |

**Rationale for Phase 2:**
- Node adds explicit typing (vs. generic Memory)
- Edge enables graph traversal and relationship queries
- Source tracking preserved for provenance

### Phase 3: Future (Not Yet Implemented)

**Workspace** — A bounded local knowledge environment.

**ContextPack** — A curated export of relevant knowledge.

These are noted for completeness but not implemented in MVP.

## Relationship Diagram

```
Source (1) ──imports── (*,N) Memory
Source (1) ──imports── (*,N) Node

Memory (N) ──derived_from── (1) Node
Node (N) ──connects_via── (N) Edge ──connects_via── (N) Node

Workspace (1) ──contains── (*,N) Source
Workspace (1) ──contains── (*,N) Memory
Workspace (1) ──contains── (*,N) Node
```

## Migration Path

**Step 1:** Keep existing Memory model — it works for embedding-based retrieval.

**Step 2:** Add Node and Edge as separate tables with explicit relationships.

**Step 3:** Optional: Migrate Memories to Nodes once Node model is stable (future).

## Consequences

**Positive:**
- Clear separation between embeddings (Memory) and structured knowledge (Node)
- Graph relationships enable traversal queries
- Provenance preserved through source tracking
- Extensible for future entity types

**Negative:**
- Two parallel paths (Memory vs Node) may cause confusion initially
- More complex queries require graph traversal logic

## Implementation Notes

1. Node and Edge tables should be added as new SQLAlchemy models in `services/api/models.py`
2. Source tracking via `source_ids` JSON field maintains provenance
3. Edge creation should validate that both nodes exist
4. Consider adding a NodeService similar to MemoryService for CRUD operations

## Review Date

Re-evaluate after Node/Edge MVP implementation or when Memory model needs to evolve.