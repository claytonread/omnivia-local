"""Tests for the provenance module (Source model)."""

from omnivia_memory.provenance.models import Source, SourceType


class TestSourceType:
    """Tests for SourceType enum."""

    def test_source_type_values(self):
        """SourceType enum has expected values."""
        assert SourceType.FILE == "file"
        assert SourceType.URL == "url"
        assert SourceType.ADR == "adr"
        assert SourceType.HUMAN == "human"

    def test_source_type_is_string_enum(self):
        """SourceType values are strings for serialization."""
        assert isinstance(SourceType.FILE.value, str)


class TestSource:
    """Tests for Source model."""

    def test_create_source_with_required_fields(self):
        """Source can be created with type and reference."""
        source = Source(
            type=SourceType.FILE,
            reference="services/omnivia-memory/src/module.py",
        )
        assert source.type == SourceType.FILE
        assert source.reference == "services/omnivia-memory/src/module.py"
        assert source.description is None

    def test_create_source_with_all_fields(self):
        """Source can be created with optional description."""
        source = Source(
            type=SourceType.ADR,
            reference="ADR-0001",
            description="Architecture decision on initial stack",
        )
        assert source.type == SourceType.ADR
        assert source.reference == "ADR-0001"
        assert source.description == "Architecture decision on initial stack"

    def test_source_to_dict(self):
        """Source serializes correctly to dictionary."""
        source = Source(
            type=SourceType.HUMAN,
            reference="direct human assertion",
            description="Verified by team member",
        )
        result = source.to_dict()

        assert result == {
            "type": "human",
            "reference": "direct human assertion",
            "description": "Verified by team member",
        }

    def test_source_to_dict_without_description(self):
        """Source serializes correctly without description."""
        source = Source(
            type=SourceType.URL,
            reference="https://example.com/docs",
        )
        result = source.to_dict()

        assert result == {
            "type": "url",
            "reference": "https://example.com/docs",
            "description": None,
        }

    def test_source_from_dict(self):
        """Source deserializes correctly from dictionary."""
        data = {
            "type": "file",
            "reference": "README.md",
            "description": "Project readme",
        }
        source = Source.from_dict(data)

        assert source.type == SourceType.FILE
        assert source.reference == "README.md"
        assert source.description == "Project readme"

    def test_source_equality(self):
        """Sources with same values are equal."""
        source1 = Source(type=SourceType.FILE, reference="test.py")
        source2 = Source(type=SourceType.FILE, reference="test.py")

        assert source1 == source2

    def test_source_inequality(self):
        """Sources with different values are not equal."""
        source1 = Source(type=SourceType.FILE, reference="test1.py")
        source2 = Source(type=SourceType.FILE, reference="test2.py")

        assert source1 != source2

    def test_source_repr(self):
        """Source has readable string representation."""
        source = Source(type=SourceType.ADR, reference="ADR-0001")
        result = repr(source)

        assert "Source" in result
        assert "adr" in result
        assert "ADR-0001" in result
