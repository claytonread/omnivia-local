"""Pattern detection module for OmniVia.

Analyzes stored memories to identify recurring patterns by:
- Content similarity (similar knowledge being stored multiple times)
- Source patterns (same source generating multiple related memories)
- Lifecycle transitions (common approval/rejection paths)

Patterns help agents understand:
- What knowledge is frequently referenced
- Which sources are authoritative vs unreliable
- Common knowledge approval workflows
"""

from omnivia_memory.pattern.models import (
    PatternType,
    PatternEntity,
    PatternRelationship,
    PatternOccurrence,
    PatternCreate,
)
from omnivia_memory.pattern.service import PatternService, PatternServiceError

__all__ = [
    "PatternType",
    "PatternEntity",
    "PatternRelationship",
    "PatternOccurrence",
    "PatternCreate",
    "PatternService",
    "PatternServiceError",
]
