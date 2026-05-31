"""Knowledge consolidation module for OmniVia.

Provides tools for aggregating related memories into consolidated knowledge
units and detecting conflicts between memories on the same topic.

Example usage:
    from omnivia_memory.consolidation import ConsolidationService

    service = ConsolidationService(repository=memory_repo)

    # Consolidate memories by topic
    units = service.consolidate_by_topic(topic="authentication")

    # Detect conflicts
    conflicts = service.detect_conflicts(topic="database")

    # Get consolidated view
    view = service.get_consolidated_view("security")
"""

from omnivia_memory.consolidation.models import (
    ConflictSeverity,
    ConsolidationStrategy,
    KnowledgeUnit,
    MemoryConflict,
    MemoryRef,
    extract_topic_keywords,
)
from omnivia_memory.consolidation.service import (
    ConsolidationService,
    ConsolidationServiceError,
    KnowledgeUnitNotFoundError,
)

__all__ = [
    # Models
    "ConflictSeverity",
    "ConsolidationStrategy",
    "KnowledgeUnit",
    "MemoryConflict",
    "MemoryRef",
    "extract_topic_keywords",
    # Service
    "ConsolidationService",
    "ConsolidationServiceError",
    "KnowledgeUnitNotFoundError",
]
