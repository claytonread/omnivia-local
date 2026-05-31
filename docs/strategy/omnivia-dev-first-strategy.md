# OmniVia Dev First Strategy

**Status:** Adopted
**Date:** 2026-05-31
**Supersedes:** Previous "OmniVia Local First" approach

---

## 1. Executive Summary

**OmniVia Dev is the first internal use case of OmniVia, focused on helping AI coding agents understand the OmniVia project itself.**

Building OmniVia Dev first before OmniVia Local provides:
- **Immediate value** — improves the team's own AI-assisted development
- **Fast feedback** — the team is the user, iterations are rapid
- **Proof of concept** — validates the architecture before external users
- **Living spec** — OmniVia's own documentation becomes the reference implementation

---

## 2. Why OmniVia Dev Before OmniVia Local

### 2.1 The Team Is the First User

OmniVia Dev serves the OmniVia development team. The team uses AI coding agents (Claude, Codex, Copilot) to build OmniVia. OmniVia Dev provides persistent memory for those agents.

**Benefits:**
- Zero user acquisition cost
- Instant feedback on usability
- Aligned incentives — the team wants it to work
- Direct access to users for UX iteration

### 2.2 Knowledge Is Already Available

OmniVia's codebase already contains:
- Architecture decisions (ADRs)
- Implementation patterns
- Domain model definitions
- Service boundaries

OmniVia Dev can index this knowledge immediately without waiting for external data.

### 2.3 The Problem Is Immediate

The team already experiences:
- Forgetting why decisions were made
- Inconsistent implementation patterns
- Knowledge scattered across files
- New team members slow to onboard

OmniVia Dev solves these problems for the team directly.

### 2.4 Risk Reduction

Building for external users (OmniVia Local) carries risks:
- User experience may not match assumptions
- Data privacy concerns with user documents
- Market validation needed
- Support infrastructure required

Building for internal use reduces these risks:
- Known users with direct feedback
- No external data privacy concerns
- Immediate validation of core functionality
- Team support is cheap

### 2.5 The Core Is Reusable

The core architecture (memory layer, graph, MCP tools) works for both:
- **OmniVia Dev** — project knowledge for AI agents
- **OmniVia Local** — user document knowledge for AI agents

Building the core first means OmniVia Local extends OmniVia Dev, not vice versa.

---

## 3. What OmniVia Dev Provides

### 3.1 Persistent Project Memory

AI coding agents often work across sessions. Without memory:
- Agent forgets previous context
- Same discussions repeat
- Decisions are revisited without knowing why

OmniVia Dev provides persistent memory that survives session boundaries.

### 3.2 Source-Backed Recall

When an AI agent makes a claim, it should cite sources:
- "Based on ADR-003, the MCP interface uses Python SDK"
- "The domain model (ADR-004) defines Memory with approval_status"

OmniVia Dev tracks source references so agents can verify claims.

### 3.3 Decision History

Architecture decisions live in ADRs, but:
- ADRs are hard to find
- Connections between decisions are invisible
- Context (why, who, when) is often missing

OmniVia Dev surfaces decision history with connections.

### 3.4 Graph Understanding

The project structure is a graph:
- Services depend on packages
- Features connect to services
- Decisions affect implementations

OmniVia Dev understands this graph and can answer questions like:
- "What services would this change affect?"
- "What's the dependency path from this file to that service?"
- "Which decisions cover this module?"

### 3.5 MCP Access

AI agents interact with OmniVia Dev through MCP tools:
- Query memory (what do we know about X?)
- Store insight (remember this pattern)
- Search decisions (find related ADRs)
- Get context (what files are relevant to Y?)

---

## 4. OmniVia Dev Target Users

### Primary: AI Coding Agents

The primary users are AI coding agents (Claude Code, Codex, Copilot) working on the OmniVia codebase. These agents need:
- Project structure awareness
- Decision context
- Implementation pattern guidance
- Consistent terminology

### Secondary: Human Developers

Human developers benefit from:
- Better AI agent assistance (agents with memory work better)
- Self-documenting code (knowledge graph surfaces patterns)
- Onboarding acceleration (new team members get project context quickly)

---

## 5. OmniVia Dev vs OmniVia Local

