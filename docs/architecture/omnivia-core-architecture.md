# OmniVia Core Architecture

**Status:** Draft
**Date:** 2026-05-31

---

## 1. Architecture Overview

OmniVia is a **local-first, cloud-scalable, governed knowledge and agent memory layer**.

The architecture is designed to be:
- **Modular** — the Python memory/intelligence core can later serve multiple apps and UI surfaces
- **Governed** — agent-created knowledge requires approval
- **Source-backed** — facts track provenance to prevent hallucination
- **Graph-native** — knowledge is connected, not isolated

```
┌─────────────────────────────────────────────────────────────┐
│                      OmniVia Core                           │
│  ┌──────────────────┐ ┌─────────────┐ ┌──────────────────┐ │
│  │ omnivia-memory   │ │ MCP server  │ │ graph layer      │ │
│  │ (Python core)    │ │ (Python)    │ │ (future)         │ │
│  └──────────────────┘ └─────────────┘ └──────────────────┘ │
└─────────────────────────────────────────────────────────────┘
         │                 │                    │
         ▼                 ▼                    ▼
┌─────────────────┐ ┌─────────────┐ ┌─────────────────────────┐
│  services/      │ │  apps/      │ │  features/              │
│  omnivia-memory │ │  local      │ │  project-ingestion      │
│                 │ │  (future)   │ │  cognitive-enrichment   │
└─────────────────┘ └─────────────┘ └─────────────────────────┘
         │                 │
         ▼                 ▼
   ┌─────────────┐   ┌─────────────┐
   │ Python CLI  │   │ omni-local  │
   │ + MCP       │   │ (Tauri app) │
   └─────────────┘   └─────────────┘
```

---

## 2. Service and Package Architecture

### 2.1 Phase 1 Service Hierarchy

```
services/
└── omnivia-memory/          # Python memory/intelligence core
    ├── src/
    │   └── omnivia_memory/
    │       ├── memory/      # Memory model and service
    │       ├── search/      # Keyword search first
    │       ├── provenance/  # Source references
    │       ├── lifecycle/   # proposed/observed/approved/rejected
    │       ├── mcp/         # Python MCP server
    │       └── cli/         # Python CLI
    ├── tests/
    └── pyproject.toml
```

### 2.2 Phase 1 Responsibilities

**omnivia-memory**
- Python memory domain model
- Local persistence
- Keyword search
- Source/provenance handling
- Lifecycle and approval rules
- Python CLI
- Python MCP server over stdio

**Future TypeScript product packages**
- Shared UI
- Graph viewer
- Connector setup UI
- Dashboard UI
- Review workflows
- Tauri/React desktop surfaces

**Future graph and semantic intelligence layer**
- Node and edge storage
- Graph traversal algorithms
- Relationship queries
- Graph-aware MCP tools after Phase 1
- Semantic search and vector store after Phase 1

---

## 3. Shared Core/App Architecture

### 3.1 Why A Python Core First?

**Reuse across apps and agents:**
- OmniVia Dev and OmniVia Local can share the same memory/intelligence core
- Changes to memory model benefit both apps
- MCP tools work the same way for both

**Clear boundaries:**
- Python owns memory, ingestion, enrichment, retrieval, and MCP
- TypeScript owns future product UI surfaces
- Testing is scoped to the service or package being changed

**Dependency flow:**
```
services/omnivia-memory (Python core)
    │
    ▼
apps/ and packages/ (future product surfaces)
    │
    ▼
infra/ (deployment)
```

### 3.2 App Variations

**OmniVia Dev:**
```
services/omnivia-memory/
├── src/
│   └── omnivia_memory/
│       ├── cli/         # Python CLI
│       ├── mcp/         # Python MCP server
│       └── memory/      # Memory core
├── tests/
├── pyproject.toml
└── README.md
```

Commands:
- `omnivia-dev init` — initialize instance
- `omnivia-dev serve` — start MCP server
- `omnivia-dev memory ...` — create, list, retrieve, update, delete, and search memories
- `omnivia-dev index` — future Phase 2 project source ingestion

**OmniVia Local:**
```
apps/local/
├── desktop/            # Future Tauri shell
├── workspace/          # Future local workspace UI
├── package.json
└── README.md
```

Features:
- Document import
- Web UI for memory management
- Privacy-preserving local storage

---

## 4. Data Architecture

### 4.1 Storage Layers

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Structured** | SQLite | Memories first; nodes, edges, ADRs later |
| **Vector** | Deferred | Semantic memory search after MVP |
| **File System** | Local files | Large assets, cached scans |
| **Configuration** | JSON files | Instance config, policies |

### 4.2 Instance Model

Each OmniVia instance (project) has isolated storage:

```
~/.omnivia/
├── instances.json          # Master registry
└── <instance-uuid>/
    ├── instance.json       # Identity
    ├── config/
    │   ├── mcp.json        # MCP settings
    │   ├── policies.json   # Approval policies
    │   └── engine.env      # LLM settings
    ├── data/
    │   ├── memories.db     # SQLite: memories
    │   ├── graph.db         # SQLite: nodes/edges
    │   └── adrs.db         # SQLite: decisions
    └── logs/
        └── omnivia.log     # Activity log
```

### 4.3 Data Models

**Memory:**
```python
class Memory:
    id: str                 # UUID
    content: str            # Knowledge content
    source: Source          # Provenance reference
    lifecycle_state: str    # proposed, observed, approved, rejected
    memory_type: str        # general, decision, pattern, constraint
    created_by: str         # human or agent
    created_at: str         # ISO timestamp
    updated_at: str

class Source:
    type: str               # file, url, adr, human
    reference: str          # Path, URL, or description
```

