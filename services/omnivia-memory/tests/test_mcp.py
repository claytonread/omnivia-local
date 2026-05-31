"""Tests for the MCP server module."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from omnivia_memory.lifecycle.models import LifecycleState
from omnivia_memory.lifecycle.rules import CreatedBy
from omnivia_memory.memory.models import Memory
from omnivia_memory.persistence.database import Database, DatabaseConfig
from omnivia_memory.persistence.repositories import MemoryRepository
from omnivia_memory.provenance.models import Source, SourceType


# Skip MCP tests if MCP is not available
pytest.importorskip("mcp")

from omnivia_memory.mcp.server import (
    TOOLS,
    TOOL_HANDLERS,
    format_error,
    format_success,
    memory_to_dict,
)


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


class TestTools:
    """Tests for MCP tool definitions."""

    def test_all_required_tools_defined(self):
        """All Phase 1 tools are defined."""
        tool_names = {tool.name for tool in TOOLS}

        expected_tools = {
            "memory_store",
            "memory_list",
            "memory_get",
            "memory_update",
            "memory_delete",
            "memory_search",
            "memory_approve",
            "memory_reject",
        }

        assert expected_tools.issubset(tool_names)

    def test_memory_store_has_required_fields(self):
        """memory_store tool has correct schema."""
        store_tool = next(t for t in TOOLS if t.name == "memory_store")
        schema = store_tool.inputSchema

        assert "content" in schema["properties"]
        assert "source_type" in schema["properties"]
        assert "source_reference" in schema["properties"]
        assert schema["required"] == ["content", "source_type", "source_reference"]

    def test_memory_store_source_type_enum(self):
        """memory_store validates source_type enum."""
        store_tool = next(t for t in TOOLS if t.name == "memory_store")
        schema = store_tool.inputSchema

        assert schema["properties"]["source_type"]["enum"] == ["file", "url", "adr", "human"]

    def test_memory_list_optional_params(self):
        """memory_list has optional parameters."""
        list_tool = next(t for t in TOOLS if t.name == "memory_list")
        schema = list_tool.inputSchema

        assert "limit" in schema["properties"]
        assert "offset" in schema["properties"]
        assert "lifecycle_state" in schema["properties"]

    def test_memory_get_requires_id(self):
        """memory_get requires memory_id."""
        get_tool = next(t for t in TOOLS if t.name == "memory_get")
        schema = get_tool.inputSchema

        assert "memory_id" in schema["properties"]
        assert schema["required"] == ["memory_id"]

    def test_memory_search_requires_query(self):
        """memory_search requires query."""
        search_tool = next(t for t in TOOLS if t.name == "memory_search")
        schema = search_tool.inputSchema

        assert "query" in schema["properties"]
        assert schema["required"] == ["query"]


class TestToolHandlers:
    """Tests for tool handlers."""

    def test_all_tools_have_handlers(self):
        """All tools have corresponding handlers."""
        tool_names = {tool.name for tool in TOOLS}
        handler_names = set(TOOL_HANDLERS.keys())

        assert tool_names == handler_names


class TestMemoryToDict:
    """Tests for memory_to_dict function."""

    def test_converts_all_fields(self, sample_memory):
        """memory_to_dict converts all fields correctly."""
        memory = sample_memory()
        result = memory_to_dict(memory)

        assert result["id"] == memory.id
        assert result["content"] == memory.content
        assert result["source"]["type"] == memory.source.type.value
        assert result["source"]["reference"] == memory.source.reference
        assert result["lifecycle_state"] == memory.lifecycle_state.value
        assert result["memory_type"] == memory.memory_type
        assert result["created_by"] == memory.created_by.value
        assert result["created_at"] == memory.created_at
        assert result["updated_at"] == memory.updated_at

    def test_serializable_to_json(self, sample_memory):
        """Output can be serialized to JSON."""
        memory = sample_memory()
        result = memory_to_dict(memory)

        # Should not raise
        json.dumps(result)


class TestFormatError:
    """Tests for format_error function."""

    def test_format_error_structure(self):
        """format_error returns correct structure."""
        result = format_error("Test error")

        assert "content" in result
        assert "isError" in result
        assert result["isError"] is True
        assert "Test error" in result["content"][0]["text"]

    def test_format_error_content_type(self):
        """format_error returns text content."""
        result = format_error("Test error")

        assert result["content"][0]["type"] == "text"


class TestFormatSuccess:
    """Tests for format_success function."""

    def test_format_success_structure(self):
        """format_success returns correct structure."""
        result = format_success({"key": "value"})

        assert "content" in result
        assert "isError" in result
        assert result["isError"] is False

    def test_format_success_serializes_data(self):
        """format_success serializes data to JSON string."""
        data = {"key": "value", "number": 42}
        result = format_success(data)

        # Text content should be JSON string
        assert result["content"][0]["type"] == "text"
        parsed = json.loads(result["content"][0]["text"])
        assert parsed == data


class TestMemoryStoreHandler:
    """Tests for memory_store tool handler."""

    def test_handler_exists(self):
        """handle_memory_store handler exists."""
        from omnivia_memory.mcp.server import handle_memory_store
        assert handle_memory_store is not None

    def test_handler_requires_source_type(self):
        """Handler validates required fields."""
        from omnivia_memory.mcp.server import handle_memory_store

        result = handle_memory_store({
            "content": "test content",
            # Missing source_type and source_reference
        })

        assert result["isError"] is True


class TestMemoryListHandler:
    """Tests for memory_list tool handler."""

    def test_handler_exists(self):
        """handle_memory_list handler exists."""
        from omnivia_memory.mcp.server import handle_memory_list
        assert handle_memory_list is not None


class TestMemoryGetHandler:
    """Tests for memory_get tool handler."""

    def test_handler_exists(self):
        """handle_memory_get handler exists."""
        from omnivia_memory.mcp.server import handle_memory_get
        assert handle_memory_get is not None

    def test_handler_returns_error_for_missing_id(self):
        """Handler returns error when memory_id missing."""
        from omnivia_memory.mcp.server import handle_memory_get

        result = handle_memory_get({})

        assert result["isError"] is True


class TestMemoryUpdateHandler:
    """Tests for memory_update tool handler."""

    def test_handler_exists(self):
        """handle_memory_update handler exists."""
        from omnivia_memory.mcp.server import handle_memory_update
        assert handle_memory_update is not None


class TestMemoryDeleteHandler:
    """Tests for memory_delete tool handler."""

    def test_handler_exists(self):
        """handle_memory_delete handler exists."""
        from omnivia_memory.mcp.server import handle_memory_delete
        assert handle_memory_delete is not None


class TestMemorySearchHandler:
    """Tests for memory_search tool handler."""

    def test_handler_exists(self):
        """handle_memory_search handler exists."""
        from omnivia_memory.mcp.server import handle_memory_search
        assert handle_memory_search is not None

    def test_handler_requires_query(self):
        """Handler validates required fields."""
        from omnivia_memory.mcp.server import handle_memory_search

        result = handle_memory_search({})

        assert result["isError"] is True


class TestMemoryApproveHandler:
    """Tests for memory_approve tool handler."""

    def test_handler_exists(self):
        """handle_memory_approve handler exists."""
        from omnivia_memory.mcp.server import handle_memory_approve
        assert handle_memory_approve is not None


class TestMemoryRejectHandler:
    """Tests for memory_reject tool handler."""

    def test_handler_exists(self):
        """handle_memory_reject handler exists."""
        from omnivia_memory.mcp.server import handle_memory_reject
        assert handle_memory_reject is not None