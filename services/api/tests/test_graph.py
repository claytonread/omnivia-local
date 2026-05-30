"""
Tests for Node and Edge CRUD endpoints.

Uses a temporary database to test API handlers without side effects.
"""

import pytest
import tempfile
import json
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from services.api.database import Base
from services.api.models import Node, Edge, NodeCreate, EdgeCreate


@pytest.fixture
def db_session():
    """Create a temporary in-memory database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestNodeModel:
    """Test Node database model operations."""

    def test_create_node(self, db_session):
        """Creating a node persists it to the database."""
        node = Node(
            id="test-id-123",
            node_type="concept",
            title="Test Concept",
            body="A test concept for unit testing",
            tags="testing,unit",
        )
        db_session.add(node)
        db_session.commit()

        retrieved = db_session.query(Node).filter(Node.id == "test-id-123").first()
        assert retrieved is not None
        assert retrieved.node_type == "concept"
        assert retrieved.title == "Test Concept"
        assert retrieved.body == "A test concept for unit testing"
        assert retrieved.tags == "testing,unit"

    def test_node_with_source_ids(self, db_session):
        """Node can store JSON array of source IDs."""
        node = Node(
            id="test-id-456",
            node_type="decision",
            title="Use SQLite",
            source_ids='["source-1", "source-2"]',
        )
        db_session.add(node)
        db_session.commit()

        retrieved = db_session.query(Node).filter(Node.id == "test-id-456").first()
        assert retrieved.source_ids == '["source-1", "source-2"]'

    def test_node_query_by_type(self, db_session):
        """Can filter nodes by type."""
        # Create nodes of different types
        for i, node_type in enumerate(["concept", "person", "concept", "project"]):
            node = Node(id=f"id-{node_type}-{i}", node_type=node_type, title=node_type)
            db_session.add(node)
        db_session.commit()

        concepts = db_session.query(Node).filter(Node.node_type == "concept").all()
        assert len(concepts) == 2


class TestEdgeModel:
    """Test Edge database model operations."""

    def test_create_edge(self, db_session):
        """Creating an edge persists it to the database."""
        # First create two nodes
        source_node = Node(id="source-123", node_type="concept", title="Source")
        target_node = Node(id="target-456", node_type="concept", title="Target")
        db_session.add(source_node)
        db_session.add(target_node)
        db_session.commit()

        # Now create edge
        edge = Edge(
            id="edge-789",
            source_node_id="source-123",
            target_node_id="target-456",
            relationship_type="relates_to",
            direction="bidirectional",
            weight=0.8,
        )
        db_session.add(edge)
        db_session.commit()

        retrieved = db_session.query(Edge).filter(Edge.id == "edge-789").first()
        assert retrieved is not None
        assert retrieved.source_node_id == "source-123"
        assert retrieved.target_node_id == "target-456"
        assert retrieved.relationship_type == "relates_to"
        assert retrieved.direction == "bidirectional"
        assert retrieved.weight == 0.8

    def test_edge_query_by_type(self, db_session):
        """Can filter edges by relationship type."""
        # Create nodes and edges
        source = Node(id="source-a", node_type="concept", title="Source A")
        target = Node(id="target-a", node_type="concept", title="Target A")
        db_session.add(source)
        db_session.add(target)
        db_session.commit()

        for i, rel_type in enumerate(["depends_on", "supports", "depends_on"]):
            edge = Edge(
                id=f"edge-{rel_type}-{i}",
                source_node_id="source-a",
                target_node_id="target-a",
                relationship_type=rel_type,
            )
            db_session.add(edge)
        db_session.commit()

        dependencies = db_session.query(Edge).filter(
            Edge.relationship_type == "depends_on"
        ).all()
        assert len(dependencies) == 2

    def test_edge_query_by_source_node(self, db_session):
        """Can find edges connected to a specific node."""
        # Create chain: A -> B -> C
        node_a = Node(id="node-a", node_type="concept", title="A")
        node_b = Node(id="node-b", node_type="concept", title="B")
        node_c = Node(id="node-c", node_type="concept", title="C")
        for node in [node_a, node_b, node_c]:
            db_session.add(node)
        db_session.commit()

        edge_ab = Edge(id="ab", source_node_id="node-a", target_node_id="node-b", relationship_type="relates_to")
        edge_bc = Edge(id="bc", source_node_id="node-b", target_node_id="node-c", relationship_type="relates_to")
        for edge in [edge_ab, edge_bc]:
            db_session.add(edge)
        db_session.commit()

        # Node B should have 2 edges
        node_b_edges = db_session.query(Edge).filter(
            (Edge.source_node_id == "node-b") | (Edge.target_node_id == "node-b")
        ).all()
        assert len(node_b_edges) == 2


class TestNodeCreateSchema:
    """Test Pydantic schema validation for Node creation."""

    @pytest.mark.parametrize("node_type", [
        "concept",
        "person",
        "project",
        "decision",
        "constraint",
        "system",
    ])
    def test_valid_node_types(self, node_type):
        """All documented node types are accepted."""
        node = NodeCreate(node_type=node_type, title="Test")
        assert node.node_type == node_type

    def test_node_create_with_optional_fields(self):
        """NodeCreate accepts all optional fields."""
        node = NodeCreate(
            node_type="decision",
            title="Use PostgreSQL",
            body="We decided to use PostgreSQL for production",
            tags="database,backend",
            source_ids=["doc-1", "doc-2"],
            metadata={"decided_by": "team", "date": "2024-01-15"},
        )
        assert node.node_type == "decision"
        assert node.body == "We decided to use PostgreSQL for production"
        assert node.source_ids == ["doc-1", "doc-2"]
        assert node.metadata == {"decided_by": "team", "date": "2024-01-15"}


class TestEdgeCreateSchema:
    """Test Pydantic schema validation for Edge creation."""

    def test_edge_create_required_fields(self):
        """EdgeCreate requires source, target, and relationship type."""
        edge = EdgeCreate(
            source_node_id="abc-123",
            target_node_id="def-456",
            relationship_type="supports",
        )
        assert edge.source_node_id == "abc-123"
        assert edge.target_node_id == "def-456"
        assert edge.relationship_type == "supports"

    @pytest.mark.parametrize("direction", ["directed", "bidirectional"])
    def test_valid_directions(self, direction):
        """Both direction values are accepted."""
        edge = EdgeCreate(
            source_node_id="a",
            target_node_id="b",
            relationship_type="relates_to",
            direction=direction,
        )
        assert edge.direction == direction

    def test_edge_create_with_weight(self):
        """EdgeCreate accepts custom weight."""
        edge = EdgeCreate(
            source_node_id="a",
            target_node_id="b",
            relationship_type="depends_on",
            weight=0.95,
        )
        assert edge.weight == 0.95