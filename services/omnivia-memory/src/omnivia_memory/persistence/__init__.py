"""SQLite persistence layer."""

from omnivia_memory.persistence.database import Database, get_database

# Note: MemoryRepository is exported from persistence.repositories directly,
# not from this package to avoid circular imports with memory module.

__all__ = ["Database", "get_database"]
