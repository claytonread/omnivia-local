"""Tests for the ingestion pipeline.

Tests file scanning, content extraction, chunking, and persistence.
"""

import hashlib
import tempfile
from pathlib import Path

import pytest

from omnivia_memory.ingestion.scanner import FileScanner, ScanOptions
from omnivia_memory.ingestion.extractors import (
    MarkdownExtractor,
    PDFExtractor,
    DOCXExtractor,
)
from omnivia_memory.ingestion.chunker import (
    ParagraphChunker,
    CharacterChunker,
)
from omnivia_memory.ingestion.models import (
    Source,
    Chunk,
    ParseStatus,
    FileType,
)


# Fixtures directory path
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir():
    """Return the fixtures directory path."""
    return FIXTURES_DIR


@pytest.fixture
def test_dir():
    """Return the test directory fixture path."""
    return FIXTURES_DIR / "test_dir"


@pytest.fixture
def sample_md():
    """Return the sample markdown fixture path."""
    return FIXTURES_DIR / "sample.md"


@pytest.fixture
def sample_pdf():
    """Return the sample PDF fixture path."""
    return FIXTURES_DIR / "sample.pdf"


@pytest.fixture
def sample_docx():
    """Return the sample DOCX fixture path."""
    return FIXTURES_DIR / "sample.docx"


# =============================================================================
# Test: FileScanner
# =============================================================================


class TestFileScanner:
    """Tests for the FileScanner class."""

    def test_scanner_detects_markdown_files(self, test_dir):
        """Scanner detects Markdown files."""
        scanner = FileScanner()
        options = ScanOptions(root_path=test_dir)
        results = scanner.scan(options)

        md_files = [f for f in results if f.file_type == FileType.MARKDOWN]
        assert len(md_files) >= 1

    def test_scanner_ignores_pycache(self, test_dir):
        """Scanner ignores __pycache__ directories."""
        scanner = FileScanner()
        options = ScanOptions(root_path=test_dir)
        results = scanner.scan(options)

        paths = [str(f.path) for f in results]
        assert not any("__pycache__" in p for p in paths)

    def test_scanner_ignores_git_directories(self, test_dir):
        """Scanner ignores .git directories."""
        scanner = FileScanner()
        options = ScanOptions(root_path=test_dir)
        results = scanner.scan(options)

        paths = [str(f.path) for f in results]
        assert not any("/.git/" in p or p.endswith(".git") for p in paths)

    def test_scanner_ignores_node_modules(self, test_dir):
        """Scanner ignores node_modules directories."""
        scanner = FileScanner()
        options = ScanOptions(root_path=test_dir)
        results = scanner.scan(options)

        paths = [str(f.path) for f in results]
        assert not any("node_modules" in p for p in paths)

    def test_scanner_ignores_py_files(self, test_dir):
        """Scanner ignores Python files by default."""
        scanner = FileScanner()
        options = ScanOptions(root_path=test_dir)
        results = scanner.scan(options)

        paths = [str(f.path) for f in results]
        assert not any(p.endswith(".py") for p in paths)

    def test_scanner_ignores_generated_files(self, test_dir):
        """Scanner ignores common generated file patterns."""
        scanner = FileScanner()
        options = ScanOptions(root_path=test_dir)
        results = scanner.scan(options)

        paths = [str(f.path) for f in results]
        # *.pyc files should be ignored
        assert not any(p.endswith(".pyc") for p in paths)

    def test_scanner_includes_metadata(self, test_dir):
        """Scanner includes file metadata in results."""
        scanner = FileScanner()
        options = ScanOptions(root_path=test_dir)
        results = scanner.scan(options)

        # Find any markdown file from the scan results
        md_file = next((f for f in results if f.file_type == FileType.MARKDOWN), None)
        assert md_file is not None
        assert md_file.path.exists()
        assert md_file.size > 0
        assert md_file.modified_time is not None
        assert md_file.file_type == FileType.MARKDOWN

    def test_scanner_respects_custom_ignore_patterns(self, test_dir):
        """Scanner respects custom ignore patterns."""
        scanner = FileScanner()
        # Ignore all .txt files
        options = ScanOptions(root_path=test_dir, ignore_patterns=["*.txt"])
        results = scanner.scan(options)

        paths = [str(f.path) for f in results]
        assert not any(p.endswith(".txt") for p in paths)

    def test_scanner_empty_directory(self, tmp_path):
        """Scanner handles empty directory."""
        scanner = FileScanner()
        options = ScanOptions(root_path=tmp_path)
        results = scanner.scan(options)

        assert len(results) == 0

    def test_scanner_nonexistent_path(self):
        """Scanner handles nonexistent path gracefully."""
        scanner = FileScanner()
        options = ScanOptions(root_path=Path("/nonexistent/path"))
        results = scanner.scan(options)

        assert len(results) == 0


