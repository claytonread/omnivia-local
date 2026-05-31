# ADR-0002: Use DreamGraph as Reference, Not Dependency

**Status:** Accepted
**Date:** 2026-05-31
**Owner:** OmniVia Team

---

## Context

DreamGraph (v12.1.0) has been cloned to `external/reference/dreamgraph-reference` for architectural analysis. DreamGraph is a source-available project with significant overlap with OmniVia goals:

- Graph-first cognitive memory
- MCP tool surface
- Knowledge graph with provenance
- Instance-scoped isolation
- Cognitive engine with dream cycles

This ADR establishes how OmniVia will use DreamGraph.

---

## Decision

**Treat DreamGraph as architectural reference only. Do not import DreamGraph code as dependencies.**

OmniVia will:
- Reference DreamGraph patterns and concepts
- Implement own solutions aligned with OmniVia needs
- Maintain clean external code boundaries
- Never copy source code from `external/reference/dreamgraph-reference/`

---

## Rationale

### 1. Licensing

DreamGraph uses the **DreamGraph Source-Available Community License v2.0**. This license:
- Allows viewing and using the source code
- Restricts commercial use
- Requires attribution
- Does not qualify as OSI-approved open source

Direct dependency on DreamGraph would complicate OmniVia's licensing and distribution.

### 2. Scope Mismatch

DreamGraph's scope exceeds OmniVia's current needs:

| Aspect | DreamGraph | OmniVia Dev MVP |
|--------|-----------|----------------|
| VS Code Extension | Yes | No (MCP only) |
| Explorer UI (Sigma/Three.js) | Yes | No |
| Copilot/Codex CLI Adapters | Yes | No |
| Plugin Host SDK | Yes | Future consideration |
| Full Cognitive Engine | Yes | Simplified |

DreamGraph implements features OmniVia doesn't need. Reference architecture allows us to pick and choose.

### 3. Architecture Differences

Key differences make direct code reuse impractical:

| Aspect | DreamGraph | OmniVia |
|--------|-----------|---------|
| Language | TypeScript | Python primary, TypeScript optional |
| Database | SQLite + custom | SQLite first; vector store deferred |
| LLM Integration | Core feature | Optional enhancement |
| Graph Model | Features/workflows/ADRs | Memory/Node/Edge/ADR |
| Dream Engine | Full cognitive loop | Simplified knowledge capture |

### 4. ADR-005 Alignment

ADR-005 already establishes external repos as reference only:

> Treat EngramMemory, MarkItDown, Unstructured, GraphRAG, Graphiti, and Cognee as reference only for MVP. Do not import these repositories as dependencies.

This ADR extends that policy to DreamGraph.

### 5. Clean Architecture

Using DreamGraph as reference enables:
- Independent evolution
- No external dependency risk
- Full architectural control
- Clear boundaries for future decisions

---

## What To Reference

### 1. Instance Model Pattern

DreamGraph's UUID-scoped instance organization provides a proven pattern for multi-project support.

**Reference:** `external/reference/dreamgraph-reference/src/instance/types.ts`

**Implement:** OmniVia instance and memory structure in `services/omnivia-memory/`

### 2. Graph Data Model

DreamGraph's fact graph structure (nodes + edges + provenance) validates our domain model.

**Reference:** `external/reference/dreamgraph-reference/src/graph/` and `src/tools/scan-project.ts`

**Implement:** Memory and Node/Edge models per ADR-004

### 3. MCP Tool Organization

DreamGraph's tool registration and categorization approach.

**Reference:** `external/reference/dreamgraph-reference/src/tools/register.ts`

**Implement:** OmniVia MCP tools in `services/omnivia-memory/src/omnivia_memory/mcp/`

### 4. Approval Workflow Concept

DreamGraph's "speculation is isolated from fact" principle.

**Reference:** `external/reference/dreamgraph-reference/src/cognitive/normalizer.ts`

**Implement:** OmniVia proposed/approved memory workflow

### 5. Source Provenance Requirements

DreamGraph's requirement that facts have traceable sources.

**Reference:** `external/reference/dreamgraph-reference/docs/cognitive-engine.md` (canonical promotion provenance)

**Implement:** Source reference tracking in OmniVia memory model

---

## What NOT To Copy

### Prohibited

| What | Why |
|------|-----|
| Source code from `src/` | License restrictions, scope mismatch |
| VS Code extension code | Not OmniVia's frontend approach |
| Explorer React components | Frontend shell is separate decision |
| Copilot/Codex adapters | IDE-specific, not needed |
| Plugin host implementation | Different plugin needs |
| Cognitive engine (dreamer/normalizer) | Overly complex for MVP |

### External Code Boundary

The following imports are prohibited:

```
# WRONG - Do not do this
from external.reference.dreamgraph_reference.src import ...
import external.reference.dreamgraph_reference as ...

# CORRECT - Reference only
# Copy patterns conceptually, implement own code
```

---

## Consequences

### Positive

1. **Clean licensing:** No source-available license complications
2. **Independent evolution:** OmniVia can evolve without DreamGraph constraints
3. **Right-sized scope:** Implement only what OmniVia needs
4. **Architectural learning:** Study proven patterns before implementing
5. **Future flexibility:** Can adopt more from DreamGraph later if needed

### Negative

1. **More implementation work:** Must build from patterns, not copies
2. **No production battle-testing:** Adopting DreamGraph code would include tested code
3. **Validation required:** Patterns must be validated for OmniVia use cases

---

## Implementation Guidance

### Reference Study Process

1. Read DreamGraph documentation in `external/reference/dreamgraph-reference/docs/`
2. Identify relevant patterns for OmniVia needs
3. Document patterns in `docs/research/dreamgraph-reference-analysis.md`
4. Implement own solution referencing patterns
5. Verify against DreamGraph example (conceptual comparison)

### Pattern Documentation

When borrowing a pattern, document:
- What the pattern does
- How DreamGraph implements it
- How OmniVia will implement it
- Why the approach fits OmniVia

### Verification

Before claiming a pattern is implemented:
1. Compare against DreamGraph reference behavior
2. Test edge cases the reference handles
3. Document any deliberate deviations
4. Review for correctness and completeness

---

## Review Date

Re-evaluate after OmniVia Dev MVP completion (Phase 1).

Consider deeper integration with DreamGraph patterns if:
1. MVP validates the approach
2. Team requests additional features
3. Architecture alignment is confirmed

---

## Related Documents

- [ADR-0001: Build OmniVia Dev First](./ADR-0001-build-omnivia-dev-first.md)
- [ADR-005: External Repos Reference Only](../adr/ADR-005-external-repos-reference-only.md)
- [DreamGraph Reference Analysis](../research/dreamgraph-reference-analysis.md)
- [OmniVia Core Architecture](../architecture/omnivia-core-architecture.md)

---

## Definition of Done

This ADR is done when:

1. **DreamGraph Reference Directory Created:** `external/reference/dreamgraph-reference/` exists with clone.
2. **Reference Analysis Documented:** `docs/research/dreamgraph-reference-analysis.md` covers useful patterns.
3. **External Code Boundary Enforced:** No imports from `external/reference/` in implementation.
4. **Strategy Updated:** `docs/strategy/omnivia-dev-first-strategy.md` references DreamGraph correctly.
5. **Architecture Updated:** `docs/architecture/omnivia-core-architecture.md` shows pattern reference.
6. **No Code Copying:** All implementation is original, patterns only.

See also: `docs/quality/definition-of-done.md`, `docs/templates/task-dod-template.md`
