# Repo Evaluation: cognee

## 1. Executive Summary
- Cognee is a mature AI memory platform with ECL pipeline (Extract, Cognify, Load)—directly competing with OmniVia's goals
- Apache 2.0 license enables full commercial use—no restrictions
- Interface-based database adapters for multiple graph/vector backends—excellent architecture pattern
- Pipeline-based processing with task orchestration—OmniVia should adopt this pattern
- MCP server included—aligns with OmniVia's MCP integration goals
- 12 search types including GRAPH_COMPLETION, RAG, CYPHER, TEMPORAL—comprehensive query coverage
- Multi-tenant access control with permission-based filtering—enterprise-ready

## 2. What It Does
Cognee is an open-source AI memory platform that gives AI agents a shared, improving memory of data, decisions, and workflows. It replaces traditional RAG with an ECL pipeline (Extract, Cognify, Load) combining embeddings, knowledge graphs, and cognitive science approaches.

## 3. Technology Stack
- **Language:** Python 3.10-3.14
- **Framework:** FastAPI, Pydantic, SQLAlchemy + Alembic
- **LLM:** litellm (unified interface), instructor (structured output)
- **Graph Databases:** Ladybug/Kuzu (default), Neo4j, AWS Neptune, PostgreSQL
- **Vector Databases:** LanceDB (default), ChromaDB, PGVector, Qdrant, Weaviate, Milvus
- **Relational DBs:** SQLite (default), PostgreSQL
- **Infrastructure:** Docker, Modal (serverless), Railway, Fly.io, Render
- **Cache:** Redis
- **Graph Algorithms:** NetworkX

## 4. Architecture
```
API Layer (cognee/api/v1/)
    ↓
Main Functions (add, cognify, recall/search, memify, remember)
    ↓
Pipeline Orchestrator (cognee/modules/pipelines/)
    ↓
Task Execution Layer (cognee/tasks/)
    ↓
Domain Modules (graph, retrieval, ingestion, etc.)
    ↓
Infrastructure Adapters (LLM, databases)
    ↓
External Services (OpenAI, Ladybug, LanceDB, etc.)
```

**Core API Endpoints:**
- `/add` — Data ingestion
- `/cognify` — Knowledge graph processing
- `/search` / `/recall` — Query interface with multiple search types
- `/memify` — Graph enrichment
- `/datasets` — Dataset management
- `/remember` / `/forget` / `/improve` — Memory operations
- `/visualize` — Graph visualization

**Search Types Available:**
- GRAPH_COMPLETION (default)
- GRAPH_SUMMARY_COMPLETION
- GRAPH_COMPLETION_COT (chain-of-thought)
- GRAPH_COMPLETION_CONTEXT_EXTENSION
- TRIPLET_COMPLETION
- RAG_COMPLETION
- CHUNKS / CHUNKS_LEXICAL
- SUMMARIES
- CYPHER (direct query)
- NATURAL_LANGUAGE
- TEMPORAL
- CODING_RULES
- FEELING_LUCKY (auto-selection)

**Key Patterns:**
1. **Pipeline-Based Processing** — Task-based pipelines composable sequentially or in parallel
2. **Interface-Based Database Adapters** — `GraphDBInterface` and `VectorDBInterface` abstract classes
3. **Multi-Tenant Access Control** — User → Dataset → Data hierarchy with permission filtering
4. **LLM Gateway** — Unified interface via litellm with Instructor for structured output

## 5. Important Files and Folders
- `/cognee/__init__.py` — Core exports (add, cognify, search, recall, memify, etc.)
- `/cognee/api/v1/add/add.py` — Data ingestion endpoint
- `/cognee/api/v1/cognify/cognify.py` — Knowledge graph construction
- `/cognee/api/v1/recall/recall.py` — Query/retrieval
- `/cognee/api/v1/remember/remember.py` — Memory operations
- `/cognee/infrastructure/databases/graph/graph_db_interface.py` — Graph DB abstraction
- `/cognee/infrastructure/databases/vector/vector_db_interface.py` — Vector DB abstraction
- `/cognee/infrastructure/llm/LLMGateway.py` — LLM interface
- `/cognee/shared/data_models.py` — KnowledgeGraph, Node, Edge models
- `/cognee/modules/pipelines/` — Pipeline orchestration
- `/cognee/modules/retrieval/` — Multiple retriever implementations
- `/cognee-mcp/Dockerfile` — MCP server container
- `/Dockerfile` — Main application container

## 6. Licence and Commercial Risk
**Apache License 2.0** — Copyright 2024 Topoteretes UG

- **Allowed:** Commercial use, modification, distribution with attribution
- **Risk Level:** None — safe for MVP, production, and commercial use
- No copyleft restrictions

## 7. What OmniVia Can Learn From It
- **ECL pipeline pattern** — Extract, Cognify, Load workflow
- **Interface-based database adapters** — Abstract backends for flexibility
- **Multi-tenant access control** — User/Dataset/Data hierarchy with permissions
- **Pipeline orchestration** — Task-based pipelines with sequential/parallel execution
- **LLM Gateway pattern** — Unified LLM interface with litellm
- **12 search strategies** — Comprehensive query type coverage
- **Dataset management** — Organized data with metadata
- **Structured output with Instructor** — Pydantic models from LLM

## 8. What OmniVia Should Not Reuse
- LanceDB as default vector store—use Qdrant (better for our scale)
- Ladybug/Kuzu as default graph—use FalkorDB or Neo4j (more mature)
- Heavy Modal integration—focus on Docker-based deployment
- Their specific cognitive prompt templates—create our own

## 9. Recommended Integration
reference only

## 10. Recommended Placement in OmniVia
external/reference/

## 11. Required Spec Kit Updates
- `specs/pipeline-architecture.md` — Add ECL pipeline pattern section
- `specs/database-abstraction.md` — Document interface-based adapter pattern
- `specs/multi-tenancy.md` — Add permission-based access control design
- `specs/query-strategies.md` — Document 12 search type options
- `specs/llm-integration.md` — Design LLM Gateway pattern

## 12. Implementation Tasks to Add
- Design ECL pipeline (Extract, Cognify, Load) for knowledge processing
- Implement `GraphDBInterface` and `VectorDBInterface` abstract classes
- Create multi-tenant access control system
- Build pipeline orchestration with task execution layer
- Design LLM Gateway with litellm integration
- Implement multiple search strategies

## 13. Final Recommendation
reference only

**Rationale:** Cognee is a direct competitor to OmniVia with a mature ECL pipeline architecture. While its patterns are excellent references, building on it would mean adopting its opinions on data models, APIs, and processing flow. OmniVia should implement its own system with different design goals while using these patterns as architecture references.