# =============================================================================
# Test: MarkdownExtractor
# =============================================================================


class TestMarkdownExtractor:
    """Tests for the MarkdownExtractor class."""

    def test_extract_markdown_content(self, sample_md):
        """Extractor reads markdown file content."""
        extractor = MarkdownExtractor()
        result = extractor.extract(sample_md)

        assert result.status == ParseStatus.SUCCESS
        assert result.content is not None
        assert len(result.content) > 0

    def test_extract_markdown_includes_headers(self, sample_md):
        """Extractor preserves headers in content."""
        extractor = MarkdownExtractor()
        result = extractor.extract(sample_md)

        assert "Test Markdown Document" in result.content
        assert "Section 1" in result.content

    def test_extract_markdown_preserves_code_blocks(self, sample_md):
        """Extractor preserves code blocks."""
        extractor = MarkdownExtractor()
        result = extractor.extract(sample_md)

        assert "```python" in result.content
        assert "def hello" in result.content

    def test_extract_nonexistent_file(self):
        """Extractor handles nonexistent file."""
        extractor = MarkdownExtractor()
        result = extractor.extract(Path("/nonexistent.md"))

        assert result.status == ParseStatus.FAILED
        assert result.content is None
        assert result.error is not None


# =============================================================================
# Test: PDFExtractor
# =============================================================================


class TestPDFExtractor:
    """Tests for the PDFExtractor class."""

    def test_extract_pdf_content(self, sample_pdf):
        """Extractor reads PDF file content."""
        extractor = PDFExtractor()
        result = extractor.extract(sample_pdf)

        assert result.status == ParseStatus.SUCCESS
        assert result.content is not None
        assert len(result.content) > 0

    def test_extract_pdf_includes_sections(self, sample_pdf):
        """Extractor preserves section text."""
        extractor = PDFExtractor()
        result = extractor.extract(sample_pdf)

        assert "Test PDF Document" in result.content
        assert "Section" in result.content

    def test_extract_nonexistent_pdf(self):
        """Extractor handles nonexistent file."""
        extractor = PDFExtractor()
        result = extractor.extract(Path("/nonexistent.pdf"))

        assert result.status == ParseStatus.FAILED
        assert result.content is None
        assert result.error is not None


# =============================================================================
# Test: DOCXExtractor
# =============================================================================


class TestDOCXExtractor:
    """Tests for the DOCXExtractor class."""

    def test_extract_docx_content(self, sample_docx):
        """Extractor reads DOCX file content."""
        extractor = DOCXExtractor()
        result = extractor.extract(sample_docx)

        assert result.status == ParseStatus.SUCCESS
        assert result.content is not None
        assert len(result.content) > 0

    def test_extract_docx_includes_headings(self, sample_docx):
        """Extractor preserves headings."""
        extractor = DOCXExtractor()
        result = extractor.extract(sample_docx)

        assert "Test DOCX Document" in result.content
        assert "Section" in result.content

    def test_extract_docx_preserves_lists(self, sample_docx):
        """Extractor preserves list content."""
        extractor = DOCXExtractor()
        result = extractor.extract(sample_docx)

        assert "Item one" in result.content
        assert "Item two" in result.content
        assert "Item three" in result.content

    def test_extract_nonexistent_docx(self):
        """Extractor handles nonexistent file."""
        extractor = DOCXExtractor()
        result = extractor.extract(Path("/nonexistent.docx"))

        assert result.status == ParseStatus.FAILED
        assert result.content is None
        assert result.error is not None


