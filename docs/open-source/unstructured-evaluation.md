# Repo Evaluation: unstructured

## 1. Executive Summary
- Unstructured provides production-grade document preprocessing for LLM pipelines—excellent reference for OmniVia's document ingestion layer
- Apache 2.0 license with permissive commercial use—safe for MVP and production
- Supports 30+ file formats including PDFs, DOCX, PPTX, HTML, images with OCR, and more
- Modular extras system (pdf, docx, image, etc.) with lazy loading—best-in-class dependency management
- Element model hierarchy with rich metadata—OmniVia should adopt this pattern
- Multiple chunking strategies (basic, by_title, token-based) with configurable overlap and header repetition

## 2. What It Does
Unstructured is an open-source library for ingesting and preprocessing images and text documents (PDFs, HTML, Word docs, and many more) into structured outputs for LLMs. It transforms unstructured data into clean, typed Element objects with rich metadata.

## 3. Technology Stack
- **Language:** Python (>=3.11, <3.14)
- **Build System:** Hatchling
- **Package Manager:** uv with locked dependencies (uv.lock)
- **Key Dependencies:**
  - HTML: beautifulsoup4, lxml, html5lib
  - PDF: pypdf, pdfminer.six, pikepdf
  - Office: python-docx, python-pptx
  - NLP: spacy
  - OCR: opencv, tesseract
  - ML: torch, transformers
- **Infrastructure:** Docker (Chainguard wolfi-base minimal image)
- **Testing:** pytest with 90% coverage threshold

## 4. Architecture
**Directory Structure:**
```
unstructured/
├── partition/          # Core partitioning functions (file → elements)
│   ├── auto.py        # Automatic file-type detection router
│   ├── pdf.py         # PDF partitioning (largest file)
│   ├── docx.py        # DOCX partitioning
│   ├── email.py       # Email partitioning
│   ├── html/          # HTML parsing submodule
│   ├── pdf_image/     # PDF/image processing
│   └── common/       # Shared utilities
├── documents/          # Data models
│   ├── elements.py   # Element, Text, Table classes
│   ├── coordinates.py # Coordinate handling
│   └── ontology.py    # Element type definitions
├── chunking/           # Text chunking strategies
│   ├── base.py       # Main chunking logic
│   ├── basic.py       # Basic chunking
│   ├── dispatch.py    # Strategy dispatcher
│   └── title.py       # Title-based chunking
├── embed/              # Embedding integrations
│   ├── openai.py      # OpenAI embeddings
│   ├── huggingface.py # HuggingFace embeddings
│   ├── voyageai.py   # VoyageAI embeddings
│   └── bedrock.py    # AWS Bedrock embeddings
├── cleaners/           # Text cleaning utilities
├── staging/           # Serialization/deserialization
└── file_utils/        # File type detection
```

**Key Patterns:**
1. **Lazy Partitioner Loading:** `_PartitionerLoader` lazily loads partitioners with helpful dependency error messages
2. **Element Model Hierarchy:** Base `Element` abstract class with Text, Title, NarrativeText, Table, etc. subclasses
3. **Dynamic Metadata:** `ElementMetadata` declares known fields but implements dynamically for ad-hoc fields
4. **Consolidation Strategies:** Metadata field consolidation during chunking (FIRST, DROP, LIST_CONCATENATE)

## 5. Important Files and Folders
- `/partition/auto.py` — Automatic file-type detection router
- `/partition/pdf.py` (58KB) — PDF partitioning logic
- `/documents/elements.py` (41KB) — Element model hierarchy
- `/chunking/base.py` (82KB) — Main chunking logic (largest file)
- `/partition/pdf_image/` — PDF/image processing submodule
- `/embed/` — Embedding integration modules
- `/Dockerfile` — Chainguard-based container

## 6. Licence and Commercial Risk
**Apache License 2.0** — Permissive open-source license

- **Allowed:** Commercial use, modification, distribution with attribution
- **Risk Level:** None — safe for MVP, production, and commercial use
- No copyleft restrictions

## 7. What OmniVia Can Learn From It
- **Lazy loading pattern** for optional dependencies with `_PartitionerLoader`
- **Element model hierarchy** — base Element with specialized subclasses
- **Dynamic metadata pattern** — `ElementMetadata` with flexible ad-hoc fields
- **Chunking strategies** — multiple strategies with configurable overlap, header repetition, table isolation
- **Consolidation strategies** — FIRST, DROP, LIST_CONCATENATE for metadata during chunking
- **Dependency decorator pattern** — `@dependency_exists` for optional features
- **Fully modular extras** — pdf, docx, image, etc. installed separately
- **Security hardening** — custom OpenCV builds from source

## 8. What OmniVia Should Not Reuse
- Don't implement all these formats from scratch—leverage existing best-in-class libraries
- Don't use their chunking strategies verbatim—adapt to our needs
- Don't adopt their embedding module approach—use our own embedding service
- Don't copy the dynamic metadata pattern exactly—consider simpler alternatives

## 9. Recommended Integration
reference only

## 10. Recommended Placement in OmniVia
external/reference/

## 11. Required Spec Kit Updates
- `specs/document-ingestion.md` — Add Element model hierarchy pattern
- `specs/chunking-strategy.md` — Document chunking strategies with consolidation
- `specs/metadata-model.md` — Design dynamic metadata approach
- `docs/architecture/dependency-management.md` — Document lazy loading patterns

## 12. Implementation Tasks to Add
- Design Element model hierarchy for document chunks
- Implement lazy dependency loading system
- Define chunking strategy options (size, overlap, header repetition)
- Create consolidation strategy enum (FIRST, DROP, LIST_CONCATENATE)
- Build dynamic metadata handling

## 13. Final Recommendation
reference only

**Rationale:** Unstructured is a production-grade library, but it's a full-featured document preprocessing system that overlaps with multiple OmniVia components. Its patterns are excellent references for architecture, but OmniVia should implement its own document processing layer with different design goals rather than building on this library.