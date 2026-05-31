"""Tests for the CLI module."""

import tempfile
from pathlib import Path

import pytest

from omnivia_memory.cli.commands import (
    build_parser,
    cmd_create,
    cmd_list,
    format_memory,
)
from omnivia_memory.lifecycle.models import LifecycleState
from omnivia_memory.lifecycle.rules import CreatedBy
from omnivia_memory.memory.models import Memory
from omnivia_memory.persistence.database import Database, DatabaseConfig
from omnivia_memory.persistence.repositories import MemoryRepository
from omnivia_memory.provenance.models import Source, SourceType


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        config = DatabaseConfig(db_path=db_path)
        db = Database(config)
        db.connect()
        yield db
        db.close()


@pytest.fixture
def repository(temp_db):
    """Create a repository for testing."""
    return MemoryRepository(temp_db)


@pytest.fixture
def sample_memory():
    """Create a sample memory for testing."""

    def _create_memory(
        content="Test memory content",
        source_type=SourceType.FILE,
        source_ref="test.py",
        created_by=CreatedBy.AGENT,
        state=LifecycleState.PROPOSED,
    ):
        memory = Memory(
            content=content,
            source=Source(type=source_type, reference=source_ref),
            created_by=created_by,
            lifecycle_state=state,
        )
        return memory

    return _create_memory


class TestBuildParser:
    """Tests for CLI argument parser."""

    def test_parser_no_args_returns_none_command(self):
        """Parser with no args returns namespace with command=None."""
        parser = build_parser()
        args = parser.parse_args([])
        assert args.command is None

    def test_parser_creates_subcommands(self):
        """Parser creates all expected subcommands."""
        parser = build_parser()

        # Check create command
        args = parser.parse_args(
            ["create", "--content", "test", "--source-type", "file", "--source-ref", "test.py"]
        )
        assert args.command == "create"
        assert args.func == cmd_create

        # Check list command
        args = parser.parse_args(["list"])
        assert args.command == "list"
        assert args.func == cmd_list

        # Check get command
        args = parser.parse_args(["get", "test-id"])
        assert args.command == "get"
        assert args.memory_id == "test-id"

        # Check search command
        args = parser.parse_args(["search", "test query"])
        assert args.command == "search"
        assert args.query == "test query"

        # Check approve command
        args = parser.parse_args(["approve", "test-id"])
        assert args.command == "approve"
        assert args.memory_id == "test-id"

        # Check reject command
        args = parser.parse_args(["reject", "test-id"])
        assert args.command == "reject"
        assert args.memory_id == "test-id"


class TestFormatMemory:
    """Tests for memory formatting."""

    def test_format_memory_contains_all_fields(self, sample_memory):
        """Formatted memory includes all key fields."""
        memory = sample_memory()
        formatted = format_memory(memory)

        assert memory.id in formatted
        assert memory.content in formatted
        assert memory.source.type.value in formatted
        assert memory.source.reference in formatted
        assert memory.lifecycle_state.value in formatted
        assert memory.memory_type in formatted
        assert memory.created_by.value in formatted

    def test_format_memory_handles_none_description(self, sample_memory):
        """Formatted memory handles None description."""
        memory = sample_memory()
        memory.source.description = None
        formatted = format_memory(memory)

        assert "N/A" in formatted


class TestCmdCreate:
    """Tests for create command."""

    def test_create_requires_source_type(self):
        """Create requires source type argument."""
        parser = build_parser()

        with pytest.raises(SystemExit):
            parser.parse_args(["create", "--content", "test"])

    def test_create_requires_source_ref(self):
        """Create requires source reference argument."""
        parser = build_parser()

        with pytest.raises(SystemExit):
            parser.parse_args(["create", "--content", "test", "--source-type", "file"])

    def test_create_validates_source_type(self):
        """Create validates source type."""
        parser = build_parser()

        with pytest.raises(SystemExit):
            parser.parse_args(
                [
                    "create",
                    "--content",
                    "test",
                    "--source-type",
                    "invalid",
                    "--source-ref",
                    "test.py",
                ]
            )


class TestCmdList:
    """Tests for list command."""

    def test_list_validates_state(self):
        """List validates lifecycle state."""
        parser = build_parser()

        with pytest.raises(SystemExit):
            parser.parse_args(["list", "--state", "invalid"])


class TestCmdGet:
    """Tests for get command."""

    def test_get_requires_memory_id(self):
        """Get requires memory ID argument."""
        parser = build_parser()

        with pytest.raises(SystemExit):
            parser.parse_args(["get"])


class TestCmdUpdate:
    """Tests for update command."""

    def test_update_requires_memory_id(self):
        """Update requires memory ID argument."""
        parser = build_parser()

        with pytest.raises(SystemExit):
            parser.parse_args(["update"])


class TestCmdDelete:
    """Tests for delete command."""

    def test_delete_requires_memory_id(self):
        """Delete requires memory ID argument."""
        parser = build_parser()

        with pytest.raises(SystemExit):
            parser.parse_args(["delete"])


class TestCmdSearch:
    """Tests for search command."""

    def test_search_requires_query(self):
        """Search requires query argument."""
        parser = build_parser()

        with pytest.raises(SystemExit):
            parser.parse_args(["search"])


class TestCmdApprove:
    """Tests for approve command."""

    def test_approve_requires_memory_id(self):
        """Approve requires memory ID argument."""
        parser = build_parser()

        with pytest.raises(SystemExit):
            parser.parse_args(["approve"])


class TestCmdReject:
    """Tests for reject command."""

    def test_reject_requires_memory_id(self):
        """Reject requires memory ID argument."""
        parser = build_parser()

        with pytest.raises(SystemExit):
            parser.parse_args(["reject"])
