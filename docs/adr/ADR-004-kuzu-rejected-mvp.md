# ADR-004: Kuzu Rejected for MVP Graph Database

Status: Rejected
Date: 2026-05-30
Source: Open Source Repository Review

## Context

OmniVia's Knowledge Graph spec (Spec 007) planned to use Kuzu as the local embedded graph database. After reviewing the Kuzu repository, this decision must be reconsidered.

## Decision

**Reject Kuzu for MVP. Use SQLite-based graph placeholders instead.**

## Rationale for Rejection

1. **Project Archived:** Kuzu v0.11.x is the final release. The project is no longer actively maintained.
2. **Maintenance Risk:** Archived projects do not receive security updates, bug fixes, or new features.
3. **Long-term Support:** Building new dependencies on archived software creates technical debt.
4. **No Clear Successor:** No indication of project revival or migration path.

## Original Plan (Now Invalid)

> "Use Kuzu for local embedded graph storage when graph needs harden." — Spec 007 Plan

## New Approach for MVP

For MVP, implement a simple graph representation using SQLite tables:

```sql
-- Entity table (graph placeholder)
CREATE TABLE entities (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    source_id TEXT,
    approval_status TEXT DEFAULT 'proposed',
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Relationship table
CREATE TABLE relationships (
    id TEXT PRIMARY KEY,
    source_entity_id TEXT NOT NULL,
    target_entity_id TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    source_id TEXT,
    approval_status TEXT DEFAULT 'proposed',
    created_at TIMESTAMP,
    FOREIGN KEY (source_entity_id) REFERENCES entities(id),
    FOREIGN KEY (target_entity_id) REFERENCES entities(id)
);
```

## Future Graph Database Spike

Before production, spike evaluation of alternatives:
- **FalkorDB:** Redis-based, actively maintained, graph capabilities
- **Neo4j:** Mature, enterprise-supported, Cypher query language
- **Qdrant:** May add native graph capabilities in future releases

## Consequences

**Positive:**
- No dependency on archived project
- SQLite is battle-tested and actively maintained
- Simple migration path when proper graph DB selected
- Avoids technical debt from abandoned software

**Negative:**
- SQLite graph representation is less optimized than native graph DB
- Cypher query patterns not available in MVP
- May need significant refactoring when graph DB added

## Reference: Related Open Source Patterns

For future graph implementation, reference:
- **Graphiti** (external/reference/graphiti) — Temporal context graphs with driver abstraction
- **Cognee** (external/reference/cognee) — ECL pipeline with GraphDBInterface
- **GraphRAG** (external/reference/graphrag) — Community detection, workflow pipelines

## Review Date

Spike evaluation required before production graph database selection.

## Definition of Done

This ADR is done when:

1. **Documentation Updated:** Implementation docs reflect the SQLite graph placeholder approach.
2. **Comment Pass Complete:** Changed code has plain-English comments for complex logic.
3. **Peer Review Complete:** A review report exists in `docs/quality/reviews/`. Critical and High findings are fixed or explicitly accepted.
4. **Tests Pass:** Unit tests pass, integration tests pass, or manual validation is documented.
5. **External Code Boundary Check:** No implementation code imports from `external/reference/`.
6. **Final Summary:** The completion summary includes what changed, tests run, review result, docs updated, remaining risks, and commands to run.

See also: `docs/quality/definition-of-done.md`, `docs/templates/task-dod-template.md`