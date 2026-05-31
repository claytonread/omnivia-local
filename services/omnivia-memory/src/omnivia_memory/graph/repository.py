"""Graph repository for SQLite persistence.

Provides CRUD operations for entities and relationships in the knowledge graph.
Uses SQLite for local-first, portable storage.
"""

from __future__ import annotations

from typing import Any

from omnivia_memory.graph.models import (
    ApprovalStatus,
    Entity,
    EntityType,
    Relationship,
    RelationshipType,
)
from omnivia_memory.persistence.database import Database


class EntityRepository:
    """Repository for persisting and retrieving entities from SQLite.

    Handles all database operations for graph entities, including:
    - Create, read, update, delete operations
    - Filtering by type and source
    - Governance status management

    Attributes:
        db: The database connection to use
    """

    def __init__(self, db: Database) -> None:
        self.db = db

    def create(self, entity: Entity) -> Entity:
        """Store a new entity in the database.

        Args:
            entity: The entity to store

        Returns:
            The stored entity (same object, persisted)

        Raises:
            ValueError: If an entity with the same ID already exists
        """
        # Check for existing entity with same ID
        existing = self.get(entity.id)
        if existing is not None:
            raise ValueError(f"Entity with ID {entity.id} already exists")

        self.db.execute(
            """
            INSERT INTO graph_entities (
                id, name, entity_type, source_id, approval_status,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entity.id,
                entity.name,
                entity.entity_type.value,
                entity.source_id,
                entity.approval_status.value,
                entity.created_at,
                entity.updated_at,
            ),
        )
        return entity

    def get(self, entity_id: str) -> Entity | None:
        """Retrieve an entity by its ID.

        Args:
            entity_id: The unique identifier of the entity

        Returns:
            The entity if found, None otherwise
        """
        cursor = self.db.execute(
            "SELECT * FROM graph_entities WHERE id = ?",
            (entity_id,),
        )
        row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_entity(row)

    def update(self, entity: Entity) -> Entity:
        """Update an existing entity in the database.

        Args:
            entity: The entity with updated values

        Returns:
            The updated entity

        Raises:
            ValueError: If the entity does not exist
        """
        existing = self.get(entity.id)
        if existing is None:
            raise ValueError(f"Entity with ID {entity.id} not found")

        # Update the updated_at timestamp
        entity.touch()

        self.db.execute(
            """
            UPDATE graph_entities SET
                name = ?,
                entity_type = ?,
                source_id = ?,
                approval_status = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                entity.name,
                entity.entity_type.value,
                entity.source_id,
                entity.approval_status.value,
                entity.updated_at,
                entity.id,
            ),
        )
        return entity

    def delete(self, entity_id: str) -> bool:
        """Delete an entity from the database.

        Also deletes all relationships connected to this entity to maintain
        referential integrity.

        Args:
            entity_id: The ID of the entity to delete

        Returns:
            True if the entity was deleted, False if it didn't exist
        """
        # Delete related relationships first to maintain referential integrity
        self.db.execute(
            "DELETE FROM graph_relationships WHERE source_entity_id = ? OR target_entity_id = ?",
            (entity_id, entity_id),
        )

        cursor = self.db.execute(
            "DELETE FROM graph_entities WHERE id = ?",
            (entity_id,),
        )
        return cursor.rowcount > 0

    def list_by_type(self, entity_type: EntityType) -> list[Entity]:
        """List all entities of a specific type.

        Args:
            entity_type: The type to filter by

        Returns:
            List of entities matching the type
        """
        cursor = self.db.execute(
            """
            SELECT * FROM graph_entities
            WHERE entity_type = ?
            ORDER BY name ASC
            """,
            (entity_type.value,),
        )

        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def list_by_source(self, source_id: str) -> list[Entity]:
        """List all entities derived from a specific source.

        Args:
            source_id: The source ID to filter by

        Returns:
            List of entities that came from this source
        """
        cursor = self.db.execute(
            """
            SELECT * FROM graph_entities
            WHERE source_id = ?
            ORDER BY created_at DESC
            """,
            (source_id,),
        )

        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def list_by_approval_status(self, status: ApprovalStatus) -> list[Entity]:
        """List all entities with a specific approval status.

        Args:
            status: The approval status to filter by

        Returns:
            List of entities with the specified status
        """
        cursor = self.db.execute(
            """
            SELECT * FROM graph_entities
            WHERE approval_status = ?
            ORDER BY created_at DESC
            """,
            (status.value,),
        )

        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def list_all(self, limit: int = 100, offset: int = 0) -> list[Entity]:
        """List all entities with pagination.

        Args:
            limit: Maximum number of entities to return
            offset: Number of entities to skip

        Returns:
            List of entities
        """
        cursor = self.db.execute(
            """
            SELECT * FROM graph_entities
            ORDER BY name ASC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )

        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def count(self) -> int:
        """Count total number of entities.

        Returns:
            Number of entities in the database
        """
        cursor = self.db.execute("SELECT COUNT(*) FROM graph_entities")
        return int(cursor.fetchone()[0])

    def _row_to_entity(self, row: Any) -> Entity:
        """Convert a database row to an Entity object.

        Args:
            row: SQLite row from the database

        Returns:
            Entity instance
        """
        return Entity(
            id=row["id"],
            name=row["name"],
            entity_type=EntityType(row["entity_type"]),
            source_id=row["source_id"],
            approval_status=ApprovalStatus(row["approval_status"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


class RelationshipRepository:
    """Repository for persisting and retrieving relationships from SQLite.

    Handles all database operations for graph relationships, including:
    - Create, read, update, delete operations
    - Neighbor queries for graph traversal
    - Filtering by entity

    Attributes:
        db: The database connection to use
    """

    def __init__(self, db: Database) -> None:
        self.db = db

    def create(self, relationship: Relationship) -> Relationship:
        """Store a new relationship in the database.

        Args:
            relationship: The relationship to store

        Returns:
            The stored relationship (same object, persisted)

        Raises:
            ValueError: If a relationship with the same ID already exists
        """
        # Check for existing relationship with same ID
        existing = self.get(relationship.id)
        if existing is not None:
            raise ValueError(f"Relationship with ID {relationship.id} already exists")

        self.db.execute(
            """
            INSERT INTO graph_relationships (
                id, source_entity_id, target_entity_id, relationship_type,
                source_id, approval_status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                relationship.id,
                relationship.source_entity_id,
                relationship.target_entity_id,
                relationship.relationship_type.value,
                relationship.source_id,
                relationship.approval_status.value,
                relationship.created_at,
                relationship.updated_at,
            ),
        )
        return relationship

    def get(self, relationship_id: str) -> Relationship | None:
        """Retrieve a relationship by its ID.

        Args:
            relationship_id: The unique identifier of the relationship

        Returns:
            The relationship if found, None otherwise
        """
        cursor = self.db.execute(
            "SELECT * FROM graph_relationships WHERE id = ?",
            (relationship_id,),
        )
        row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_relationship(row)

    def update(self, relationship: Relationship) -> Relationship:
        """Update an existing relationship in the database.

        Args:
            relationship: The relationship with updated values

        Returns:
            The updated relationship

        Raises:
            ValueError: If the relationship does not exist
        """
        existing = self.get(relationship.id)
        if existing is None:
            raise ValueError(f"Relationship with ID {relationship.id} not found")

        # Update the updated_at timestamp
        relationship.touch()

        self.db.execute(
            """
            UPDATE graph_relationships SET
                source_entity_id = ?,
                target_entity_id = ?,
                relationship_type = ?,
                source_id = ?,
                approval_status = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                relationship.source_entity_id,
                relationship.target_entity_id,
                relationship.relationship_type.value,
                relationship.source_id,
                relationship.approval_status.value,
                relationship.updated_at,
                relationship.id,
            ),
        )
        return relationship

    def delete(self, relationship_id: str) -> bool:
        """Delete a relationship from the database.

        Args:
            relationship_id: The ID of the relationship to delete

        Returns:
            True if the relationship was deleted, False if it didn't exist
        """
        cursor = self.db.execute(
            "DELETE FROM graph_relationships WHERE id = ?",
            (relationship_id,),
        )
        return cursor.rowcount > 0

    def get_neighbors(self, entity_id: str) -> list[tuple[Entity, Relationship]]:
        """Get all entities directly connected to a given entity.

        Returns both incoming and outgoing relationships, paired with the
        connected entity. This enables graph traversal for queries like
        "what does this entity depend on?" or "what depends on this?".

        Args:
            entity_id: The ID of the entity to get neighbors for

        Returns:
            List of (entity, relationship) tuples for all connected entities
        """
        neighbors: list[tuple[Entity, Relationship]] = []

        # Get outgoing relationships (where this entity is the source)
        cursor = self.db.execute(
            """
            SELECT r.*, e.*
            FROM graph_relationships r
            JOIN graph_entities e ON r.target_entity_id = e.id
            WHERE r.source_entity_id = ?
            """,
            (entity_id,),
        )
        for row in cursor.fetchall():
            relationship = self._row_to_relationship(row)
            entity = self._row_to_entity(row)
            neighbors.append((entity, relationship))

        # Get incoming relationships (where this entity is the target)
        cursor = self.db.execute(
            """
            SELECT r.*, e.*
            FROM graph_relationships r
            JOIN graph_entities e ON r.source_entity_id = e.id
            WHERE r.target_entity_id = ?
            """,
            (entity_id,),
        )
        for row in cursor.fetchall():
            relationship = self._row_to_relationship(row)
            entity = self._row_to_entity(row)
            neighbors.append((entity, relationship))

        return neighbors

    def get_by_entity(self, entity_id: str) -> list[Relationship]:
        """Get all relationships connected to a given entity.

        Returns both relationships where the entity is the source and where
        it is the target.

        Args:
            entity_id: The ID of the entity to get relationships for

        Returns:
            List of relationships connected to the entity
        """
        cursor = self.db.execute(
            """
            SELECT * FROM graph_relationships
            WHERE source_entity_id = ? OR target_entity_id = ?
            ORDER BY created_at DESC
            """,
            (entity_id, entity_id),
        )

        return [self._row_to_relationship(row) for row in cursor.fetchall()]

    def get_by_type(
        self, entity_id: str, relationship_type: RelationshipType
    ) -> list[Relationship]:
        """Get relationships of a specific type for an entity.

        Args:
            entity_id: The ID of the entity
            relationship_type: The type of relationships to retrieve

        Returns:
            List of matching relationships
        """
        cursor = self.db.execute(
            """
            SELECT * FROM graph_relationships
            WHERE (source_entity_id = ? OR target_entity_id = ?)
            AND relationship_type = ?
            ORDER BY created_at DESC
            """,
            (entity_id, entity_id, relationship_type.value),
        )

        return [self._row_to_relationship(row) for row in cursor.fetchall()]

    def get_outgoing(self, entity_id: str) -> list[Relationship]:
        """Get relationships where the entity is the source (outgoing).

        Args:
            entity_id: The ID of the source entity

        Returns:
            List of outgoing relationships
        """
        cursor = self.db.execute(
            """
            SELECT * FROM graph_relationships
            WHERE source_entity_id = ?
            ORDER BY created_at DESC
            """,
            (entity_id,),
        )

        return [self._row_to_relationship(row) for row in cursor.fetchall()]

    def get_incoming(self, entity_id: str) -> list[Relationship]:
        """Get relationships where the entity is the target (incoming).

        Args:
            entity_id: The ID of the target entity

        Returns:
            List of incoming relationships
        """
        cursor = self.db.execute(
            """
            SELECT * FROM graph_relationships
            WHERE target_entity_id = ?
            ORDER BY created_at DESC
            """,
            (entity_id,),
        )

        return [self._row_to_relationship(row) for row in cursor.fetchall()]

    def list_all(self, limit: int = 100, offset: int = 0) -> list[Relationship]:
        """List all relationships with pagination.

        Args:
            limit: Maximum number of relationships to return
            offset: Number of relationships to skip

        Returns:
            List of relationships
        """
        cursor = self.db.execute(
            """
            SELECT * FROM graph_relationships
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )

        return [self._row_to_relationship(row) for row in cursor.fetchall()]

    def count(self) -> int:
        """Count total number of relationships.

        Returns:
            Number of relationships in the database
        """
        cursor = self.db.execute("SELECT COUNT(*) FROM graph_relationships")
        return int(cursor.fetchone()[0])

    def _row_to_entity(self, row: Any) -> Entity:
        """Convert a database row to an Entity object.

        Args:
            row: SQLite row from the database

        Returns:
            Entity instance
        """
        return Entity(
            id=row["id"],
            name=row["name"],
            entity_type=EntityType(row["entity_type"]),
            source_id=row["source_id"],
            approval_status=ApprovalStatus(row["approval_status"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def _row_to_relationship(self, row: Any) -> Relationship:
        """Convert a database row to a Relationship object.

        Args:
            row: SQLite row from the database

        Returns:
            Relationship instance
        """
        return Relationship(
            id=row["id"],
            source_entity_id=row["source_entity_id"],
            target_entity_id=row["target_entity_id"],
            relationship_type=RelationshipType(row["relationship_type"]),
            source_id=row["source_id"],
            approval_status=ApprovalStatus(row["approval_status"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def link_to_memory(
        self,
        entity_id: str,
        memory_id: str,
        source_id: str,
    ) -> bool:
        """Create a link between an entity and a memory.

        This tracks which memory provided knowledge about this entity.

        Args:
            entity_id: The entity to link
            memory_id: The memory to link to
            source_id: Reference to the source document

        Returns:
            True if link was created
        """
        from datetime import datetime, timezone

        # Check if link already exists
        existing = self.db.execute(
            "SELECT * FROM entity_memory_links WHERE entity_id = ? AND memory_id = ?",
            (entity_id, memory_id),
        ).fetchone()

        if existing is not None:
            return False  # Link already exists

        self.db.execute(
            """
            INSERT INTO entity_memory_links (
                entity_id, memory_id, source_id, created_at
            ) VALUES (?, ?, ?, ?)
            """,
            (
                entity_id,
                memory_id,
                source_id,
                datetime.now(timezone.utc).isoformat(),
            ),
        )

        return True
