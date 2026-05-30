# ADR-001: Qdrant as MVP Vector Database

Status: Accepted
Date: 2026-05-30
Source: Open Source Repository Review

## Context

OmniVia needs a local vector database for semantic search over chunks and memories. After reviewing seven open source repositories, Qdrant emerged as the recommended vector database choice.

## Decision

**Adopt Qdrant for MVP as the local vector database through Docker.**

## Rationale

1. **Production-grade:** Qdrant is actively maintained with production deployments worldwide
2. **Apache 2.0 license:** Permissive open source license suitable for commercial products
3. **Local-first support:** Designed for self-hosted deployments
4. **Python client:** Official `qdrant-client` package for easy integration
5. **Docker-native:** Single container deployment with health checks
6. **Feature-rich:** Supports filtering, hybrid search, quantization, and multi-tenancy
7. **Performance:** Built in Rust for high throughput and low latency

## Alternatives Considered

- **LanceDB:** Not adopted—used as default in Cognee but Qdrant has better production maturity
- **ChromaDB:** Not adopted—less production-hardened than Qdrant
- **PGVector:** Not adopted—requires PostgreSQL which adds complexity
- **Weaviate/Milvus:** Not adopted—over-engineered for MVP use case

## Rejected Alternative

- **Kuzu:** REJECTED—Project is archived (v0.11.x is final release). Using an archived project introduces long-term maintenance and security risks.

## Placement

```yaml
# infra/docker/docker-compose.local.yml
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_storage:/qdrant/storage
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Dependencies

- Python client: `qdrant-client>=1.7.0`

## Consequences

**Positive:**
- Fast vector search without API costs
- Local deployment with no cloud dependency
- Proven production reliability

**Negative:**
- Additional Docker container to manage
- Need to handle Qdrant upgrade path
- One more service to monitor

## Review Date

Re-evaluate after MVP completion or if project status changes.