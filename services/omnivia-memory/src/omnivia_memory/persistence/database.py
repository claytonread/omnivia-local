"""SQLite database connection and schema management.

Provides a simple, portable SQLite-backed persistence layer for memories.
The database file is stored in the user's data directory.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Generator


@dataclass
class DatabaseConfig:
    """Configuration for the SQLite database.

    Attributes:
        db_path: Path to the SQLite database file
        auto_commit: Whether to auto-commit transactions (default True)
    """

    db_path: Path
    auto_commit: bool = True


class Database:
    """SQLite database wrapper for OmniVia memory storage.

    Provides connection management, schema initialization, and basic
    transaction support. Thread-safe for read operations.

    Attributes:
        config: Database configuration
    """

    def __init__(self, config: DatabaseConfig) -> None:
        self.config = config
        self._connection: sqlite3.Connection | None = None

    def connect(self) -> None:
        """Establish connection to the database.

        Creates the database file and schema if they don't exist.
        """
        # Ensure parent directory exists
        self.config.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._connection = sqlite3.connect(
            str(self.config.db_path),
            check_same_thread=False,
        )
        self._connection.row_factory = sqlite3.Row
        self._init_schema()

    def close(self) -> None:
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

    @property
    def connection(self) -> sqlite3.Connection:
        """Get the database connection.

        Raises:
            RuntimeError: If not connected
        """
        if self._connection is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._connection

    def _init_schema(self) -> None:
        """Initialize the database schema.

        Creates the memories table and any other required tables.
        """
        cursor = self.connection.cursor()

        # Create memories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                source_type TEXT NOT NULL,
                source_reference TEXT NOT NULL,
                source_description TEXT,
                lifecycle_state TEXT NOT NULL DEFAULT 'proposed',
                memory_type TEXT NOT NULL DEFAULT 'general',
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Create indexes for common queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_lifecycle
            ON memories(lifecycle_state)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_created_at
            ON memories(created_at)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_type
            ON memories(memory_type)
        """)

        if self.config.auto_commit:
            self.connection.commit()

    def execute(
        self,
        query: str,
        params: tuple[Any, ...] | dict[str, Any] | None = None,
    ) -> sqlite3.Cursor:
        """Execute a SQL query.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Cursor with query results
        """
        cursor = self.connection.cursor()
        cursor.execute(query, params or ())
        if self.config.auto_commit:
            self.connection.commit()
        return cursor

    def executemany(
        self,
        query: str,
        params: list[tuple[Any, ...]],
    ) -> sqlite3.Cursor:
        """Execute a SQL query with multiple parameter sets.

        Args:
            query: SQL query string
            params: List of parameter tuples

        Returns:
            Cursor with query results
        """
        cursor = self.connection.cursor()
        cursor.executemany(query, params)
        if self.config.auto_commit:
            self.connection.commit()
        return cursor

    def commit(self) -> None:
        """Commit the current transaction."""
        self.connection.commit()

    def rollback(self) -> None:
        """Rollback the current transaction."""
        self.connection.rollback()

    @contextmanager
    def transaction(self) -> Generator[None, None, None]:
        """Context manager for explicit transactions.

        Usage:
            with db.transaction():
                db.execute("INSERT INTO ...", params)
                db.execute("UPDATE ...", params)
        """
        try:
            yield
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise


# Global database instance for convenience
_global_db: Database | None = None


def get_database(db_path: Path | str | None = None) -> Database:
    """Get or create the global database instance.

    Args:
        db_path: Optional path to the database file.
                 Defaults to ~/.omnivia/memories.db

    Returns:
        The global Database instance
    """
    global _global_db

    if _global_db is None:
        if db_path is None:
            # Default to ~/.omnivia/memories.db
            home = Path.home()
            db_dir = home / ".omnivia"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / "memories.db"

        config = DatabaseConfig(db_path=Path(db_path))
        _global_db = Database(config)
        _global_db.connect()

    return _global_db


def reset_database() -> None:
    """Reset the global database instance.

    Useful for testing or when switching to a different database.
    """
    global _global_db

    if _global_db is not None:
        _global_db.close()
        _global_db = None