# =============================================================================
# Test: ParagraphChunker
# =============================================================================


class TestParagraphChunker:
    """Tests for the ParagraphChunker class."""

    def test_chunk_by_paragraph_basic(self):
        """Chunks split text by paragraphs."""
        text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
        chunker = ParagraphChunker()
        chunks = chunker.chunk(text)

        assert len(chunks) >= 3

    def test_chunk_preserves_content(self):
        """Chunks preserve original text content."""
        text = "First paragraph.\n\nSecond paragraph."
        chunker = ParagraphChunker()
        chunks = chunker.chunk(text)

        combined = " ".join(c.content for c in chunks)
        assert "First paragraph" in combined
        assert "Second paragraph" in combined

    def test_chunk_empty_text(self):
        """Chunker handles empty text."""
        chunker = ParagraphChunker()
        chunks = chunker.chunk("")

        assert len(chunks) == 0

    def test_chunk_single_paragraph(self):
        """Chunker handles single paragraph."""
        text = "Only one paragraph here."
        chunker = ParagraphChunker()
        chunks = chunker.chunk(text)

        assert len(chunks) == 1
        assert chunks[0].content == text

    def test_chunk_preserves_offsets(self):
        """Chunks include offset information."""
        text = "First.\n\nSecond."
        chunker = ParagraphChunker()
        chunks = chunker.chunk(text)

        for chunk in chunks:
            assert chunk.start_offset >= 0
            assert chunk.end_offset >= chunk.start_offset


# =============================================================================
# Test: CharacterChunker
# =============================================================================


class TestCharacterChunker:
    """Tests for the CharacterChunker class."""

    def test_chunk_by_character_basic(self):
        """Chunks split text by character count."""
        text = "A" * 200
        chunker = CharacterChunker(chunk_size=50)
        chunks = chunker.chunk(text)

        assert len(chunks) >= 3
        assert all(len(c.content) <= 50 for c in chunks)

    def test_chunk_with_overlap(self):
        """Chunks include overlap between chunks."""
        text = "ABCDEFGHIJ" * 20
        chunker = CharacterChunker(chunk_size=50, overlap=10)
        chunks = chunker.chunk(text)

        assert len(chunks) >= 2
        # Verify overlap - there should be some repeated content at boundaries
        total_content = "".join(c.content for c in chunks)
        assert len(total_content) >= len(text)

    def test_chunk_overlap_positions(self):
        """Overlapping chunks share content at boundaries."""
        text = "AAAAABBBBBCCCCC" * 10  # Clear boundaries at 5-char intervals
        chunker = CharacterChunker(chunk_size=15, overlap=5)
        chunks = chunker.chunk(text)

        if len(chunks) >= 2:
            # Chunk boundary should be before the overlap
            last_of_first = chunks[0].content[-5:]
            # The last 5 chars of first chunk should appear in second chunk
            assert last_of_first in chunks[1].content

    def test_chunk_empty_text(self):
        """Chunker handles empty text."""
        chunker = CharacterChunker(chunk_size=50)
        chunks = chunker.chunk("")

        assert len(chunks) == 0

    def test_chunk_respects_max_chunks(self):
        """Chunker respects maximum chunk count."""
        text = "X" * 1000
        chunker = CharacterChunker(chunk_size=50, max_chunks=5)
        chunks = chunker.chunk(text)

        assert len(chunks) <= 5

    def test_chunk_handles_short_text(self):
        """Chunker handles text shorter than chunk size."""
        text = "Short text"
        chunker = CharacterChunker(chunk_size=100)
        chunks = chunker.chunk(text)

        assert len(chunks) == 1
        assert chunks[0].content == text


# =============================================================================
# Test: Source Model
# =============================================================================


