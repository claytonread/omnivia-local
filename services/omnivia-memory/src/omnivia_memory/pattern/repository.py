"""Pattern repository for SQLite persistence.

Provides CRUD operations for patterns and their occurrences in the
knowledge graph. Uses SQLite for local-first, portable storage.
"""

from __future__ import annotations

from typing import Any

from omnivia_memory.pattern.models import (
    PatternEntity,
    PatternOccurrence,
    PatternType,
)
from omnivia_memory.persistence.database import Database


class PatternRepository:
    """Repository for persisting and retrieving patterns from SQLite.

    Handles all database operations for patterns, including:
    - Create, read, update, delete operations
    - Filtering by type and source
    - Occurrence tracking

    Attributes:
        db: The database connection to use
    """

    def __init__(self, db: Database) -> None:
        self.db = db

    def create(self, pattern: PatternEntity) -> PatternEntity:
        """Store a new pattern in the database.

        Args:
            pattern: The pattern to store

        Returns:
            The stored pattern (same object, persisted)

        Raises:
            ValueError: If a pattern with the same ID already exists
        """
        # Check for existing pattern with same ID
        existing = self.get(pattern.id)
        if existing is not None:
            raise ValueError(f"Pattern with ID {pattern.id} already exists")

        self.db.execute(
            """
            INSERT INTO patterns (
                id, name, pattern_type, description, confidence,
                occurrence_count, source_id, approval_status,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                pattern.id,
                pattern.name,
                pattern.pattern_type.value,
                pattern.description,
                pattern.confidence,
                pattern.occurrence_count,
                pattern.source_id,
                pattern.approval_status,
                pattern.created_at,
                pattern.updated_at,
            ),
        )
        return pattern

    def get(self, pattern_id: str) -> PatternEntity | None:
        """Retrieve a pattern by its ID.

        Args:
            pattern_id: The unique identifier of the pattern

        Returns:
            The pattern if found, None otherwise
        """
        cursor = self.db.execute(
            "SELECT * FROM patterns WHERE id = ?",
            (pattern_id,),
        )
        row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_pattern(row)

    def update(self, pattern: PatternEntity) -> PatternEntity:
        """Update an existing pattern in the database.

        Args:
            pattern: The pattern with updated values

        Returns:
            The updated pattern

        Raises:
            ValueError: If the pattern does not exist
        """
        existing = self.get(pattern.id)
        if existing is None:
            raise ValueError(f"Pattern with ID {pattern.id} not found")

        # Update the updated_at timestamp
        pattern.touch()

        self.db.execute(
            """
            UPDATE patterns SET
                name = ?,
                pattern_type = ?,
                description = ?,
                confidence = ?,
                occurrence_count = ?,
                source_id = ?,
                approval_status = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                pattern.name,
                pattern.pattern_type.value,
                pattern.description,
                pattern.confidence,
                pattern.occurrence_count,
                pattern.source_id,
                pattern.approval_status,
                pattern.updated_at,
                pattern.id,
            ),
        )
        return pattern

    def delete(self, pattern_id: str) -> bool:
        """Delete a pattern and its occurrences.

        Also deletes all pattern occurrences linked to this pattern
        to maintain referential integrity.

        Args:
            pattern_id: The ID of the pattern to delete

        Returns:
            True if the pattern was deleted, False if it didn't exist
        """
        # Delete occurrences first
        self.db.execute(
            "DELETE FROM pattern_occurrences WHERE pattern_id = ?",
            (pattern_id,),
        )

        # Delete relationships
        self.db.execute(
            "DELETE FROM pattern_relationships WHERE source_pattern_id = ? OR target_pattern_id = ?",
            (pattern_id, pattern_id),
        )

        cursor = self.db.execute(
            "DELETE FROM patterns WHERE id = ?",
            (pattern_id,),
        )
        return cursor.rowcount > 0

    def list_by_type(self, pattern_type: PatternType) -> list[PatternEntity]:
        """List all patterns of a specific type.

        Args:
            pattern_type: The type to filter by

        Returns:
            List of patterns matching the type
        """
        cursor = self.db.execute(
            """
            SELECT * FROM patterns
            WHERE pattern_type = ?
            ORDER BY confidence DESC, occurrence_count DESC
            """,
            (pattern_type.value,),
        )

        return [self._row_to_pattern(row) for row in cursor.fetchall()]

    def list_by_source(self, source_id: str) -> list[PatternEntity]:
        """List all patterns derived from a specific source.

        Args:
            source_id: The source ID to filter by

        Returns:
            List of patterns that came from this source
        """
        cursor = self.db.execute(
            """
            SELECT * FROM patterns
            WHERE source_id = ?
            ORDER BY created_at DESC
            """,
            (source_id,),
        )

        return [self._row_to_pattern(row) for row in cursor.fetchall()]

    def list_all(self, limit: int = 100, offset: int = 0) -> list[PatternEntity]:
        """List all patterns with pagination.

        Args:
            limit: Maximum number of patterns to return
            offset: Number of patterns to skip

        Returns:
            List of patterns
        """
        cursor = self.db.execute(
            """
            SELECT * FROM patterns
            ORDER BY confidence DESC, occurrence_count DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )

        return [self._row_to_pattern(row) for row in cursor.fetchall()]

    def list_occurrences(self, pattern_id: str) -> list[PatternOccurrence]:
        """List all occurrences of a pattern.

        Args:
            pattern_id: The pattern ID to get occurrences for

        Returns:
            List of occurrences for the pattern
        """
        cursor = self.db.execute(
            """
            SELECT * FROM pattern_occurrences
            WHERE pattern_id = ?
            ORDER BY detected_at DESC
            """,
            (pattern_id,),
        )

        return [self._row_to_occurrence(row) for row in cursor.fetchall()]

    def create_occurrence(self, occurrence: PatternOccurrence) -> PatternOccurrence:
        """Store a pattern occurrence.

        Args:
            occurrence: The occurrence to store

        Returns:
            The stored occurrence
        """
        self.db.execute(
            """
            INSERT INTO pattern_occurrences (
                pattern_id, memory_id, evidence, detected_at
            ) VALUES (?, ?, ?, ?)
            """,
            (
                occurrence.pattern_id,
                occurrence.memory_id,
                occurrence.evidence,
                occurrence.detected_at,
            ),
        )
        return occurrence

    def count(self) -> int:
        """Count total number of patterns.

        Returns:
            Number of patterns in the database
        """
        cursor = self.db.execute("SELECT COUNT(*) FROM patterns")
        return int(cursor.fetchone()[0])

    def _row_to_pattern(self, row: Any) -> PatternEntity:
        """Convert a database row to a PatternEntity object.

        Args:
            row: SQLite row from the database

        Returns:
            PatternEntity instance
        """
        return PatternEntity(
            id=row["id"],
            name=row["name"],
            pattern_type=PatternType(row["pattern_type"]),
            description=row["description"],
            confidence=row["confidence"],
            occurrence_count=row["occurrence_count"],
            source_id=row["source_id"],
            approval_status=row["approval_status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def _row_to_occurrence(self, row: Any) -> PatternOccurrence:
        """Convert a database row to a PatternOccurrence object.

        Args:
            row: SQLite row from the database

        Returns:
            PatternOccurrence instance
        """
        return PatternOccurrence(
            pattern_id=row["pattern_id"],
            memory_id=row["memory_id"],
            evidence=row["evidence"],
            detected_at=row["detected_at"],
        )
