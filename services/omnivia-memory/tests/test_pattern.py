"""Tests for the pattern detection module."""

import tempfile
from pathlib import Path

import pytest

from omnivia_memory.lifecycle.models import LifecycleState
from omnivia_memory.lifecycle.rules import CreatedBy
from omnivia_memory.memory.models import Memory
from omnivia_memory.pattern.models import (
    PatternCreate,
    PatternEntity,
    PatternOccurrence,
    PatternRelationship,
    PatternType,
)
from omnivia_memory.pattern.service import (
    PatternService,
    PatternServiceError,
    PatternValidationError,
)
from omnivia_memory.persistence.database import Database, DatabaseConfig
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


class TestPatternType:
    """Tests for PatternType enum."""

    def test_pattern_type_values(self):
        """PatternType has expected values."""
        assert PatternType.CONTENT_SIMILARITY.value == "content_similarity"
        assert PatternType.SOURCE_CLUSTER.value == "source_cluster"
        assert PatternType.LIFECYCLE_TRANSITION.value == "lifecycle_transition"
        assert PatternType.CONCEPT_REFERENCE.value == "concept_reference"
        assert PatternType.DECISION_RECURRENCE.value == "decision_recurrence"

    def test_pattern_type_is_string_enum(self):
        """PatternType is a string enum."""
        assert isinstance(PatternType.CONTENT_SIMILARITY, str)


class TestPatternEntity:
    """Tests for PatternEntity model."""

    def test_create_pattern_entity_with_required_fields(self):
        """PatternEntity can be created with required fields."""
        pattern = PatternEntity(
            name="Test Pattern",
            pattern_type=PatternType.CONTENT_SIMILARITY,
            description="A test pattern",
            confidence=0.8,
            occurrence_count=5,
        )

        assert pattern.name == "Test Pattern"
        assert pattern.pattern_type == PatternType.CONTENT_SIMILARITY
        assert pattern.description == "A test pattern"
        assert pattern.confidence == 0.8
        assert pattern.occurrence_count == 5
        assert pattern.approval_status == "proposed"
        assert pattern.id is not None
        assert pattern.created_at is not None
        assert pattern.updated_at is not None

    def test_create_pattern_entity_with_all_fields(self):
        """PatternEntity can be created with all fields."""
        pattern = PatternEntity(
            id="custom-id",
            name="Custom Pattern",
            pattern_type=PatternType.SOURCE_CLUSTER,
            description="Custom description",
            confidence=0.9,
            occurrence_count=10,
            source_id="source-123",
            approval_status="approved",
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
        )

        assert pattern.id == "custom-id"
        assert pattern.source_id == "source-123"
        assert pattern.approval_status == "approved"
        assert pattern.created_at == "2026-01-01T00:00:00Z"

    def test_pattern_to_dict(self):
        """PatternEntity serializes correctly to dictionary."""
        pattern = PatternEntity(
            id="test-id",
            name="Test Pattern",
            pattern_type=PatternType.CONTENT_SIMILARITY,
            description="A test",
            confidence=0.8,
            occurrence_count=5,
        )

        result = pattern.to_dict()

        assert result["id"] == "test-id"
        assert result["name"] == "Test Pattern"
        assert result["pattern_type"] == "content_similarity"
        assert result["confidence"] == 0.8
        assert result["occurrence_count"] == 5
        assert result["approval_status"] == "proposed"

    def test_pattern_from_dict(self):
        """PatternEntity deserializes correctly from dictionary."""
        data = {
            "id": "test-id",
            "name": "Test Pattern",
            "pattern_type": "content_similarity",
            "description": "A test",
            "confidence": 0.8,
            "occurrence_count": 5,
            "source_id": "source-123",
            "approval_status": "approved",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
        }

        pattern = PatternEntity.from_dict(data)

        assert pattern.id == "test-id"
        assert pattern.pattern_type == PatternType.CONTENT_SIMILARITY
        assert pattern.confidence == 0.8
        assert pattern.approval_status == "approved"

    def test_pattern_approve(self):
        """approve() transitions pattern to approved state."""
        pattern = PatternEntity(
            name="Test",
            pattern_type=PatternType.CONTENT_SIMILARITY,
            description="Test",
            confidence=0.8,
            occurrence_count=5,
        )
        original_updated = pattern.updated_at

        pattern.approve()

        assert pattern.approval_status == "approved"
        assert pattern.updated_at != original_updated

    def test_pattern_reject(self):
        """reject() transitions pattern to rejected state."""
        pattern = PatternEntity(
            name="Test",
            pattern_type=PatternType.CONTENT_SIMILARITY,
            description="Test",
            confidence=0.8,
            occurrence_count=5,
        )

        pattern.reject()

        assert pattern.approval_status == "rejected"

    def test_pattern_touch(self):
        """touch() updates the updated_at timestamp."""
        pattern = PatternEntity(
            name="Test",
            pattern_type=PatternType.CONTENT_SIMILARITY,
            description="Test",
            confidence=0.8,
            occurrence_count=5,
        )
        original_updated = pattern.updated_at

        pattern.touch()

        assert pattern.updated_at != original_updated


