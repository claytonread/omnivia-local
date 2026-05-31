"""Ingestion module for OmniVia.

Provides file scanning, content extraction, chunking, and persistence
for project source ingestion.
"""

from omnivia_memory.ingestion.chunker import (
    BaseChunker,
    CharacterChunker,
    ChunkConfig,
    ParagraphChunker,
)
from omnivia_memory.ingestion.extractors import (
    BaseExtractor,
    DOCXExtractor,
    MarkdownExtractor,
    PDFExtractor,
)
from omnivia_memory.ingestion.models import (
    Chunk,
    ExtractionResult,
    FileType,
    ParseStatus,
    Source,
)
from omnivia_memory.ingestion.pipeline import IngestResult, IngestionPipeline
from omnivia_memory.ingestion.repositories import ChunkRepository
from omnivia_memory.ingestion.scanner import FileInfo, FileScanner, ScanOptions

__all__ = [
    "BaseChunker",
    "BaseExtractor",
    "CharacterChunker",
    "Chunk",
    "ChunkConfig",
    "ChunkRepository",
    "DOCXExtractor",
    "ExtractionResult",
    "FileInfo",
    "FileScanner",
    "FileType",
    "IngestResult",
    "IngestionPipeline",
    "MarkdownExtractor",
    "PDFExtractor",
    "ParagraphChunker",
    "ParseStatus",
    "ScanOptions",
    "Source",
]