**Node (Graph, post-Phase 1 pseudocode):**
```python
class Node:
    id: str
    node_type: str          # concept, service, package, file, decision, person
    title: str
    body: str
    tags: list[str]
    source_ids: list[str]   # References to sources
    metadata: dict
    created_at: str
    updated_at: str
```

**Edge (Graph, post-Phase 1 pseudocode):**
```python
class Edge:
    id: str
    source_node_id: str
    target_node_id: str
    relationship_type: str  # derives_from, references, implements, depends_on, supports, relates_to, belongs_to
    weight: float           # 0.0 - 1.0
    direction: str          # directed or bidirectional
    created_at: str
```

---

## 5. MCP Architecture

### 5.1 Tool Categories

**Memory Tools:**
- `memory_store` — Store new memory with source
- `memory_search` — Search by keyword in Phase 1
- `memory_get` — Get by ID
- `memory_list` — List stored memories
- `memory_update` — Update an existing memory
- `memory_approve` — Approve proposed memory
- `memory_reject` — Reject memory
- `memory_delete` — Delete memory

**Post-Phase 1 Graph Tools:**
- `graph_get_node` — Get node by ID
- `graph_search` — Search nodes by type/properties
- `graph_get_neighbors` — Get adjacent nodes
- `graph_get_path` — Find path between nodes
- `graph_create_node` — Create node
- `graph_create_edge` — Create edge

**Post-Phase 1 Decision Tools:**
- `decision_get` — Get ADR by ID
- `decision_search` — Search ADRs
- `decision_create` — Create ADR
- `decision_update` — Update ADR

**Post-Phase 1 Context Tools:**
- `context_get_project` — Get project overview
- `context_get_service` — Get service info
- `context_get_dependencies` — Get dependency graph

### 5.2 MCP Server Structure

```python
# omnivia_memory/mcp/server.py
def create_omnivia_server(config: ServerConfig) -> McpServer:
    server = McpServer(name="omnivia", version="0.1.0")

    register_memory_tools(server)

    # Graph, decision, and context tools are added after Phase 1.
    return server
```

### 5.3 Transport Layer

**Primary:** stdio
- Standard input/output communication
- For MCP client integration
- Production use

**Secondary:** HTTP
- For debugging and direct access
- Development use only
- Optional feature

---

## 6. Governance Architecture

### 6.1 Approval Workflow

```
┌──────────────┐     Store      ┌──────────────┐
│ Human        │ ────(direct)──▶│ APPROVED     │
│ Memory       │                 │ Memory       │
└──────────────┘                 └──────────────┘

┌──────────────┐    Store       ┌──────────────┐
│ AI Agent     │ ────(auto)────▶│ PROPOSED     │
│ Memory       │                 │ Memory       │
└──────────────┘                 └──────────────┘
                                          │
                        ┌─────────────────┴─────────────────┐
                        ▼                                   ▼
               ┌──────────────┐                    ┌──────────────┐
               │ Human        │                    │ Source       │
               │ Approval     │                    │ Verified     │
               └──────────────┘                    └──────────────┘
                        │                                   │
                        ▼                                   ▼
               ┌──────────────────────┐           ┌──────────────────┐
               │ APPROVED (if human   │           │ OBSERVED (auto   │
               │ explicitly approves) │           │ on source match) │
               └──────────────────────┘           └──────────────────┘
```

### 6.2 Source Verification

When a memory's source is verified:
1. Check if source file/ADR exists
2. Verify content matches reference
3. If verified → transition to `observed`
4. Human can then approve `observed` → `approved`

### 6.3 Audit Trail

All state transitions are logged:
- Timestamp
- Memory ID
- Previous state
- New state
- Actor (human/agent ID)
- Reason (if provided)

---

## 7. Reuse Between Dev and Local

### 7.1 Shared Core Benefits

**Memory Model:** Same for both
- Dev: project knowledge
- Local: user documents

**Graph Model:** Same for both
- Dev: project structure
- Local: document relationships

**MCP Tools:** Same for both
- Dev: CLI access
- Local: Tauri desktop app

### 7.2 Differences by App

| Aspect | OmniVia Dev | OmniVia Local |
|--------|-------------|---------------|
| Frontend | CLI | Tauri desktop app |
| Indexer | Project scanner | Document importer |
| User | AI agents (primary) | Humans (primary) |
| Data scope | Project | User's documents |
| Privacy | No sensitive data | User's private data |

### 7.3 Extension Pattern

```
services/omnivia-memory (Python core)
    │
    ├──▶ OmniVia Dev     (CLI + MCP)
    │           │
    └──▶ OmniVia Local   (future Tauri + document importer)
```

---

## 8. Key Architectural Decisions

| Decision | Rationale |
|----------|----------|
| SQLite for storage | Portable, single-file, zero-config |
| MCP for tool surface | Standard AI agent interface |
| Instance isolation | Multiple projects, clean boundaries |
| Approval workflow | Governance for AI-created knowledge |
| Source references | Provenance tracking, hallucination prevention |
| Python memory core | Long-term fit for ingestion, AI processing, retrieval, and GraphRAG-style workflows |
| TypeScript UI later | Product surfaces can use React/Tauri without owning the intelligence core |

---

## 9. Related Documents

- [OmniVia Dev First Strategy](../strategy/omnivia-dev-first-strategy.md)
- [OmniVia Dev MVP Spec](../specs/omnivia-dev-mvp-spec.md)
- [DreamGraph Reference Analysis](../research/dreamgraph-reference-analysis.md)
- [ADR-0001: Build OmniVia Dev First](../decisions/ADR-0001-build-omnivia-dev-first.md)
- [ADR-0002: Use DreamGraph as Reference](../decisions/ADR-0002-use-dreamgraph-as-reference-not-dependency.md)
