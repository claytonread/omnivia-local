# Pattern Detection Module

Provides tools for detecting recurring patterns in stored memories and the knowledge graph. Patterns are themselves knowledge that can be stored, approved, and queried.

## Overview

The pattern module analyzes stored memories to identify recurring knowledge patterns across:

1. **Content similarity** - Similar knowledge appearing in multiple memories
2. **Source clusters** - The same source generating multiple related memories
3. **Lifecycle transitions** - Common state change paths (proposed -> approved)

Detected patterns are stored in "proposed" state for human review before they influence agent reasoning, following OmniVia's governance model.

## Pattern Types

| Type | Description | Example |
|------|-------------|---------|
| `content_similarity` | Multiple memories contain similar knowledge | "Logging decisions appear in 3 different files" |
| `source_cluster` | Same source generates multiple related memories | "docs/ folder generates 10+ task memories" |
| `lifecycle_transition` | Common state change paths | "Agents always create proposed memories" |
| `concept_reference` | Same concept mentioned across different memories | "JWT mentioned in auth and security contexts" |
| `decision_recurrence` | Similar decisions being made repeatedly | "Multiple services choosing PostgreSQL" |

## Models

### PatternEntity

A detected pattern in the knowledge graph.

```python
from omnivia_memory.pattern.models import PatternEntity, PatternType

pattern = PatternEntity(
    name="Similar content: authentication JWT",
    pattern_type=PatternType.CONTENT_SIMILARITY,
    description="Found 3 memories with similar authentication content",
    confidence=0.85,
    occurrence_count=3,
)
```

### PatternOccurrence

An occurrence linking a pattern to the memory that triggered its detection.

```python
from omnivia_memory.pattern.models import PatternOccurrence

occurrence = PatternOccurrence(
    pattern_id="pattern-uuid",
    memory_id="memory-uuid",
    evidence="Matched on keywords: JWT, authentication, token",
)
```

### PatternRelationship

A relationship between patterns or between a pattern and a memory.

```python
from omnivia_memory.pattern.models import PatternRelationship

rel = PatternRelationship(
    source_pattern_id="pattern-a",
    target_pattern_id="pattern-b",
    relationship_type="specializes",
)
```

## Service Usage

### Python API

```python
from omnivia_memory.pattern import PatternService, PatternType
from omnivia_memory.pattern.repository import PatternRepository
from omnivia_memory.memory.service import MemoryService
from omnivia_memory.persistence.repositories import MemoryRepository
from omnivia_memory.persistence.database import Database, DatabaseConfig

# Create services
db = Database(DatabaseConfig(db_path="~/.omnivia/memories.db"))
db.connect()
memory_repo = MemoryRepository(db)
memory_service = MemoryService(repository=memory_repo)
pattern_repo = PatternRepository(db)
service = PatternService(pattern_repository=pattern_repo, memory_service=memory_service)

# Detect patterns in all memories
memories = memory_service.list(limit=1000)
patterns = service.detect_all_patterns(memories, min_occurrences=2)

# Get a specific pattern
pattern = service.get_pattern("pattern-id-123")

# List all patterns
patterns = service.list_patterns(pattern_type=PatternType.CONTENT_SIMILARITY, limit=100)

# Get occurrences of a pattern
occurrences = service.get_pattern_occurrences("pattern-id-123")

# Approve a pattern
approved = service.approve_pattern("pattern-id-123")

# Reject a pattern
rejected = service.reject_pattern("pattern-id-123")

# Delete a pattern
deleted = service.delete_pattern("pattern-id-123")
```

### MCP Tools

Agents interact with pattern detection through MCP tools over stdio transport.

#### pattern_detect

Detect patterns in stored memories.

```json
{
  "name": "pattern_detect",
  "arguments": {
    "min_occurrences": 2
  }
}
```

Response:
```json
{
  "patterns_detected": 5,
  "patterns": [
    {
      "id": "pattern-uuid",
      "name": "Source cluster: auth.py",
      "pattern_type": "source_cluster",
      "description": "Source 'auth.py' generated 4 memories...",
      "confidence": 0.8,
      "occurrence_count": 4,
      "approval_status": "proposed"
    }
  ]
}
```

#### pattern_list

List detected patterns with optional filtering.

```json
{
  "name": "pattern_list",
  "arguments": {
    "pattern_type": "content_similarity",
    "limit": 100,
    "offset": 0
  }
}
```

#### pattern_get

Retrieve a specific pattern by ID.

```json
{
  "name": "pattern_get",
  "arguments": {
    "pattern_id": "pattern-uuid"
  }
}
```

#### pattern_get_occurrences

Get all occurrences of a pattern showing which memories triggered detection.

```json
{
  "name": "pattern_get_occurrences",
  "arguments": {
    "pattern_id": "pattern-uuid"
  }
}
```

Response:
```json
[
  {
    "pattern_id": "pattern-uuid",
    "memory_id": "memory-uuid",
    "evidence": "Similarity score: 0.85",
    "detected_at": "2026-06-01T00:00:00Z"
  }
]
```

#### pattern_approve

Approve a pattern, moving it from 'proposed' to 'approved'.

```json
{
  "name": "pattern_approve",
  "arguments": {
    "pattern_id": "pattern-uuid"
  }
}
```

#### pattern_reject

Reject a pattern, moving it to 'rejected' state.

```json
{
  "name": "pattern_reject",
  "arguments": {
    "pattern_id": "pattern-uuid"
  }
}
```

## Detection Algorithms

### Content Similarity

Uses sequence matching to find memories with similar content. Memories with similarity >= 70% are grouped together.

```python
# Internal algorithm
similarity = SequenceMatcher(None, norm_text1, norm_text2).ratio()
if similarity >= 0.7:
    # Group into pattern
```

### Source Clusters

Groups memories by source reference. Sources generating multiple memories indicate consistent knowledge capture patterns.

### Lifecycle Transitions

Analyzes how memories move between lifecycle states, identifying common paths like "agent creates proposed" or "human creates approved".

## Confidence Scoring

Patterns receive confidence scores based on:

- Number of supporting occurrences
- Strength of content similarity
- Consistency of source generation

Scores range from 0.0 (no confidence) to 1.0 (high confidence).

## Approval Workflow

1. **Detection** - Patterns are detected with `proposed` status
2. **Review** - Human reviews the pattern description and occurrences
3. **Approval/Rejection** - Pattern is approved or rejected via MCP tool
4. **Usage** - Approved patterns can influence agent reasoning

## Example Workflow

1. **Agent stores memories** during code analysis
2. **Pattern detection runs** - analyzes stored memories
3. **Patterns created** - in proposed state with confidence scores
4. **Human reviews** - approves or rejects detected patterns
5. **Approved patterns inform future decisions** - agents query approved patterns

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| `PatternNotFoundError` | Pattern ID does not exist | Check pattern list first |
| `PatternValidationError` | Invalid state transition | Review current status |
| `PatternServiceError` | Repository not configured | Check service initialization |

## Related Documentation

- [Knowledge Consolidation Module](../consolidation/README.md)
- [Memory Models](../memory/models.py)
- [MCP Server](../mcp/server.py)