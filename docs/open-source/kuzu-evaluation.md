# Repo Evaluation: kuzu

## 1. Executive Summary
- Kuzu is an embedded graph database with modern C++ implementation and excellent performance characteristics
- MIT License enables full commercial use—no restrictions
- **Project Status: ARCHIVED** — Not actively maintained; last release 0.11.x; OmniVia should not build new dependencies on this
- Cypher query language support with ANTLR4 parser—industry-standard query interface
- Extension framework for modularity—good architectural pattern
- Vector similarity search support—relevant for hybrid search use cases
- Multiple language bindings (Python, Node.js, Java, Rust, C)—broad compatibility

## 2. What It Does
Kuzu is an embedded property graph database optimized for complex analytical workloads on very large databases. It provides property graph data modeling with Cypher query language support, full-text search, vector indices, and ACID transactions.

## 3. Technology Stack
- **Language:** C++20 (primary), with Python (pybind11), Rust, C, Node.js, Java bindings
- **Build System:** CMake
- **Parser:** ANTLR4 for Cypher query language parsing
- **WebAssembly:** Supports browser-based execution via Emscripten
- **Compression:** zstd, brotli, snappy, lz4
- **Index:** simsimd for SIMD vector similarity search
- **Storage:** Columnar format with WAL-based recovery

## 4. Architecture
**Source Structure (`/src`):**

1. **`main/`** — Database and connection management
   - `database.cpp` — Core database class
   - `connection.cpp` — Connection interface for queries
   - `client_context.cpp` — Client context management

2. **`storage/`** — Storage layer
   - `buffer_manager/` — Memory management with page eviction (mmap)
   - `table/` — Node and relationship table storage
   - `wal/` — Write-Ahead Log for ACID transactions
   - `compression/` — Data compression
   - `index/` — Hash and vector index structures

3. **`processor/`** — Query execution engine
   - `operator/` — Physical operators (joins, scans, aggregations)
   - `map/` — Logical-to-physical plan mapping
   - Vectorized query processing

4. **`planner/`** — Query planning
   - `join_order/` — Join order enumeration with cardinality estimation
   - DP-based planning for graph pattern matching

5. **`binder/`** — Semantic analysis
   - Expression binding, DDL statement binding

6. **`parser/`** — Query parsing via ANTLR4

7. **`optimizer/`** — Query optimization

8. **`extension/`** — Extension framework
   - Dynamic extension loading
   - Official extensions: algo, fts, json, vector, duckdb, postgres, sqlite, httpfs, delta, iceberg, azure, neo4j, unity_catalog, llm

9. **`catalog/`** — Metadata management

10. **`transaction/`** — Transaction management
    - Serializable ACID transactions
    - Checkpointing and WAL replay

## 5. Important Files and Folders
- `/src/main/database.cpp` — Core database class
- `/src/main/connection.cpp` — Query connection interface
- `/src/storage/` — Storage layer with buffer management
- `/src/storage/wal/` — WAL for ACID transactions
- `/src/processor/` — Vectorized query processor
- `/src/extension/` — Extension framework
- `/src/c_api/` — Public C API for embedding
- `/scripts/extension/Dockerfile` — NGINX-based extension server
- `/CMakeLists.txt` — Build configuration

## 6. Licence and Commercial Risk
**MIT License** — Copyright 2022-2025 Kuzu Inc.

- **Allowed:** Commercial use, modification, distribution with attribution
- **Risk Level:** None for existing use; caution for new projects
- **Status Note:** Project is archived as of 0.11.x—may not receive security updates

## 7. What OmniVia Can Learn From It
- **Clean separation of logical layers** — parser, binder, planner, processor, storage
- **Vectorized query processing** — Performance optimization pattern
- **Extension framework** — Dynamic loading for modularity
- **Buffer management with mmap** — Page eviction strategy
- **WAL-based recovery** — ACID transaction implementation
- **Join planning with cardinality estimation** — Query optimization
- **Columnar storage with compression** — Storage efficiency

## 8. What OmniVia Should Not Reuse
- **Do not build new dependencies on Kuzu** — Project is archived
- Use FalkorDB or Neo4j instead for production graph database needs
- Don't copy C++ implementation patterns unless building in C++

## 9. Recommended Integration
reject

## 10. Recommended Placement in OmniVia
Not applicable (rejected)

## 11. Required Spec Kit Updates
- `specs/graph-database.md` — Remove Kuzu as option, add FalkorDB/Neo4j
- `specs/database-abstraction.md` — Document graph DB interface without Kuzu
- `docs/architecture/storage.md` — Update storage recommendations

## 12. Implementation Tasks to Add
- Select alternative graph database (FalkorDB or Neo4j) for production
- Update `GraphDriver` interface to exclude Kuzu
- Document extension framework pattern for future reference

## 13. Final Recommendation
reject for MVP

**Rationale:** While Kuzu is a well-engineered embedded graph database with excellent patterns, the project is archived and no longer actively maintained. Building new dependencies on an archived project introduces long-term maintenance and security risks. OmniVia should use FalkorDB (Redis-based, actively maintained) or Neo4j (mature, enterprise-supported) for graph database needs.