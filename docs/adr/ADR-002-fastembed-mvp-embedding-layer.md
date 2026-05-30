# ADR-002: FastEmbed as MVP Local Embedding Layer

Status: Accepted
Date: 2026-05-30
Source: Open Source Repository Review

## Context

OmniVia needs local embedding generation to avoid API costs and ensure data privacy. After reviewing open source options, FastEmbed emerged as the recommended choice.

## Decision

**Adopt FastEmbed for MVP as the local embedding package.**

## Rationale

1. **Zero API costs:** Local ONNX-based inference, no external API calls
2. **Privacy-first:** All embeddings generated locally, data never leaves the machine
3. **nomic-embed-text-v1.5 model:** High-quality embeddings optimized for code and documentation
4. **Apache 2.0 license:** Permissive open source license
5. **Qdrant ecosystem:** Developed and maintained by Qdrant team, seamless integration
6. **ONNX runtime:** Cross-platform, optimized inference
7. **Lightweight:** ~100MB model, reasonable for local deployment

## Alternatives Considered

- **OpenAI embeddings:** REJECTED—Requires API key, incurs costs, data leaves local machine
- **Sentence transformers:** Not adopted—larger models, slower inference
- **HuggingFace embeddings:** Not adopted—more complex setup, less optimized

## Reference Analysis

- **EngramMemory:** Uses FastEmbed with nomic-embed-text-v1.5 for local embeddings
- **Graphiti:** Supports multiple embedding providers; FastEmbed pattern validated
- **GraphRAG:** Uses Azure/OpenAI embeddings; not local-first

## Placement

```python
# services/embedding-service/requirements.txt
fastembed>=0.7.0
```

## Integration Pattern

```python
from fastembed import TextEmbedding

# Initialize model
model = TextEmbedding("nomic-ai/nomic-embed-text-v1.5")

# Generate embeddings
embeddings = list(model.embed(query_texts))
```

## Consequences

**Positive:**
- No API costs for embedding generation
- Full data privacy for embedding operations
- Fast inference with ONNX optimization
- Simple API for embedding generation

**Negative:**
- Model downloads on first run (~100MB)
- CPU-bound embedding may be slower than GPU
- Need to manage model version updates

## Review Date

Re-evaluate after MVP completion or if embedding requirements change.