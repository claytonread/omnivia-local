"""Chunking strategies for content segmentation."""

from __future__ import annotations

import hashlib
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from omnivia_memory.ingestion.models import Chunk


class BaseChunker(ABC):
    """Abstract base class for chunking strategies."""

    @abstractmethod
    def chunk(self, content: str, source_id: str = "default") -> list[Chunk]:
        """Split content into chunks."""
        pass


@dataclass
class ChunkConfig:
    """Configuration for chunking behavior."""

    source_id: str
    chunk_size: int = 500
    overlap: int = 50
    max_chunks: Optional[int] = None


class ParagraphChunker(BaseChunker):
    """Splits content by paragraph boundaries."""

    def chunk(self, content: str, source_id: str = "default") -> list[Chunk]:
        """Split content by paragraphs."""
        if not content or not content.strip():
            return []

        paragraphs = re.split(r"\n\s*\n", content)
        chunks = []
        for idx, para in enumerate(paragraphs):
            para = para.strip()
            if not para:
                continue

            start = content.find(para)
            if start == -1:
                start = sum(len(p) + 2 for p in paragraphs[:idx])

            end = start + len(para)
            content_hash = hashlib.sha256(para.encode()).hexdigest()

            chunk = Chunk(
                source_id=source_id,
                chunk_index=idx,
                content=para,
                start_offset=start,
                end_offset=end,
                content_hash=content_hash,
            )
            chunks.append(chunk)

        return chunks


class CharacterChunker(BaseChunker):
    """Splits content by character count with overlap."""

    def __init__(self, chunk_size: int = 500, overlap: int = 50, max_chunks: Optional[int] = None):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.max_chunks = max_chunks

    def chunk(self, content: str, source_id: str = "default") -> list[Chunk]:
        """Split content by character count."""
        if not content:
            return []

        chunks = []
        position = 0
        idx = 0

        while position < len(content):
            if self.max_chunks is not None and idx >= self.max_chunks:
                break

            chunk_end = min(position + self.chunk_size, len(content))

            if chunk_end < len(content):
                last_space = content.rfind(" ", position, chunk_end)
                if last_space > position:
                    chunk_end = last_space + 1

            chunk_text = content[position:chunk_end]
            if not chunk_text.strip():
                break

            content_hash = hashlib.sha256(chunk_text.encode()).hexdigest()
            chunk = Chunk(
                source_id=source_id,
                chunk_index=idx,
                content=chunk_text,
                start_offset=position,
                end_offset=chunk_end,
                content_hash=content_hash,
            )
            chunks.append(chunk)

            position = chunk_end - self.overlap
            if position <= chunks[-1].start_offset:
                position = chunk_end
            idx += 1

        return chunks
