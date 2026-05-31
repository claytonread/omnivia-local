"""Tests for the MCP server module."""

import json
import tempfile
from pathlib import Path

import pytest

from omnivia_memory.lifecycle.models import LifecycleState
from omnivia_memory.lifecycle.rules import CreatedBy
from omnivia_memory.memory.models import Memory
from omnivia_memory.persistence.database import Database, DatabaseConfig
from omnivia_memory.persistence.repositories import MemoryRepository
from omnivia_memory.provenance.models import Source, SourceType

from mcp.types import CallToolResult

from omnivia_memory.mcp.server import (
    TOOLS,
    TOOL_HANDLERS,
    error_result,
    success_result,
    memory_to_dict,
    handle_memory_store,
    handle_memory_get,
    handle_memory_update,
    handle_memory_delete,
    handle_memory_search,
    handle_memory_approve,
    handle_memory_reject,
    handle_graph_search,
    handle_graph_get_context,
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
        content: str = "Test memory content",
        source_type: SourceType = SourceType.FILE,
        source_ref: str = "test.py",
        created_by: CreatedBy = CreatedBy.AGENT,
        state: LifecycleState = LifecycleState.PROPOSED,
    ) -> Memory:
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

    def test_memory_approve_requires_id(self):
        """memory_approve requires memory_id."""
        approve_tool = next(t for t in TOOLS if t.name == "memory_approve")
        schema = approve_tool.inputSchema

        assert "memory_id" in schema["properties"]
        assert schema["required"] == ["memory_id"]

    def test_memory_reject_requires_id(self):
        """memory_reject requires memory_id."""
        reject_tool = next(t for t in TOOLS if t.name == "memory_reject")
        schema = reject_tool.inputSchema

        assert "memory_id" in schema["properties"]
        assert schema["required"] == ["memory_id"]


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


class TestErrorResult:
    """Tests for error_result function."""

    def test_returns_call_tool_result(self):
        """error_result returns CallToolResult."""
        result = error_result("Test error")

        assert isinstance(result, CallToolResult)

    def test_is_error_true(self):
        """error_result sets isError to True."""
        result = error_result("Test error")

        assert result.isError is True

    def test_content_contains_message(self):
        """error_result includes message in content."""
        result = error_result("Test error message")

        assert len(result.content) == 1
        assert "Test error message" in result.content[0].text


class TestSuccessResult:
    """Tests for success_result function."""

    def test_returns_call_tool_result(self):
        """success_result returns CallToolResult."""
        result = success_result({"key": "value"})

        assert isinstance(result, CallToolResult)

    def test_is_error_false(self):
        """success_result sets isError to False."""
        result = success_result({"key": "value"})

        assert result.isError is False

    def test_serializes_data_to_json(self):
        """success_result serializes data to JSON string."""
        data = {"key": "value", "number": 42}
        result = success_result(data)

        parsed = json.loads(result.content[0].text)
        assert parsed == data


class TestMemoryStoreHandler:
    """Tests for memory_store tool handler."""

    def test_handler_returns_error_for_missing_source_type(self):
        """Handler returns error when source_type missing."""
        result = handle_memory_store(
            {
                "content": "test content",
                "source_reference": "test.py",
                # Missing source_type
            }
        )

        assert isinstance(result, CallToolResult)
        assert result.isError is True
        assert "source_type" in result.content[0].text

    def test_handler_returns_error_for_missing_source_reference(self):
        """Handler returns error when source_reference missing."""
        result = handle_memory_store(
            {
                "content": "test content",
                "source_type": "file",
                # Missing source_reference
            }
        )

        assert isinstance(result, CallToolResult)
        assert result.isError is True
        assert "source_reference" in result.content[0].text


class TestMemoryGetHandler:
    """Tests for memory_get tool handler."""

    def test_handler_returns_error_for_missing_id(self):
        """Handler returns error when memory_id missing."""
        result = handle_memory_get({})

        assert isinstance(result, CallToolResult)
        assert result.isError is True
        assert "memory_id" in result.content[0].text


class TestMemoryUpdateHandler:
    """Tests for memory_update tool handler."""

    def test_handler_returns_error_for_missing_id(self):
        """Handler returns error when memory_id missing."""
        result = handle_memory_update({})

        assert isinstance(result, CallToolResult)
        assert result.isError is True
        assert "memory_id" in result.content[0].text


