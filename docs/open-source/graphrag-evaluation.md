# Repo Evaluation: graphrag

## 1. Executive Summary
- GraphRAG from Microsoft provides enterprise-grade knowledge graph construction for LLM pipelines—strong reference for OmniVia's graph-based retrieval
- MIT license enables full commercial use—no restrictions
- Monorepo structure with 7 packages demonstrates best practices for Python library organization
- Four search strategies (local, global, drift, basic) cover diverse query patterns—OmniVia should implement similar flexibility
- Factory pattern extensively used for extensibility—OmniVia should adopt this pattern
- Async-first design with heavy asyncio usage for parallel LLM calls—important performance pattern
- Azure-centric cloud dependencies—may need abstraction for multi-cloud support

## 2. What It Does
GraphRAG is a data pipeline and transformation suite by Microsoft that extracts meaningful, structured data from unstructured text using LLMs. It builds knowledge graphs to enhance LLM reasoning over private data through graph-based retrieval-augmented generation.

## 3. Technology Stack
- **Language:** Python 3.11-3.13
- **Package Manager:** uv (Astral's Python package manager)
- **Build Tool:** Hatchling
- **Task Runner:** poethepoet (poe)
- **Key Dependencies:**
  - LLM: azure-identity, graphrag-llm (custom package)
  - Vector: graphrag-vectors (custom package)
  - Graph: networkx, graspologic-native
  - NLP: spacy, nltk, textblob, blis
  - Data: pandas, pyarrow
  - Storage: azure-storage-blob, azure-search-documents, azure-cosmos
  - Config: pydantic v2
- **Monorepo Packages:** graphrag, graphrag-llm, graphrag-storage, graphrag-cache, graphrag-chunking, graphrag-input, graphrag-vectors, graphrag-common

## 4. Architecture
**Monorepo Structure (`/packages/`):**
- `graphrag/` — Main CLI and orchestration
- `graphrag-llm/` — LLM abstraction layer
- `graphrag-storage/` — Storage backends (file, memory, Azure)
- `graphrag-cache/` — Caching implementation
- `graphrag-chunking/` — Text chunking
- `graphrag-input/` — Input parsing
- `graphrag-vectors/` — Vector storage
- `graphrag-common/` — Shared utilities

**Indexing Pipeline (`graphrag index`):**
1. `load_input_documents` — Load raw documents
2. `create_base_text_units` — Chunk documents
3. `create_final_documents` — Process documents
4. `extract_graph` — Extract entities/relationships via LLM
5. `finalize_graph` — Clean and finalize graph
6. `extract_covariates` — Extract claims/facts
7. `create_communities` — Cluster graph (Leiden algorithm)
8. `create_final_text_units` — Link text to entities
9. `create_community_reports` — Generate community summaries
10. `generate_text_embeddings` — Create vector embeddings

**Query Pipeline (`graphrag query`):**
- `local` — Entity-focused search (graph + vector)
- `global` — Community-based map-reduce search
- `drift` — Multi-hop search algorithm
- `basic` — Simple vector similarity

**Factory Pattern:** Storage, cache, logger, vector store, LLM, pipeline factories with custom implementation registration.

## 5. Important Files and Folders
- `/packages/graphrag/graphrag/index/workflows/factory.py` — Pipeline creation
- `/packages/graphrag/graphrag/query/factory.py` — Query engine creation
- `/packages/graphrag/graphrag/cli/main.py` — CLI entrypoint
- `/packages/graphrag/graphrag/config/models/graph_rag_config.py` — Configuration model
- `/packages/graphrag/graphrag/data_model/schemas.py` — Output schemas
- `/packages/graphrag/graphrag/index/workflows/extract_graph.py` — Entity extraction
- `/unified-search-app/Dockerfile` — Streamlit app container

## 6. Licence and Commercial Risk
**MIT License** — Permissive open-source license from Microsoft Corporation

- **Allowed:** Commercial use, modification, distribution with attribution
- **Risk Level:** None — safe for MVP, production, and commercial use
- No copyleft restrictions

## 7. What OmniVia Can Learn From It
- **Factory pattern for extensibility** — storage, cache, LLM, vector stores all pluggable
- **Workflow-based pipelines** — composable workflow functions with clear stages
- **Configuration-driven behavior** — Pydantic v2 models for all config
- **Callback system** — extensible callbacks for logging, progress, etc.
- **Community detection** — Leiden algorithm for graph clustering
- **Four search strategies** — local, global, drift, basic covering different query patterns
- **Async-first design** — heavy asyncio for parallel LLM calls
- **Data model schemas** — Parquet output with predefined column definitions

## 8. What OmniVia Should Not Reuse
- Azure-specific dependencies—build abstraction layer for multi-cloud
- Monorepo structure—may not fit OmniVia's architecture
- Custom internal packages (graphrag-llm, etc.)—leverage existing standards
- Heavy enterprise tooling (poetry, poethepoet)—use uv for consistency
- Streamlit for UI—OmniVia has its own web stack

## 9. Recommended Integration
reference only

## 10. Recommended Placement in OmniVia
external/reference/

## 11. Required Spec Kit Updates
- `specs/graph-indexing.md` — Add workflow pipeline pattern section
- `specs/query-strategies.md` — Document search strategy options
- `specs/configuration.md` — Add Pydantic v2 configuration patterns
- `docs/architecture/factory-pattern.md` — Create factory pattern design doc

## 12. Implementation Tasks to Add
- Design factory pattern for database/vector store abstraction
- Implement workflow-based indexing pipeline
- Create search strategy abstraction (local, global, drift, basic)
- Add community detection integration
- Design callback system for extensibility

## 13. Final Recommendation
reference only

**Rationale:** GraphRAG provides excellent patterns for knowledge graph construction and query strategies, but it's tightly coupled to Azure infrastructure. OmniVia should implement its own graph-based retrieval system using these patterns as design references, with proper abstraction for multiple backend providers.