# ADR-0001: Build OmniVia Dev First

**Status:** Accepted
**Date:** 2026-05-31
**Owner:** OmniVia Team

---

## Context

OmniVia has two potential first use cases:

1. **OmniVia Dev** — Persistent project memory for AI coding agents working on OmniVia
2. **OmniVia Local** — Local knowledge management for external end users

The team has been considering which to build first. This decision formalizes the choice.

---

## Decision

**Build OmniVia Dev before OmniVia Local.**

OmniVia Dev is the first internal use case, focused on helping AI coding agents understand the OmniVia project itself.

---

## Rationale

### 1. Immediate Value

The OmniVia team is the first user. Building for internal use means:
- Zero user acquisition cost
- Instant feedback on usability
- Direct access to users for rapid iteration
- Aligned incentives — the team wants it to work

### 2. Fast Feedback Loop

Internal users provide:
- Faster iteration cycles
- Direct communication
- Real usage metrics
- Immediate bug reports

### 3. Knowledge Already Available

OmniVia's codebase contains the knowledge we need to index:
- ADRs (architecture decisions)
- Implementation patterns
- Domain model definitions
- Service boundaries

No external data collection needed.

### 4. Problem Is Immediate

The team already experiences:
- AI agents forgetting context between sessions
- Repeated discussions about past decisions
- Inconsistent implementation patterns
- Slow onboarding for new team members

### 5. Risk Reduction

External users (OmniVia Local) carry risks:
- User experience may not match assumptions
- Data privacy concerns with user documents
- Market validation needed before heavy investment
- Support infrastructure required

Internal use reduces these risks.

### 6. Core Is Reusable

The core architecture works for both:
- **OmniVia Dev** — project knowledge for AI agents
- **OmniVia Local** — user document knowledge for AI agents

Building core first means OmniVia Local extends OmniVia Dev, not vice versa.

---

## Alternatives Considered

### Alternative 1: OmniVia Local First

Build for external end users before internal use.

**Rejected because:**
- User research required before design
- Data privacy concerns complicate development
- Market validation uncertainty
- Team doesn't benefit until after external release
- Unknown user experience quality

### Alternative 2: Build Both Simultaneously

Split focus between Dev and Local.

**Rejected because:**
- Team capacity is limited
- Shared core not yet validated
- Risk of neither product being good
- Complexity of dual development

### Alternative 3: Research Phase First

Spend time researching before building anything.

**Rejected because:**
- Team has direct experience with the problem
- Quick prototype provides better feedback than research
- Building is learning

---

## Consequences

### Positive

1. **Immediate utility:** Team benefits as soon as MVP ships
2. **Rapid iteration:** Direct feedback from daily use
3. **Architecture validation:** Core tested in real use before external exposure
4. **Internal marketing:** Team becomes advocates when it works
5. **Technical acceleration:** AI agents with memory work better, improving team velocity

### Negative

1. **Single-user focus:** Architecture may be too project-specific
2. **No external validation:** Market fit not proven until OmniVia Local
3. **Team dependency:** Success depends on team adoption

### Mitigation

- Design core for extensibility (Python memory/intelligence core first)
- Document architecture for external deployers
- Plan OmniVia Local extension from day one
- Track adoption metrics to ensure value

---

## Implementation Plan

### Phase 1: Memory Core (MVP)

Priority order:
1. Python memory core under `services/omnivia-memory`
2. Local persistence
3. Basic memory operations (create, list, retrieve, update, delete, keyword search)
4. Source and provenance tracking
5. Memory lifecycle workflow
6. Python CLI and MCP server with stdio transport
7. Basic test coverage

Phase 1 explicitly excludes project indexing, repo scanning, semantic search, vector store, graph enrichment, graph traversal, dashboard UI, desktop app, cloud sync, external connectors, and agent workflow automation.

### Phase 2: Project Source Ingestion

After Phase 1 complete:
- Repo and document scanning
- Source references
- File metadata
- Source-backed recall
- Project context ingestion
- ADR, decision, and task source linking
- Project ontology

### Phase 3: Graph and Semantic Intelligence

After Phase 2:
- Node/Edge model
- Relationship traversal
- Decision graph
- Dependency tracking
- Semantic search
- Vector store
- Graph enrichment

### Phase 4: Dev Agent Workflow Support

Future:
- Pattern detection
- Knowledge consolidation
- Tension surfacing
- Recommendations
- Agent workflow support

### Phase 5: OmniVia Local Productisation

Future:
- User document indexing
- Personal knowledge management
- Tauri desktop shell
- Dashboard UI
- Connector setup screens
- Review workflows

---

## Decision Timeline

| Date | Milestone |
|------|-----------|
| 2026-05-31 | Decision recorded (this ADR) |
| 2026-06-01 | Begin Phase 1 implementation |
| 2026-06-15 | Phase 1 MVP complete |
| 2026-07-01 | Team adoption metrics collected |
| 2026-07-15 | Phase 2 complete |
| 2026-08-01 | Phase 3 complete |
| TBD | OmniVia Local planning |

---

## Review Criteria

This decision will be re-evaluated if:
1. Team adoption metrics show < 50% usage after 30 days
2. Architecture proves unsuitable for OmniVia Local extension
3. External users identify critical missing features too late

---

## Related Decisions

- [ADR-0002: Use DreamGraph as Reference, Not Dependency](./ADR-0002-use-dreamgraph-as-reference-not-dependency.md)
- [ADR-005: External Repos Reference Only](../adr/ADR-005-external-repos-reference-only.md)
- [ADR-004: Domain Model](../adr/ADR-004-domain-model.md)

---

## Definition of Done

This ADR is done when:

1. **Documentation Updated:** Strategy and spec documents reference this decision.
2. **Service Structure:** `services/omnivia-memory/` created for the Python Phase 1 memory core.
3. **MVP Implementation:** Phase 1 MVP code exists.
4. **First Tool Works:** At minimum `memory_store` tool operational.
5. **Team Adoption:** At least one team member using OmniVia Dev tools.
6. **Feedback Collected:** Team feedback documented for iteration.

See also: `docs/quality/definition-of-done.md`, `docs/templates/task-dod-template.md`