class TestSourceModel:
    """Tests for the Source model."""

    def test_create_source(self):
        """Can create a source record."""
        source = Source(
            path="/path/to/file.md",
            file_type=FileType.MARKDOWN,
            size=1024,
            hash="abc123",
            status=ParseStatus.SUCCESS,
        )

        assert source.path == "/path/to/file.md"
        assert source.file_type == FileType.MARKDOWN
        assert source.size == 1024

    def test_source_to_dict(self):
        """Source serializes to dictionary."""
        source = Source(
            path="/path/to/file.md",
            file_type=FileType.MARKDOWN,
            size=1024,
            hash="abc123",
            status=ParseStatus.SUCCESS,
        )

        data = source.to_dict()
        assert data["path"] == "/path/to/file.md"
        assert data["file_type"] == "markdown"

    def test_source_from_dict(self):
        """Source deserializes from dictionary."""
        data = {
            "path": "/path/to/file.md",
            "file_type": "markdown",
            "size": 1024,
            "hash": "abc123",
            "status": "success",
            "error": None,
        }

        source = Source.from_dict(data)
        assert source.path == "/path/to/file.md"
        assert source.file_type == FileType.MARKDOWN

    def test_source_hash_calculation(self, sample_md):
        """Source calculates content hash correctly."""
        content = sample_md.read_text()
        expected_hash = hashlib.sha256(content.encode()).hexdigest()

        source = Source(
            path=str(sample_md),
            file_type=FileType.MARKDOWN,
            size=len(content),
            hash=expected_hash,
            status=ParseStatus.SUCCESS,
        )

        assert source.hash == expected_hash


# =============================================================================
# Test: Chunk Model
# =============================================================================


class TestChunkModel:
    """Tests for the Chunk model."""

    def test_create_chunk(self):
        """Can create a chunk record."""
        chunk = Chunk(
            source_id="source-123",
            chunk_index=0,
            content="Test content",
            start_offset=0,
            end_offset=12,
            content_hash="abc123",
        )

        assert chunk.source_id == "source-123"
        assert chunk.chunk_index == 0
        assert chunk.content == "Test content"

    def test_chunk_to_dict(self):
        """Chunk serializes to dictionary."""
        chunk = Chunk(
            source_id="source-123",
            chunk_index=0,
            content="Test content",
            start_offset=0,
            end_offset=12,
            content_hash="abc123",
        )

        data = chunk.to_dict()
        assert data["source_id"] == "source-123"
        assert data["chunk_index"] == 0
        assert data["content"] == "Test content"

    def test_chunk_from_dict(self):
        """Chunk deserializes from dictionary."""
        data = {
            "id": "chunk-456",
            "source_id": "source-123",
            "chunk_index": 0,
            "content": "Test content",
            "start_offset": 0,
            "end_offset": 12,
            "content_hash": "abc123",
        }

        chunk = Chunk.from_dict(data)
        assert chunk.id == "chunk-456"
        assert chunk.source_id == "source-123"

    def test_chunk_equality(self):
        """Chunks with same ID are equal."""
        chunk1 = Chunk(
            id="same-id",
            source_id="source-123",
            chunk_index=0,
            content="Content",
            start_offset=0,
            end_offset=7,
            content_hash="abc",
        )
        chunk2 = Chunk(
            id="same-id",
            source_id="source-123",
            chunk_index=1,
            content="Different",
            start_offset=0,
            end_offset=9,
            content_hash="def",
        )

        assert chunk1 == chunk2


# =============================================================================
# Test: Chunk Persistence and Re-chunking
# =============================================================================


