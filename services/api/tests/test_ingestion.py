"""
Tests for the vault ingestion service.

Uses a temp directory to simulate workspace scanning without touching real files.
"""

import pytest
import tempfile
from pathlib import Path

from services.api.services.ingestion import (
    scan_workspace,
    _should_skip,
    _file_type_from_extension,
    SUPPORTED_EXTENSIONS,
)


class TestFileTypeMapping:
    """Test that file extensions map to correct types."""

    @pytest.mark.parametrize("ext,expected", [
        (".md", "markdown"),
        (".markdown", "markdown"),
        (".txt", "text"),
        (".py", "unsupported"),
        (".jpg", "unsupported"),
        (".PDF", "unsupported"),
        ("", "unsupported"),
    ])
    def test_file_type_from_extension(self, ext, expected):
        assert _file_type_from_extension(ext) == expected


class TestSkipPatterns:
    """Test that skip logic correctly identifies files to ignore."""

    def test_skips_hidden_by_default(self):
        """Files starting with dot are skipped unless explicitly allowed."""
        assert _should_skip(Path(".env"))
        assert _should_skip(Path(".DS_Store"))
        assert _should_skip(Path(".cache"))

    def test_skips_explicit_names(self):
        """Known directories like node_modules are skipped."""
        assert _should_skip(Path("node_modules"))
        assert _should_skip(Path(".venv"))
        assert _should_skip(Path("__pycache__"))
        assert _should_skip(Path(".git"))

    def test_keeps_allowed_exceptions(self):
        """Approved dotfiles are not skipped."""
        assert not _should_skip(Path(".env.example"))
        assert not _should_skip(Path(".gitignore"))

    def test_skips_compiled_artfacts(self):
        """Python bytecode and other compiled files are skipped."""
        assert _should_skip(Path("example.pyc"))
        assert _should_skip(Path("example.pyo"))

    def test_keeps_markdown_files(self):
        """Markdown and text files are not skipped."""
        assert not _should_skip(Path("README.md"))
        assert not _should_skip(Path("notes.txt"))
        assert not _should_skip(Path("article.markdown"))


class TestScanWorkspace:
    """Integration tests for full workspace scanning."""

    @pytest.fixture
    def temp_workspace(self):
        """Create a temp directory with sample files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create supported files
            Path(tmpdir, "README.md").write_text("# Hello")
            Path(tmpdir, "notes").mkdir()
            Path(tmpdir, "notes", "todo.txt").write_text("Buy groceries")
            Path(tmpdir, "notes", "journal.md").write_text("- wake up\n- coffee")

            # Create unsupported files
            Path(tmpdir, "image.png").write_bytes(b"\x89PNG")
            Path(tmpdir, "script.py").write_text("print('hello')")

            # Create skip candidates
            Path(tmpdir, ".DS_Store").write_text("ignored")
            Path(tmpdir, "node_modules").mkdir()
            Path(tmpdir, "node_modules", "package.json").write_text("{}")

            yield tmpdir

    def test_scans_workspace_and_returns_inventory(self, temp_workspace):
        """Scanning a workspace returns file metadata."""
        result = scan_workspace(temp_workspace)

        assert result.workspace_path == temp_workspace
        assert result.total_files > 0
        assert result.scan_duration_ms >= 0

        # Check that supported files are counted
        assert result.supported_files >= 3  # README.md, todo.txt, journal.md

        # Check that unsupported files are still reported
        assert result.unsupported_files >= 2  # image.png, script.py

    def test_includes_file_metadata(self, temp_workspace):
        """Inventory items contain correct metadata."""
        result = scan_workspace(temp_workspace)

        markdown_items = [i for i in result.items if i.file_type == "markdown"]
        assert len(markdown_items) > 0

        for item in markdown_items:
            assert item.path
            assert item.extension in SUPPORTED_EXTENSIONS
            assert item.size >= 0
            assert item.modified_ms > 0
            assert item.file_type == "markdown"
            assert item.parse_status == "supported"

    def test_skips_cache_and_hidden_directories(self, temp_workspace):
        """Cache directories like node_modules are not recursed into."""
        result = scan_workspace(temp_workspace)

        # node_modules should not appear in results
        paths = [item.path for item in result.items]
        assert not any("node_modules" in p for p in paths)
        assert not any(".DS_Store" in p for p in paths)

    def test_raises_on_nonexistent_path(self):
        """Scanning a non-existent path raises ValueError."""
        with pytest.raises(ValueError, match="Not a directory"):
            scan_workspace("/nonexistent/path/12345")

    def test_respects_max_files_limit(self, temp_workspace):
        """Scanning stops at max_files limit."""
        result = scan_workspace(temp_workspace, max_files=2)
        assert result.total_files <= 2

    def test_supported_extensions_constant(self):
        """SUPPORTED_EXTENSIONS contains expected values."""
        assert ".md" in SUPPORTED_EXTENSIONS
        assert ".markdown" in SUPPORTED_EXTENSIONS
        assert ".txt" in SUPPORTED_EXTENSIONS