"""Ingestion pipeline orchestration."""

from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import Any

from omnivia_memory.ingestion.chunker import BaseChunker, ParagraphChunker
from omnivia_memory.ingestion.extractors import BaseExtractor, MarkdownExtractor
from omnivia_memory.ingestion.models import Chunk, FileType, ParseStatus, Source
from omnivia_memory.ingestion.scanner import FileScanner, ScanOptions


@dataclasses.dataclass
class IngestResult:
    """Result of an ingestion operation."""

    source: Source | None = None
    chunks: list[Chunk] = dataclasses.field(default_factory=list)
    error: str | None = None


class IngestionPipeline:
    """Orchestrates the full ingestion pipeline: scan -> extract -> chunk -> persist."""

    def __init__(
        self,
        scanner: FileScanner | None = None,
        extractors: dict[FileType, BaseExtractor] | None = None,
        chunker: BaseChunker | None = None,
        source_repository: Any = None,
        chunk_repository: Any = None,
    ) -> None:
        self.scanner = scanner or FileScanner()
        self.extractors = extractors or {FileType.MARKDOWN: MarkdownExtractor()}
        self.chunker = chunker or ParagraphChunker()
        self.source_repository = source_repository
        self.chunk_repository = chunk_repository

    def ingest_file(self, file_path: Path) -> IngestResult:
        """Ingest a single file through the pipeline.

        The source record is persisted if source_repository is configured.
        Chunks are linked to the persisted source ID for provenance tracking.

        If the file was already ingested (same path), the existing source is returned
        without re-processing to avoid duplicate records.
        """
        try:
            file_type = self._get_file_type(file_path)
            if file_type == FileType.UNKNOWN:
                return IngestResult(error=f"Unsupported file type: {file_path.suffix}")

            extractor = self.extractors.get(file_type)
            if not extractor:
                return IngestResult(error=f"No extractor for {file_type.value}")

            result = extractor.extract(file_path)
            if result.status != ParseStatus.SUCCESS:
                return IngestResult(error=result.error)

            # Check if source already exists (by path) to avoid duplicates
            source = None
            if self.source_repository:
                existing = self.source_repository.get_by_path(str(file_path))
                if existing is not None:
                    # Source already ingested - return existing source with empty chunks
                    # to indicate no new work was done
                    return IngestResult(source=existing, chunks=[])

            # Create new source record
            source = Source(
                path=str(file_path),
                file_type=file_type,
                size=file_path.stat().st_size,
                hash=result.hash,
                status=ParseStatus.SUCCESS,
            )

            # Persist source if repository is configured
            if self.source_repository:
                try:
                    self.source_repository.create(source)
                except ValueError:
                    # Source with same ID already exists (race condition) - fetch and return
                    existing = self.source_repository.get_by_id(source.id)
                    if existing:
                        source = existing

            # Link chunks to the persisted source for provenance
            chunks = self.chunker.chunk("" if result.content is None else result.content, source.id)

            if self.chunk_repository:
                for chunk in chunks:
                    self.chunk_repository.create(chunk)

            return IngestResult(source=source, chunks=chunks)

        except Exception as e:
            return IngestResult(error=str(e))

    def ingest_directory(self, root_path: Path) -> list[IngestResult]:
        """Ingest all supported files in a directory."""
        options = ScanOptions(root_path=root_path)
        files = self.scanner.scan(options)
        results = []
        for file_info in files:
            result = self.ingest_file(file_info.path)
            results.append(result)
        return results

    def _get_file_type(self, path: Path) -> FileType:
        ext = path.suffix.lower()
        type_map = {
            ".md": FileType.MARKDOWN,
            ".markdown": FileType.MARKDOWN,
            ".pdf": FileType.PDF,
            ".docx": FileType.DOCX,
        }
        return type_map.get(ext, FileType.UNKNOWN)