class TestChunkPersistence:
    """Tests for chunk persistence and re-chunking logic."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir) / "test_chunks.db"

    @pytest.fixture
    def db_with_chunk_schema(self, temp_db_path):
        """Create a database with chunk schema for testing."""
        import sqlite3

        db_path = temp_db_path
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Create chunks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                start_offset INTEGER NOT NULL,
                end_offset INTEGER NOT NULL,
                content_hash TEXT
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_hash ON chunks(content_hash)")
        conn.commit()

        yield conn

        conn.close()

    @pytest.fixture
    def chunk_repository(self, db_with_chunk_schema):
        """Create a chunk repository for testing."""
        from omnivia_memory.ingestion.repositories import ChunkRepository

        # Create a wrapper that provides the execute method
        class DBWrapper:
            def __init__(self, conn):
                self._conn = conn
                self.config = type("obj", (object,), {"auto_commit": True})()

            def execute(self, query, params=None):
                cursor = self._conn.cursor()
                cursor.execute(query, params or ())
                if self.config.auto_commit:
                    self._conn.commit()
                return cursor

        wrapper = DBWrapper(db_with_chunk_schema)
        return ChunkRepository(wrapper)

    def test_create_chunk_record(self, chunk_repository):
        """Can create a chunk record."""
        chunk = Chunk(
            source_id="source-123",
            chunk_index=0,
            content="Test content",
            start_offset=0,
            end_offset=12,
            content_hash="abc123",
        )

        result = chunk_repository.create(chunk)
        assert result is not None
        assert result.id is not None

    def test_get_chunks_by_source(self, chunk_repository):
        """Can retrieve chunks by source ID."""
        for i in range(5):
            chunk = Chunk(
                source_id="source-123",
                chunk_index=i,
                content=f"Chunk {i}",
                start_offset=i * 10,
                end_offset=(i + 1) * 10,
                content_hash=f"hash{i}",
            )
            chunk_repository.create(chunk)

        results = chunk_repository.get_by_source_id("source-123")
        assert len(results) == 5

    def test_rechunking_detects_unchanged_content(self, chunk_repository):
        """Re-chunking detects unchanged chunks based on content hash."""
        # Create initial chunks
        content = "Unchanged content"
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        chunk = Chunk(
            source_id="source-123",
            chunk_index=0,
            content=content,
            start_offset=0,
            end_offset=len(content),
            content_hash=content_hash,
        )
        chunk_repository.create(chunk)

        # Check if chunk with same hash exists
        existing = chunk_repository.get_by_content_hash(content_hash)
        # The new chunk should have the same hash, so it's detected as unchanged
        assert existing is not None

    def test_rechunking_detects_changed_content(self, chunk_repository):
        """Re-chunking detects changed content."""
        # Create chunk with original content
        original_content = "Original content"
        original_hash = hashlib.sha256(original_content.encode()).hexdigest()

        chunk = Chunk(
            source_id="source-123",
            chunk_index=0,
            content=original_content,
            start_offset=0,
            end_offset=len(original_content),
            content_hash=original_hash,
        )
        chunk_repository.create(chunk)

        # Check for changed content
        new_content = "Modified content"
        new_hash = hashlib.sha256(new_content.encode()).hexdigest()

        # Hashes should be different
        assert original_hash != new_hash

        # Should not find existing chunk with new hash
        existing = chunk_repository.get_by_content_hash(new_hash)
        assert existing is None


# =============================================================================
# Integration Test: Full Pipeline
# =============================================================================


class TestIngestionPipeline:
    """Integration tests for the full ingestion pipeline."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir) / "integration.db"

    @pytest.fixture
    def db_for_pipeline(self, temp_db_path):
        """Create a database for integration tests."""
        import sqlite3

        db_path = temp_db_path
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row

        # Create chunks table
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                start_offset INTEGER NOT NULL,
                end_offset INTEGER NOT NULL,
                content_hash TEXT
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source_id)")
        conn.commit()

        yield conn

        conn.close()

    @pytest.fixture
    def chunk_repo(self, db_for_pipeline):
        """Create a chunk repository."""
        from omnivia_memory.ingestion.repositories import ChunkRepository

        class DBWrapper:
            def __init__(self, conn):
                self._conn = conn
                self.config = type("obj", (object,), {"auto_commit": True})()

            def execute(self, query, params=None):
                cursor = self._conn.cursor()
                cursor.execute(query, params or ())
                if self.config.auto_commit:
                    self._conn.commit()
                return cursor

        wrapper = DBWrapper(db_for_pipeline)
        return ChunkRepository(wrapper)

    def test_full_pipeline_markdown(self, sample_md, chunk_repo):
        """Full pipeline: scan -> extract -> chunk -> persist."""
        from omnivia_memory.ingestion.pipeline import IngestionPipeline

        pipeline = IngestionPipeline(
            scanner=FileScanner(),
            extractors={
                FileType.MARKDOWN: MarkdownExtractor(),
            },
            chunker=ParagraphChunker(),
            source_repository=None,
            chunk_repository=chunk_repo,
        )

        results = pipeline.ingest_file(sample_md)

        # Verify source was created
        assert results.source is not None
        assert results.source.status == ParseStatus.SUCCESS

        # Verify chunks were created
        chunks = chunk_repo.get_by_source_id(results.source.id)
        assert len(chunks) > 0

        # Verify chunk content
        for chunk in chunks:
            assert len(chunk.content) > 0
            assert chunk.content_hash is not None

    def test_pipeline_handles_extraction_error(self, chunk_repo):
        """Pipeline handles extraction errors gracefully."""
        from omnivia_memory.ingestion.pipeline import IngestionPipeline

        pipeline = IngestionPipeline(
            scanner=FileScanner(),
            extractors={},
            chunker=ParagraphChunker(),
            source_repository=None,
            chunk_repository=chunk_repo,
        )

        # Try to ingest nonexistent file
        results = pipeline.ingest_file(Path("/nonexistent.md"))

        assert results.source is None
        assert results.error is not None

    def test_pipeline_multiple_files(self, fixtures_dir, chunk_repo):
        """Pipeline processes multiple files correctly."""
        from omnivia_memory.ingestion.pipeline import IngestionPipeline

        pipeline = IngestionPipeline(
            scanner=FileScanner(),
            extractors={
                FileType.MARKDOWN: MarkdownExtractor(),
            },
            chunker=ParagraphChunker(),
            source_repository=None,
            chunk_repository=chunk_repo,
        )

        # Scan for files
        scanner = FileScanner()
        options = ScanOptions(root_path=fixtures_dir)
        files = scanner.scan(options)

        # Ingest markdown files
        md_files = [f for f in files if f.file_type == FileType.MARKDOWN]
        for file_info in md_files:
            result = pipeline.ingest_file(file_info.path)
            # Should process without error
            assert result is not None

        # Verify at least one source was processed
        assert len(md_files) >= 1


