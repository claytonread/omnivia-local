# Repo Evaluation: engram-memory

## 1. Executive Summary
- Engram Memory provides a sophisticated three-tiered memory system with ACT-R cognitive science foundations—OmniVia should adopt this tiered caching concept for performance
- Uses Qdrant + FastEmbed for semantic search with zero API costs—ideal for local-first architecture
- Includes MCP server with 15 tools—directly aligns with OmniVia's MCP integration goals
- BSL 1.1 license permits internal use but restricts commercial SaaS offerings—acceptable for MVP phase
- Features multi-device memory sharing (Hives), conflict detection, and credential scrubbing—enterprise-ready patterns worth implementing
- Hot-tier ACT-R cache gets faster with use—unique performance optimization not found elsewhere

## 2. What It Does
Engram Memory is a three-tiered persistent memory system for AI agents that stores, searches, recalls, and forgets memories using semantic embeddings with zero API costs. It implements ACT-R cognitive theory with tiered retrieval that improves performance the more it's used.

## 3. Technology Stack
- **Language:** Python 3.12, TypeScript (OpenClaw plugin)
- **Frameworks:** FastAPI, Uvicorn, MCP (Model Context Protocol)
- **Databases:** Qdrant (vector), Kuzu (graph), in-memory hot-tier cache
- **Embeddings:** FastEmbed (ONNX-based, local), nomic-embed-text-v1.5 model
- **Search:** BM25 sparse vectors, cosine similarity, LSH (Locality Sensitive Hashing)
- **Infrastructure:** Docker (all-in-one or 3-container compose)
- **Package Manager:** uv with locked dependencies
- **Ports:** 6333 (Qdrant), 11435 (FastEmbed), 8585 (MCP)

## 4. Architecture
**Three-Tier Recall Engine:**
1. **Tier 1 - Hot-Tier Cache** (`hot_tier.py`): Sub-millisecond in-memory cache using ACT-R cognitive model with base-level activation and exponential decay. Max 1,000 entries.
2. **Tier 2 - Multi-Head Hash Index** (`multi_head_hasher.py`): O(1) candidate retrieval via Locality Sensitive Hashing with Matryoshka representation learning (64-dim fast slice with 4-6 hash heads).
3. **Tier 3 - Hybrid Vector Search** (`recall_engine.py`): Full 768-dimensional cosine similarity in Qdrant + BM25 sparse vectors via Reciprocal Rank Fusion.
4. **Graph Layer** (`graph_layer.py`): Kuzu-backed entity graph for cross-category connections and spreading activation.

**MCP Server:** 15 tools exposed via MCP protocol for memory_store, memory_search, memory_recall, memory_forget, memory_consolidate, memory_connect, memory_feedback, hive operations.

**Community Edition Caps:** Hot-tier 1,000 entries, hash index 4 heads/12-bit, entity graph 500 entities.

## 5. Important Files and Folders
- `/src/recall/recall_engine.py` (65KB) — Main orchestrator for three-tier system
- `/src/recall/hot_tier.py` (18KB) — ACT-R-based frequency cache
- `/src/recall/multi_head_hasher.py` (14KB) — LSH candidate retrieval
- `/src/recall/graph_layer.py` (17KB) — Kuzu entity graph integration
- `/mcp/server.py` (43KB) — MCP server with 15 tools
- `/src/index.ts` (22KB) — OpenClaw plugin
- `/docker/all-in-one/Dockerfile` — All-in-one container definition
- `/docker-compose.yml` — Multi-container setup

## 6. Licence and Commercial Risk
**Business Source License 1.1 (BSL-1.1)** from Engram Memory AI, LLC

- **Free for:** Internal use, research, self-hosted deployments
- **Prohibited:** Using as hosted/managed/SaaS offering for third parties
- **Service restriction:** Cannot offer as a service unless open-sourcing entire stack
- **Converts to:** Apache 2.0 after 4 years
- **Risk Level:** Low for MVP and internal use; requires licence review for commercial SaaS

## 7. What OmniVia Can Learn From It
- **Tiered caching architecture** with ACT-R cognitive model for memory activation/decay
- **Matryoshka representation learning** for hierarchical vector dimensions (64-dim fast, 768-dim full)
- **Multi-head LSH** for eliminating false positives in O(1) candidate retrieval
- **Credential scrubbing** (detects 20+ patterns) — important security pattern
- **Conflict detection** during store (similarity >= 0.82 checks for contradictions)
- **Automatic category detection** via keyword regex (13 types)
- **Hive-based multi-device memory sharing** pattern
- **Noise filtering** (short messages, generic responses, code blocks)

## 8. What OmniVia Should Not Reuse
- Hardcoded community edition caps (1,000 cache entries, etc.) for production scaling
- BSL license in our implementation—use Apache 2.0 for our code
- Kuzu as graph database (archived project)—use FalkorDB or Neo4j instead
- Engram Cloud extension pattern if we need cloud sync

## 9. Recommended Integration
reference only

## 10. Recommended Placement in OmniVia
external/reference/

## 11. Required Spec Kit Updates
- `specs/memory-architecture.md` — Add tiered caching pattern section
- `specs/mcp-integration.md` — Reference MCP tool patterns
- `docs/architecture/search-patterns.md` — Document ACT-R model and LSH concepts

## 12. Implementation Tasks to Add
- Implement tiered memory caching with hot/warm/cold tiers
- Add multi-head LSH for fast candidate retrieval
- Implement credential scrubbing in memory store pipeline
- Add conflict detection during memory consolidation
- Design Hive-based multi-device sharing mechanism

## 13. Final Recommendation
reference only

**Rationale:** While Engram Memory's tiered architecture and cognitive science foundations are excellent references, the BSL license restricts SaaS usage and the project is now archived (maintained but not actively developed). The architecture patterns are valuable for design reference, but OmniVia should implement similar patterns independently rather than depending on this library.