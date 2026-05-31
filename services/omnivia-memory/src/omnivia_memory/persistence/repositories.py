"""Memory repository for SQLite persistence.

Provides CRUD operations for memories with full lifecycle and provenance support.
"""

from __future__ import annotations

from typing import Any

from omnivia_memory.lifecycle.models import LifecycleState
from omnivia_memory.lifecycle.rules import CreatedBy
from omnivia_memory.memory.models import Memory
from omnivia_memory.persistence.database import Database
from omnivia_memory.provenance.models import Source, SourceType


class MemoryRepository:
    """Repository for persisting and retrieving memories from SQLite.

    Handles all database operations for memories, including:
    - Create, read, update, delete operations
    - Lifecycle state management
    - Keyword search

    Attributes:
        db: The database connection to use
    """

    def __init__(self, db: Database) -> None:
        self.db = db

    def create(self, memory: Memory) -> Memory:
        """Store a new memory in the database.

        Args:
            memory: The memory to store

        Returns:
            The stored memory (same object, persisted)

        Raises:
            ValueError: If a memory with the same ID already exists
        """
        # Check for existing memory with same ID
        existing = self.get_by_id(memory.id)
        if existing is not None:
            raise ValueError(f"Memory with ID {memory.id} already exists")

        self.db.execute(
            """
            INSERT INTO memories (
                id, content, source_type, source_reference, source_description,
                lifecycle_state, memory_type, created_by, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                memory.id,
                memory.content,
                memory.source.type.value,
                memory.source.reference,
                memory.source.description,
                memory.lifecycle_state.value,
                memory.memory_type,
                memory.created_by.value,
                memory.created_at,
                memory.updated_at,
            ),
        )
        return memory

    def get_by_id(self, memory_id: str) -> Memory | None:
        """Retrieve a memory by its ID.

        Args:
            memory_id: The unique identifier of the memory

        Returns:
            The memory if found, None otherwise
        """
        cursor = self.db.execute(
            "SELECT * FROM memories WHERE id = ?",
            (memory_id,),
        )
        row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_memory(row)

    def list_all(
        self,
        limit: int = 100,
        offset: int = 0,
        lifecycle_state: LifecycleState | None = None,
    ) -> list[Memory]:
        """List all memories, optionally filtered by lifecycle state.

        Args:
            limit: Maximum number of memories to return
            offset: Number of memories to skip
            lifecycle_state: Optional filter by lifecycle state

        Returns:
            List of memories matching the criteria
        """
        if lifecycle_state is not None:
            cursor = self.db.execute(
                """
                SELECT * FROM memories
                WHERE lifecycle_state = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (lifecycle_state.value, limit, offset),
            )
        else:
            cursor = self.db.execute(
                """
                SELECT * FROM memories
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            )

        return [self._row_to_memory(row) for row in cursor.fetchall()]

    def update(self, memory: Memory) -> Memory:
        """Update an existing memory in the database.

        Args:
            memory: The memory with updated values

        Returns:
            The updated memory

        Raises:
            ValueError: If the memory does not exist
        """
        existing = self.get_by_id(memory.id)
        if existing is None:
            raise ValueError(f"Memory with ID {memory.id} not found")

        self.db.execute(
            """
            UPDATE memories SET
                content = ?,
                source_type = ?,
                source_reference = ?,
                source_description = ?,
                lifecycle_state = ?,
                memory_type = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                memory.content,
                memory.source.type.value,
                memory.source.reference,
                memory.source.description,
                memory.lifecycle_state.value,
                memory.memory_type,
                memory.updated_at,
                memory.id,
            ),
        )
        return memory

    def delete(self, memory_id: str) -> bool:
        """Delete a memory from the database.

        Args:
            memory_id: The ID of the memory to delete

        Returns:
            True if the memory was deleted, False if it didn't exist
        """
        cursor = self.db.execute(
            "DELETE FROM memories WHERE id = ?",
            (memory_id,),
        )
        return cursor.rowcount > 0

    def search(self, query: str, limit: int = 20) -> list[Memory]:
        """Search memories by keyword.

        Uses SQLite LIKE for simple keyword matching. Phase 1 uses this
        approach; vector search will be added in a later phase.

        Args:
            query: Search query (matched against content)
            limit: Maximum number of results to return

        Returns:
            List of memories containing the query in their content
        """
        # Escape special LIKE characters and add wildcards for partial matching
        escaped_query = query.replace("%", "\\%").replace("_", "\\_")
        pattern = f"%{escaped_query}%"

        cursor = self.db.execute(
            """
            SELECT * FROM memories
            WHERE content LIKE ? ESCAPE '\\'
            ORDER BY
                CASE
                    WHEN content LIKE ? THEN 0
                    ELSE 1
                END,
                updated_at DESC
            LIMIT ?
            """,
            (pattern, f"%{query}%", limit),
        )

        return [self._row_to_memory(row) for row in cursor.fetchall()]

    def count(self, lifecycle_state: LifecycleState | None = None) -> int:
        """Count memories, optionally filtered by lifecycle state.

        Args:
            lifecycle_state: Optional filter by lifecycle state

        Returns:
            Number of memories matching the criteria
        """
        if lifecycle_state is not None:
            cursor = self.db.execute(
                "SELECT COUNT(*) FROM memories WHERE lifecycle_state = ?",
                (lifecycle_state.value,),
            )
        else:
            cursor = self.db.execute("SELECT COUNT(*) FROM memories")

        return int(cursor.fetchone()[0])

    def _row_to_memory(self, row: Any) -> Memory:
        """Convert a database row to a Memory object.

        Args:
            row: SQLite row from the database

        Returns:
            Memory instance
        """
        return Memory(
            id=row["id"],
            content=row["content"],
            source=Source(
                type=SourceType(row["source_type"]),
                reference=row["source_reference"],
                description=row["source_description"],
            ),
            lifecycle_state=LifecycleState(row["lifecycle_state"]),
            memory_type=row["memory_type"],
            created_by=CreatedBy(row["created_by"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