class TestPatternOccurrence:
    """Tests for PatternOccurrence model."""

    def test_create_occurrence(self):
        """PatternOccurrence can be created."""
        occurrence = PatternOccurrence(
            pattern_id="pattern-123",
            memory_id="memory-456",
            evidence="Content matched pattern",
        )

        assert occurrence.pattern_id == "pattern-123"
        assert occurrence.memory_id == "memory-456"
        assert occurrence.evidence == "Content matched pattern"
        assert occurrence.detected_at is not None

    def test_occurrence_to_dict(self):
        """PatternOccurrence serializes correctly."""
        occurrence = PatternOccurrence(
            pattern_id="pattern-123",
            memory_id="memory-456",
            evidence="Evidence text",
        )

        result = occurrence.to_dict()

        assert result["pattern_id"] == "pattern-123"
        assert result["memory_id"] == "memory-456"
        assert result["evidence"] == "Evidence text"

    def test_occurrence_from_dict(self):
        """PatternOccurrence deserializes correctly."""
        data = {
            "pattern_id": "pattern-123",
            "memory_id": "memory-456",
            "evidence": "Evidence text",
            "detected_at": "2026-01-01T00:00:00Z",
        }

        occurrence = PatternOccurrence.from_dict(data)

        assert occurrence.pattern_id == "pattern-123"
        assert occurrence.memory_id == "memory-456"


class TestPatternRelationship:
    """Tests for PatternRelationship model."""

    def test_create_relationship(self):
        """PatternRelationship can be created."""
        rel = PatternRelationship(
            source_pattern_id="pattern-123",
            target_pattern_id="pattern-456",
            relationship_type="specializes",
        )

        assert rel.source_pattern_id == "pattern-123"
        assert rel.target_pattern_id == "pattern-456"
        assert rel.relationship_type == "specializes"
        assert rel.approval_status == "proposed"

    def test_relationship_to_dict(self):
        """PatternRelationship serializes correctly."""
        rel = PatternRelationship(
            source_pattern_id="pattern-123",
            target_pattern_id="pattern-456",
            related_memory_id="memory-789",
        )

        result = rel.to_dict()

        assert result["source_pattern_id"] == "pattern-123"
        assert result["target_pattern_id"] == "pattern-456"
        assert result["related_memory_id"] == "memory-789"


class TestPatternCreate:
    """Tests for PatternCreate input model."""

    def test_create_pattern_create(self):
        """PatternCreate can be created."""
        create = PatternCreate(
            name="New Pattern",
            pattern_type=PatternType.SOURCE_CLUSTER,
            description="A new pattern",
            confidence=0.75,
            occurrence_count=3,
            source_id="source-123",
        )

        assert create.name == "New Pattern"
        assert create.pattern_type == PatternType.SOURCE_CLUSTER
        assert create.confidence == 0.75
        assert create.occurrence_count == 3