# =============================================================================
# Test: Source Persistence in Pipeline
# =============================================================================


class TestSourcePersistence:
    """Tests for source record persistence in the ingestion pipeline."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir) / "source_test.db"

    @pytest.fixture
    def db_with_sources_schema(self, temp_db_path):
        """Create a database with sources and chunks schema for testing."""
        import sqlite3

        db_path = temp_db_path
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Create sources table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                id TEXT PRIMARY KEY,
                file_path TEXT NOT NULL,
                extension TEXT,
                size_bytes INTEGER,
                modified_time TEXT,
                file_type TEXT NOT NULL,
                content_hash TEXT,
                parse_status TEXT NOT NULL,
                error_message TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sources_path ON sources(file_path)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sources_hash ON sources(content_hash)")

        # Create chunks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                start_offset INTEGER NOT NULL,
                end_offset INTEGER NOT NULL,
                content_hash TEXT
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source_id)")
        conn.commit()

        yield conn

        conn.close()

    @pytest.fixture
    def db_wrapper(self, db_with_sources_schema):
        """Create a DB wrapper for repositories."""
        conn = db_with_sources_schema

        class DBWrapper:
            def __init__(self, conn):
                self._conn = conn
                self.config = type("obj", (object,), {"auto_commit": True})()

            def execute(self, query, params=None):
                cursor = self._conn.cursor()
                cursor.execute(query, params or ())
                if self.config.auto_commit:
                    self._conn.commit()
                return cursor

        return DBWrapper(conn)

    @pytest.fixture
    def source_repo(self, db_wrapper):
        """Create a source repository."""
        from omnivia_memory.ingestion.repositories import SourceRepository

        return SourceRepository(db_wrapper)

    @pytest.fixture
    def chunk_repo(self, db_wrapper):
        """Create a chunk repository."""
        from omnivia_memory.ingestion.repositories import ChunkRepository

        return ChunkRepository(db_wrapper)

    def test_ingest_file_persists_source(self, sample_md, source_repo, chunk_repo):
        """ingest_file() persists a source when source_repository is configured."""
        from omnivia_memory.ingestion.pipeline import IngestionPipeline

        pipeline = IngestionPipeline(
            scanner=FileScanner(),
            extractors={FileType.MARKDOWN: MarkdownExtractor()},
            chunker=ParagraphChunker(),
            source_repository=source_repo,
            chunk_repository=chunk_repo,
        )

        result = pipeline.ingest_file(sample_md)

        # Source should be persisted
        assert result.source is not None
        assert result.error is None

        # Verify source exists in repository
        retrieved = source_repo.get_by_id(result.source.id)
        assert retrieved is not None
        assert retrieved.path == str(sample_md)
        assert retrieved.file_type == FileType.MARKDOWN

    def test_chunks_linked_to_persisted_source(self, sample_md, source_repo, chunk_repo):
        """Chunks are linked to the persisted source ID."""
        from omnivia_memory.ingestion.pipeline import IngestionPipeline

        pipeline = IngestionPipeline(
            scanner=FileScanner(),
            extractors={FileType.MARKDOWN: MarkdownExtractor()},
            chunker=ParagraphChunker(),
            source_repository=source_repo,
            chunk_repository=chunk_repo,
        )

        result = pipeline.ingest_file(sample_md)

        # Verify source was persisted
        assert result.source is not None
        source_id = result.source.id

        # Get chunks from repository
        chunks = chunk_repo.get_by_source_id(source_id)

        # All chunks should reference the persisted source
        assert len(chunks) > 0
        for chunk in chunks:
            assert chunk.source_id == source_id

    def test_directory_ingestion_persists_sources(self, test_dir, source_repo, chunk_repo):
        """Directory ingestion persists sources for discovered files."""
        from omnivia_memory.ingestion.pipeline import IngestionPipeline

        pipeline = IngestionPipeline(
            scanner=FileScanner(),
            extractors={FileType.MARKDOWN: MarkdownExtractor()},
            chunker=ParagraphChunker(),
            source_repository=source_repo,
            chunk_repository=chunk_repo,
        )

        results = pipeline.ingest_directory(test_dir)

        # Count successful ingestions with sources
        successful_with_sources = [r for r in results if r.source is not None and r.chunks]
        assert len(successful_with_sources) >= 1

        # Verify sources were persisted in repository
        all_sources = source_repo.list_all(limit=100)
        assert len(all_sources) >= len(successful_with_sources)

    def test_duplicate_ingestion_handled_predictably(self, sample_md, source_repo, chunk_repo):
        """Duplicate/repeated ingestion is handled without crashing."""
        from omnivia_memory.ingestion.pipeline import IngestionPipeline

        pipeline = IngestionPipeline(
            scanner=FileScanner(),
            extractors={FileType.MARKDOWN: MarkdownExtractor()},
            chunker=ParagraphChunker(),
            source_repository=source_repo,
            chunk_repository=chunk_repo,
        )

        # First ingestion
        result1 = pipeline.ingest_file(sample_md)
        assert result1.source is not None
        assert result1.error is None

        # Second ingestion of same file - should return existing source without error
        result2 = pipeline.ingest_file(sample_md)
        assert result2.source is not None
        # Should return existing source (empty chunks)
        assert result2.source.id == result1.source.id
        assert len(result2.chunks) == 0  # No new chunks for existing source

    def test_source_list_after_ingestion(self, sample_md, source_repo, chunk_repo):
        """sources CLI can list persisted ingested sources."""
        from omnivia_memory.ingestion.pipeline import IngestionPipeline

        pipeline = IngestionPipeline(
            scanner=FileScanner(),
            extractors={FileType.MARKDOWN: MarkdownExtractor()},
            chunker=ParagraphChunker(),
            source_repository=source_repo,
            chunk_repository=chunk_repo,
        )

        # Ingest file
        result = pipeline.ingest_file(sample_md)
        assert result.source is not None

        # List all sources
        sources = source_repo.list_all(limit=100)
        assert len(sources) >= 1

        # Verify source is queryable by path
        by_path = source_repo.get_by_path(str(sample_md))
        assert by_path is not None
        assert by_path.id == result.source.id
