# Repo Evaluation: markitdown

## 1. Executive Summary
- MarkItDown is a lightweight document-to-Markdown converter with 24 built-in converters—excellent reference for building OmniVia's document ingestion pipeline
- MIT license enables full commercial use with no restrictions—safest option for MVP
- Supports 24 formats including PDF, DOCX, PPTX, XLSX, EPUB, HTML, YouTube, and more
- Plugin architecture via entry points enables third-party converter extensions—OmniVia should adopt this pattern
- MCP server package included—aligns with OmniVia's MCP integration goals
- Focuses on document-to-text extraction rather than high-fidelity rendering—right approach for LLM ingestion

## 2. What It Does
MarkItDown is a Python utility that converts various file formats to Markdown for use with LLMs and text analysis pipelines. It preserves document structure (headings, lists, tables, links) while extracting text content in a format optimized for AI consumption.

## 3. Technology Stack
- **Language:** Python 3.10+
- **Build System:** Hatchling (via `pyproject.toml`)
- **Key Dependencies:**
  - Core: beautifulsoup4, requests, markdownify, magika, charset-normalizer, defusedxml
  - Optional: python-pptx, mammoth (DOCX), pandas, openpyxl, pdfminer.six, pdfplumber
  - Cloud: azure-ai-documentintelligence, azure-ai-contentunderstanding, azure-identity
- **Package Manager:** uv compatible
- **Package Structure:** Monorepo with markitdown, markitdown-mcp, markitdown-ocr sub-packages

## 4. Architecture
**Monorepo Structure (`/packages`):**
- `markitdown/` — Core library
- `markitdown-mcp/` — MCP server integration
- `markitdown-ocr/` — OCR plugin using LLM vision
- `markitdown-sample-plugin/` — Example plugin template

**Core Architecture (`markitdown/src/markitdown/`):**

1. **`_markitdown.py`** — Main `MarkItDown` class as entry point
   - Manages converter registration and priority ordering
   - Handles multiple input sources: local files, URLs, HTTP responses, streams
   - Uses `Magika` for file type detection
   - Plugin loading via entry points

2. **`_base_converter.py`** — Abstract base classes
   - `DocumentConverter` with `accepts()` and `convert()` methods
   - `DocumentConverterResult` for conversion results

3. **`_stream_info.py`** — Immutable `StreamInfo` dataclass for file metadata

4. **`converters/`** — 24 converter implementations with consistent pattern:
   - Plain text, HTML, RSS, Wikipedia, YouTube, Bing SERP
   - PDF (table extraction), DOCX, XLSX/XLS, PPTX, EPUB
   - Images, Audio, Outlook MSG, ZIP, CSV
   - Azure Document Intelligence, Azure Content Understanding

**Plugin Architecture:** Third-party converters register via `markitdown.plugin` entry point.

## 5. Important Files and Folders
- `/packages/markitdown/src/markitdown/_markitdown.py` — Main class, converter registry
- `/packages/markitdown/src/markitdown/_base_converter.py` — Abstract converter base classes
- `/packages/markitdown/src/markitdown/_stream_info.py` — Stream metadata model
- `/packages/markitdown/src/markitdown/converters/` — 24 converter implementations
- `/packages/markitdown-mcp/` — MCP server package
- `/packages/markitdown-ocr/` — OCR plugin
- `/packages/markitdown-sample-plugin/` — Plugin example

## 6. Licence and Commercial Risk
**MIT License** — Permissive open-source license

- **Allowed:** Commercial use, modification, distribution with attribution
- **Risk Level:** None — safe for MVP, production, and commercial use
- No copyleft restrictions, no usage limitations

## 7. What OmniVia Can Learn From It
- **Plugin architecture via entry points** — converters register dynamically
- **Priority-based converter ordering** — more specific converters tried first
- **Lazy dependency loading** — optional dependencies imported with delayed error reporting
- **Stream position preservation** — `accepts()` must not advance file stream
- **Graceful fallback** — PDF falls back from pdfplumber to pdfminer
- **Immutable StreamInfo** pattern — frozen dataclass for metadata
- **Consistent converter pattern** — `ACCEPTED_MIME_TYPE_PREFIXES`, `ACCEPTED_FILE_EXTENSIONS`
- **Multi-source input handling** — files, URLs, HTTP responses, streams unified

## 8. What OmniVia Should Not Reuse
- Don't replicate the converter implementations—build our own with different focus
- Don't use Azure-specific cloud dependencies unless needed for enterprise features
- Don't implement YouTube/Bing converters unless explicitly required

## 9. Recommended Integration
reference only

## 10. Recommended Placement in OmniVia
external/reference/

## 11. Required Spec Kit Updates
- `specs/document-ingestion.md` — Add converter registration pattern section
- `specs/file-processing.md` — Document file type detection with Magika
- `docs/architecture/plugin-architecture.md` — Create plugin system design doc

## 12. Implementation Tasks to Add
- Design plugin architecture for document converters using entry point pattern
- Implement stream-based processing with position preservation
- Add graceful fallback chain for PDF processing (pdfplumber → pdfminer → pypdf)
- Create converter priority registry system
- Add file type detection integration

## 13. Final Recommendation
reference only

**Rationale:** MarkItDown's architecture patterns are excellent references for OmniVia's document ingestion pipeline, particularly the plugin system and converter registry. However, it doesn't provide a full memory/knowledge graph system—just document conversion. OmniVia should implement its own document processing pipeline inspired by these patterns rather than depending on this library.