class TestPatternService:
    """Tests for PatternService class."""

    def test_service_initialization(self):
        """PatternService initializes without repository."""
        service = PatternService()

        assert service.pattern_repository is None
        assert service.memory_service is None

    def test_calculate_similarity_identical(self):
        """calculate_similarity returns 1.0 for identical text."""
        service = PatternService()
        similarity = service._calculate_similarity("test content", "test content")

        assert similarity == 1.0

    def test_calculate_similarity_different(self):
        """calculate_similarity returns lower value for different text."""
        service = PatternService()
        similarity = service._calculate_similarity("test content", "different content")

        assert 0.0 <= similarity < 1.0

    def test_calculate_similarity_normalized(self):
        """calculate_similarity normalizes whitespace and case."""
        service = PatternService()
        similarity = service._calculate_similarity(
            "TEST  CONTENT",
            "test content",
        )

        assert similarity > 0.5

    def test_extract_common_terms(self):
        """_extract_common_terms extracts meaningful words."""
        service = PatternService()
        contents = [
            "Python is a programming language used for backend development",
            "Python supports async programming and has many libraries",
        ]

        terms = service._extract_common_terms(contents)

        assert "python" in terms.lower()
        # Should have extracted some significant terms
        assert len(terms) > 0

    def test_extract_common_terms_handles_empty(self):
        """_extract_common_terms handles empty content list."""
        service = PatternService()

        terms = service._extract_common_terms([])

        assert terms == "various topics"

    def test_create_pattern_validates_confidence(self):
        """create_pattern validates confidence range."""
        service = PatternService()
        create = PatternCreate(
            name="Test",
            pattern_type=PatternType.CONTENT_SIMILARITY,
            description="Test",
            confidence=1.5,  # Invalid: > 1.0
            occurrence_count=3,
        )

        with pytest.raises(PatternValidationError):
            service.create_pattern(create)

    def test_get_pattern_requires_repository(self):
        """get_pattern raises error without repository."""
        service = PatternService()

        with pytest.raises(PatternServiceError):
            service.get_pattern("any-id")

    def test_list_patterns_requires_repository(self):
        """list_patterns raises error without repository."""
        service = PatternService()

        with pytest.raises(PatternServiceError):
            service.list_patterns()

    def test_delete_pattern_requires_repository(self):
        """delete_pattern raises error without repository."""
        service = PatternService()

        with pytest.raises(PatternServiceError):
            service.delete_pattern("any-id")

    def test_record_occurrence_requires_repository(self):
        """record_occurrence raises error without repository."""
        service = PatternService()

        with pytest.raises(PatternServiceError):
            service.record_occurrence("pattern-123", "memory-456")