class TestMemoryDeleteHandler:
    """Tests for memory_delete tool handler."""

    def test_handler_returns_error_for_missing_id(self):
        """Handler returns error when memory_id missing."""
        result = handle_memory_delete({})

        assert isinstance(result, CallToolResult)
        assert result.isError is True
        assert "memory_id" in result.content[0].text


class TestMemorySearchHandler:
    """Tests for memory_search tool handler."""

    def test_handler_returns_error_for_missing_query(self):
        """Handler returns error when query missing."""
        result = handle_memory_search({})

        assert isinstance(result, CallToolResult)
        assert result.isError is True
        assert "query" in result.content[0].text


class TestMemoryApproveHandler:
    """Tests for memory_approve tool handler."""

    def test_handler_returns_error_for_missing_id(self):
        """Handler returns structured error when memory_id missing."""
        result = handle_memory_approve({})

        # Should return CallToolResult with isError=True, not raise KeyError
        assert isinstance(result, CallToolResult)
        assert result.isError is True
        assert "memory_id" in result.content[0].text

    def test_handler_returns_call_tool_result_type(self):
        """Handler returns CallToolResult, not dict."""
        result = handle_memory_approve({})

        assert type(result).__name__ == "CallToolResult"


class TestMemoryRejectHandler:
    """Tests for memory_reject tool handler."""

    def test_handler_returns_error_for_missing_id(self):
        """Handler returns structured error when memory_id missing."""
        result = handle_memory_reject({})

        # Should return CallToolResult with isError=True, not raise KeyError
        assert isinstance(result, CallToolResult)
        assert result.isError is True
        assert "memory_id" in result.content[0].text

    def test_handler_returns_call_tool_result_type(self):
        """Handler returns CallToolResult, not dict."""
        result = handle_memory_reject({})

        assert type(result).__name__ == "CallToolResult"


class TestGraphSearchTool:
    """Tests for graph_search tool definition."""

    def test_graph_search_tool_exists(self):
        """graph_search tool is defined."""
        tool_names = {tool.name for tool in TOOLS}
        assert "graph_search" in tool_names

    def test_graph_search_has_required_fields(self):
        """graph_search tool has correct schema."""
        search_tool = next(t for t in TOOLS if t.name == "graph_search")
        schema = search_tool.inputSchema

        assert "query" in schema["properties"]
        assert "entity_types" in schema["properties"]
        assert "depth" in schema["properties"]
        assert "limit" in schema["properties"]
        assert schema["required"] == ["query"]

    def test_graph_search_depth_defaults_to_zero(self):
        """graph_search defaults depth to 0 (no neighbors)."""
        search_tool = next(t for t in TOOLS if t.name == "graph_search")
        schema = search_tool.inputSchema

        assert schema["properties"]["depth"]["default"] == 0

    def test_graph_search_limit_defaults_to_twenty(self):
        """graph_search defaults limit to 20."""
        search_tool = next(t for t in TOOLS if t.name == "graph_search")
        schema = search_tool.inputSchema

        assert schema["properties"]["limit"]["default"] == 20


class TestGraphGetContextTool:
    """Tests for graph_get_context tool definition."""

    def test_graph_get_context_tool_exists(self):
        """graph_get_context tool is defined."""
        tool_names = {tool.name for tool in TOOLS}
        assert "graph_get_context" in tool_names

    def test_graph_get_context_has_required_fields(self):
        """graph_get_context tool has correct schema."""
        context_tool = next(t for t in TOOLS if t.name == "graph_get_context")
        schema = context_tool.inputSchema

        assert "entity_id" in schema["properties"]
        assert "depth" in schema["properties"]
        assert schema["required"] == ["entity_id"]

    def test_graph_get_context_depth_defaults_to_one(self):
        """graph_get_context defaults depth to 1 (direct neighbors)."""
        context_tool = next(t for t in TOOLS if t.name == "graph_get_context")
        schema = context_tool.inputSchema

        assert schema["properties"]["depth"]["default"] == 1


class TestGraphSearchHandler:
    """Tests for graph_search tool handler."""

    def test_handler_returns_error_for_missing_query(self):
        """Handler returns error when query missing."""
        result = handle_graph_search({})

        assert isinstance(result, CallToolResult)
        assert result.isError is True
        assert "query" in result.content[0].text


class TestGraphGetContextHandler:
    """Tests for graph_get_context tool handler."""

    def test_handler_returns_error_for_missing_entity_id(self):
        """Handler returns error when entity_id missing."""
        result = handle_graph_get_context({})

        assert isinstance(result, CallToolResult)
        assert result.isError is True
        assert "entity_id" in result.content[0].text