| Aspect | OmniVia Dev | OmniVia Local |
|--------|-------------|---------------|
| **Users** | AI coding agents (internal) | External end users |
| **Data** | OmniVia codebase + team knowledge | User documents and notes |
| **Scope** | Project-level knowledge | Personal knowledge management |
| **Access** | MCP tools for AI agents | Web UI for humans |
| **Approval** | Team validates AI knowledge | User validates their knowledge |
| **Privacy** | No external data | User data stays on device |
| **Deployment** | Team infrastructure | Local desktop app |

**Key Insight:** OmniVia Dev is the prototype for OmniVia Local. The core architecture serves both; the frontend shell differs.

---

## 6. Strategic Benefits

### 6.1 Internal Marketing

When OmniVia Dev works well, the team becomes advocates:
- Demo to stakeholders
- Case studies for sales
- Real usage metrics
- Feedback for improvements

### 6.2 Architecture Validation

Building for internal use validates:
- MCP tool design
- Memory model
- Graph structure
- Approval workflow

If it works for OmniVia, it likely works for OmniVia Local users.

### 6.3 Reduced Time to Market

OmniVia Dev can ship before OmniVia Local:
- No user research needed
- No UX design for end users
- No support infrastructure
- No marketing materials

Ship OmniVia Dev first, then extend to Local.

### 6.4 Technical Acceleration

The team using OmniVia Dev builds faster:
- AI agents with memory work better
- Less time explaining context to agents
- Consistent patterns across the codebase
- Decision rationale always available

---

## 7. Success Metrics

### 7.1 Adoption Metrics

- AI agents use OmniVia Dev tools consistently
- Memory queries return relevant results
- Source references are cited in agent output

### 7.2 Quality Metrics

- Fewer repeated decisions (ADR reuse increases)
- Faster onboarding (new team members ramp faster)
- Consistent implementation patterns

### 7.3 Technical Metrics

- MCP tool latency acceptable (< 200ms)
- Memory retrieval accuracy high (relevant results)
- Graph traversal useful (answers real questions)

---

## 8. Phases

### Phase 1: Memory Core (MVP)
- Python memory/intelligence service
- Local memory persistence
- Create/store, list, retrieve/get, update, delete, and keyword search memory
- Source/provenance fields
- Memory lifecycle workflow
- Basic Python CLI and MCP server
- Basic test coverage

Phase 1 explicitly excludes project indexing, repo scanning, semantic search, vector store, graph enrichment, graph traversal, dashboard UI, desktop app, cloud sync, external connectors, and agent workflow automation.

### Phase 2: Project Source Ingestion
- Repo and document scanning
- Source references
- File metadata
- Source-backed recall
- Project context ingestion
- Project ontology
- Decision and task source linking

### Phase 3: Graph and Semantic Intelligence
- Node/Edge model implementation
- Relationship traversal
- Decision graph
- Dependency tracking
- Semantic search
- Vector store
- Graph enrichment

### Phase 4: Dev Agent Workflow Support
- Automatic pattern detection
- Knowledge consolidation
- Tension surfacing
- Recommendation generation
- Agent workflow support

### Phase 5: OmniVia Local Productisation
- User document indexing
- Personal knowledge management
- Local deployment (Tauri shell)
- Privacy-preserving architecture
- Dashboard UI
- Connector setup screens
- Review workflows

---

## 9. Risk Mitigation

### Risk: Team Doesn't Use It
**Mitigation:** Make it valuable to AI agents, not just humans. If Claude Code uses OmniVia Dev, the team benefits automatically.

### Risk: Architecture Doesn't Scale to Local
**Mitigation:** Design core for extensibility. Separation of concerns (memory, graph, MCP) allows different frontends.

### Risk: MVP Is Too Limited
**Mitigation:** Define MVP scope tightly. Core MCP tools + memory store + approval workflow. Extend based on feedback.

### Risk: Dependency on Internal Build
**Mitigation:** Document architecture clearly. External users can deploy their own OmniVia Dev instances.

---

## 10. Decision Record

This strategy is recorded in:
- `docs/decisions/ADR-0001-build-omnivia-dev-first.md`
- `docs/decisions/decision-register.md`

Re-evaluate after Phase 1 MVP completion based on adoption metrics and user feedback.

---

## Related Documents

- [DreamGraph Reference Analysis](../research/dreamgraph-reference-analysis.md)
- [OmniVia Dev MVP Spec](../specs/omnivia-dev-mvp-spec.md)
- [OmniVia Core Architecture](../architecture/omnivia-core-architecture.md)
- [ADR-0001: Build OmniVia Dev First](./decisions/ADR-0001-build-omnivia-dev-first.md)
