# Decision Register

**Status:** Active
**Date:** 2026-05-31
**Owner:** OmniVia Team

---

## Purpose

This register tracks all major architectural, product, and strategic decisions for OmniVia. Each decision is linked to its ADR and supporting documentation.

---

## Active Decisions

| ID | Title | Status | Date | Owner |
|----|-------|--------|------|-------|
| [ADR-0001](./ADR-0001-build-omnivia-dev-first.md) | Build OmniVia Dev First | Accepted | 2026-05-31 | OmniVia Team |
| [ADR-0002](./ADR-0002-use-dreamgraph-as-reference-not-dependency.md) | Use DreamGraph as Reference, Not Dependency | Accepted | 2026-05-31 | OmniVia Team |
| [DEC-0003](./DEC-0003-build-omnivia-dev-phase-1-memory-core-in-python.md) | Build OmniVia Dev Phase 1 Memory Core in Python | Accepted | 2026-05-31 | OmniVia Team |
| [ADR-004](./../adr/ADR-004-domain-model.md) | OmniVia Local Knowledge Domain Model | Proposed | 2026-05-30 | Claude |
| [ADR-005](./../adr/ADR-005-external-repos-reference-only.md) | External Repos Reference Only | Accepted | 2026-05-30 | Claude |

---

## Decision Categories

### Strategy

| ID | Title | Rationale |
|----|-------|-----------|
| ADR-0001 | Build OmniVia Dev First | Internal users first, core validates before external |
| ADR-0002 | Use DreamGraph as Reference | Patterns valuable, code not to be copied |

### Architecture

| ID | Title | Rationale |
|----|-------|-----------|
| ADR-004 | Domain Model | Layered model with Source, Memory, Node, Edge |
| ADR-005 | External Repos Reference Only | Clean boundaries, no license complications |
| DEC-0003 | Dev Phase 1 Python Core | Python fits long-term memory/intelligence needs |

### Accepted Implementation Decisions

| Topic | Decision | Status |
|-------|----------|--------|
| Memory/intelligence core language | Python | Accepted |
| MCP server language | Python for Phase 1 | Accepted |
| CLI language | Python for Phase 1 | Accepted |
| Future product UI language | TypeScript / React / Tauri deferred for UI/product surfaces | Accepted for later |
| Package structure | Python service under `services/omnivia-memory` for Phase 1 | Accepted |
| Vector store | Defer for MVP; use keyword search first | Accepted |
| Project indexing | Deferred to Phase 2 Project Source Ingestion | Accepted |
| DreamGraph usage | Reference only; do not copy source code or import from `external/reference/` | Accepted |
| Phase 1 scope | Memory core only; no project indexing, repo scanning, semantic search, vector store, graph enrichment, graph traversal, dashboard UI, desktop app, cloud sync, external connectors, or agent workflow automation | Accepted |
| Controlling document | MVP spec controls Phase 1 scope | Accepted |

### Pending Decisions

The following decisions are pending or under consideration:

| Topic | Description | Status |
|-------|-------------|--------|
| LLM Integration | How to integrate with language models | Pending |

---

## Decision Process

### Creating a Decision

1. **Identify** the decision to be made
2. **Document** context, alternatives, and rationale in an ADR
3. **Review** with team (async or sync)
4. **Accept/Reject** the decision
5. **Record** in this register
6. **Implement** according to decision
7. **Revisit** if context changes significantly

### ADR Template

Each ADR should include:
- Context (what's the situation?)
- Decision (what was decided?)
- Rationale (why this choice?)
- Alternatives (what else was considered?)
- Consequences (what are the impacts?)
- Review criteria (when to revisit?)

---

## Review Schedule

| Decision | Last Review | Next Review | Notes |
|----------|-------------|-------------|-------|
| ADR-0001 | 2026-05-31 | 2026-07-15 | 30 days after implementation |
| ADR-0002 | 2026-05-31 | 2026-07-15 | 30 days after implementation |
| ADR-004 | 2026-05-30 | 2026-06-30 | After node/edge MVP |
| ADR-005 | 2026-05-30 | 2026-06-30 | After external repos reviewed |

---

## Decision Dependencies

Some decisions depend on others:

```
ADR-0001 (Dev First)
    │
    ├──▶ ADR-0002 (Reference DreamGraph)
    │        │
    │        └──▶ ADR-004 (Domain Model)
    │
    └──▶ DEC-0003 (Phase 1 Python Memory Core)
             │
             └──▶ Phase 1 implementation handoff

ADR-005 (External Repos Reference)
    │
    └──▶ ADR-0002 (DreamGraph Reference)
```

---

## Archive

### Superseded Decisions

| ID | Title | Superseded By | Date |
|----|-------|---------------|------|
| None yet | | | |

### Rejected Decisions

| ID | Title | Reason | Date |
|----|-------|---------|------|
| None yet | | | | |

---

## How to Update This Register

1. When a new decision is made, add to Active Decisions table
2. When a decision is superseded, move to Archive
3. When reviewing a decision, update Last Review date
4. When closing a decision, add to Archive with outcome

---

## Related Documents

- [OmniVia Dev First Strategy](../strategy/omnivia-dev-first-strategy.md)
- [OmniVia Dev MVP Spec](../specs/omnivia-dev-mvp-spec.md)
- [OmniVia Core Architecture](../architecture/omnivia-core-architecture.md)
- [DreamGraph Reference Analysis](../research/dreamgraph-reference-analysis.md)
- [Definition of Done](../quality/definition-of-done.md)