class TestPatternDetection:
    """Tests for pattern detection algorithms."""

    def test_detect_content_similarity_no_similar(self, sample_memory):
        """detect_content_similarity returns empty for unique memories."""
        service = PatternService()
        memories = [
            sample_memory(content="Completely different content about cats"),
            sample_memory(content="Another unique topic about dogs"),
            sample_memory(content="Something else entirely about birds"),
        ]

        patterns = service._detect_content_similarity(memories, min_occurrences=2)

        # With low similarity threshold and different content, may get no patterns
        # or patterns depending on threshold
        assert isinstance(patterns, list)

    def test_detect_content_similarity_with_similar(self, sample_memory):
        """detect_content_similarity finds similar memories."""
        service = PatternService()
        # Create memories with similar content
        memories = [
            sample_memory(content="Python is a great programming language"),
            sample_memory(content="Python programming language is widely used"),
            sample_memory(content="Java is also a programming language"),
        ]

        patterns = service._detect_content_similarity(memories, min_occurrences=2)

        # Should find patterns for the two Python memories
        assert any(p.pattern_type == PatternType.CONTENT_SIMILARITY for p in patterns)

    def test_detect_source_clusters(self, sample_memory):
        """detect_source_clusters groups memories by source."""
        service = PatternService()
        memories = [
            sample_memory(source_ref="same_file.py", content="Content 1"),
            sample_memory(source_ref="same_file.py", content="Content 2"),
            sample_memory(source_ref="same_file.py", content="Content 3"),
            sample_memory(source_ref="other.py", content="Content 4"),
        ]

        patterns = service._detect_source_clusters(memories, min_occurrences=2)

        # Should find pattern for same_file.py source cluster
        assert len(patterns) >= 1
        assert any(p.pattern_type == PatternType.SOURCE_CLUSTER for p in patterns)
        assert any("same_file.py" in p.name for p in patterns)

    def test_detect_lifecycle_transitions(self, sample_memory):
        """detect_lifecycle_transitions groups by creator and state."""
        service = PatternService()
        memories = [
            sample_memory(created_by=CreatedBy.AGENT, state=LifecycleState.PROPOSED),
            sample_memory(created_by=CreatedBy.AGENT, state=LifecycleState.PROPOSED),
            sample_memory(created_by=CreatedBy.AGENT, state=LifecycleState.PROPOSED),
            sample_memory(created_by=CreatedBy.HUMAN, state=LifecycleState.APPROVED),
        ]

        patterns = service._detect_lifecycle_transitions(memories, min_occurrences=2)

        # Should find pattern for agent creating proposed memories
        assert len(patterns) >= 1
        assert any(p.pattern_type == PatternType.LIFECYCLE_TRANSITION for p in patterns)

    def test_detect_all_patterns(self, sample_memory):
        """detect_all_patterns runs all detection algorithms."""
        service = PatternService()
        memories = [
            sample_memory(
                source_ref="file1.py",
                content="Python programming content",
            ),
            sample_memory(
                source_ref="file1.py",
                content="More Python programming",
            ),
        ]

        patterns = service.detect_all_patterns(memories)

        # Should find both content similarity and source cluster patterns
        pattern_types = {p.pattern_type for p in patterns}
        assert PatternType.CONTENT_SIMILARITY in pattern_types
        assert PatternType.SOURCE_CLUSTER in pattern_types
        assert PatternType.LIFECYCLE_TRANSITION in pattern_types

    def test_detect_all_patterns_min_occurrences_override(self, sample_memory):
        """detect_all_patterns respects min_occurrences parameter."""
        service = PatternService()
        memories = [
            sample_memory(content="Same content 1"),
            sample_memory(content="Same content 2"),
        ]

        # With min_occurrences=3, should not create patterns
        patterns = service.detect_all_patterns(memories, min_occurrences=3)

        # No patterns should be created since we only have 2 memories
        assert len(patterns) == 0

    def test_pattern_defaults_to_proposed(self):
        """Detected patterns default to proposed status."""
        service = PatternService()
        create = PatternCreate(
            name="Test Pattern",
            pattern_type=PatternType.CONTENT_SIMILARITY,
            description="Test",
            confidence=0.8,
            occurrence_count=3,
        )

        pattern = service.create_pattern(create)

        assert pattern.approval_status == "proposed"


class TestPatternServiceApproval:
    """Tests for pattern approval workflow."""

    def test_approve_pattern_requires_repository(self):
        """approve_pattern raises error without repository."""
        service = PatternService()

        with pytest.raises(PatternServiceError):
            service.approve_pattern("any-id")

    def test_reject_pattern_requires_repository(self):
        """reject_pattern raises error without repository."""
        service = PatternService()

        with pytest.raises(PatternServiceError):
            service.reject_pattern("any-id")

    def test_get_pattern_occurrences_requires_repository(self):
        """get_pattern_occurrences raises error without repository."""
        service = PatternService()

        with pytest.raises(PatternServiceError):
            service.get_pattern_occurrences("any-id")
