"""Tests for the search module."""

import pytest

from omnivia_memory.lifecycle.rules import CreatedBy
from omnivia_memory.memory.models import Memory
from omnivia_memory.provenance.models import Source, SourceType
from omnivia_memory.search.service import SearchService


@pytest.fixture
def search_service():
    """Create a search service for testing."""
    return SearchService()


@pytest.fixture
def sample_memory():
    """Create a sample memory for testing."""

    def _create_memory(content="Test content"):
        return Memory(
            content=content,
            source=Source(type=SourceType.FILE, reference="test.py"),
            created_by=CreatedBy.AGENT,
        )

    return _create_memory


class TestSearchService:
    """Tests for SearchService class."""

    def test_search_without_repository(self, search_service):
        """Search without repository returns empty list."""
        result = search_service.search("query")

        assert result == []

    def test_rank_results_returns_same_order(self, search_service, sample_memory):
        """rank_results returns memories in same order (Phase 1)."""
        memories = [
            sample_memory(content="First"),
            sample_memory(content="Second"),
            sample_memory(content="Third"),
        ]

        result = search_service.rank_results(memories, "query")

        assert result == memories

    def test_highlight_matches_returns_excerpt(self, search_service, sample_memory):
        """highlight_matches returns content excerpt."""
        memory = sample_memory(
            content="This is a longer memory content that contains important information about the project."
        )

        result = search_service.highlight_matches(memory, "important")

        assert "important" in result.lower()

    def test_highlight_matches_returns_full_content_if_short(self, search_service, sample_memory):
        """highlight_matches returns full content if under 200 chars."""
        memory = sample_memory(content="Short content")

        result = search_service.highlight_matches(memory, "Short")

        assert result == "Short content"

    def test_highlight_matches_handles_no_match(self, search_service, sample_memory):
        """highlight_matches handles query not in content."""
        memory = sample_memory(content="This is some content without the query")

        result = search_service.highlight_matches(memory, "nonexistent")

        # Should return truncated content
        assert "..." in result or len(result) <= 210

    def test_highlight_matches_adds_ellipsis(self, search_service, sample_memory):
        """highlight_matches adds ellipsis when truncating."""
        long_content = "A" * 300
        memory = sample_memory(content=long_content)

        result = search_service.highlight_matches(memory, "AAAA")

        # Should have ellipsis since content is longer than excerpt
        assert "..." in result
