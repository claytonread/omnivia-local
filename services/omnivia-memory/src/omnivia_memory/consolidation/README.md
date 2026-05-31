# Knowledge Consolidation Module

Provides tools for aggregating related memories into consolidated knowledge units and detecting conflicts between memories on the same topic.

## Overview

The consolidation module helps AI coding agents synthesize related memories into coherent knowledge units while surfacing contradictions for human review. This enables agents to:

1. **Aggregate related memories** into knowledge units by topic, source, or decision context
2. **Detect conflicts** between memories that assert different states on the same topic
3. **Get consolidated views** of knowledge on a topic with conflict information

## Models

### KnowledgeUnit

A synthesized view of related memories on a topic. Preserves provenance by referencing original memories.

```python
from omnivia_memory.consolidation.models import KnowledgeUnit, ConsolidationStrategy

unit = KnowledgeUnit(
    topic="authentication",
    summary="JWT-based authentication pattern",
    consolidation_strategy=ConsolidationStrategy.TOPIC,
    confidence_score=0.8,
)
```

### MemoryConflict

A detected conflict between memories on the same topic. Surfaces contradictions for human review.

```python
from omnivia_memory.consolidation.models import MemoryConflict, ConflictSeverity

conflict = MemoryConflict(
    topic="security",
    severity=ConflictSeverity.HIGH,
    conflict_description="Contradictory security settings",
)
```

### MemoryRef

A reference to an original memory within a knowledge unit. Tracks provenance.

```python
from omnivia_memory.consolidation.models import MemoryRef

ref = MemoryRef(
    memory_id="abc-123",
    memory_content="Use JWT tokens for authentication",
    source_reference="auth.py",
    created_at="2026-06-01T00:00:00Z",
)
```

## Consolidation Strategies

Three strategies for grouping memories:

| Strategy | Description | Use Case |
|----------|-------------|----------|
| `topic` | Group by subject/theme | "What do we know about authentication?" |
| `source` | Group by origin file or ADR | "What did we learn from ADR-0042?" |
| `decision` | Group by decision context | "What decisions have we made about caching?" |

## Conflict Severity Levels

| Severity | Meaning | Example |
|----------|---------|---------|
| `high` | Direct contradiction | "We approve requests" vs "We reject requests" |
| `medium` | Partial disagreement | Different emphasis or perspective |
| `low` | Minor wording differences | Same meaning, different phrasing |

## Service Usage

### Python API

```python
from omnivia_memory.consolidation import ConsolidationService
from omnivia_memory.persistence.repositories import MemoryRepository
from omnivia_memory.persistence.database import Database, DatabaseConfig

# Create service with repository
db = Database(DatabaseConfig(db_path="~/.omnivia/memories.db"))
db.connect()
repo = MemoryRepository(db)
service = ConsolidationService(repository=repo)

# Consolidate memories by topic
units = service.consolidate_by_topic(topic="authentication", limit=50)

# Consolidate memories by source
units = service.consolidate_by_source(source_reference="auth.py")

# Consolidate decision-related memories
units = service.consolidate_by_decision(decision_id="auth-strategy")

# Get a specific knowledge unit
unit = service.get_knowledge_unit("unit-id-123")

# List all knowledge units
units = service.list_knowledge_units(strategy="topic", limit=20)

# Detect conflicts between memories
conflicts = service.detect_conflicts(topic="security")

# Get comprehensive consolidated view
view = service.get_consolidated_view("authentication", include_conflicts=True)

# Resolve a detected conflict
conflict = service.resolve_conflict("conflict-id", "Resolution: Standardized on JWT")

# Get statistics
stats = service.get_stats()
# Returns: {total_knowledge_units, by_strategy, total_conflicts, unresolved_conflicts, ...}
```

### MCP Tools

Agents interact with consolidation through MCP tools over stdio transport.

#### consolidate_knowledge

Consolidate related memories into knowledge units.

```json
{
  "name": "consolidate_knowledge",
  "arguments": {
    "topic": "authentication",
    "memory_type": "decision",
    "strategy": "topic",
    "limit": 50
  }
}
```

Response:
```json
{
  "units_created": 2,
  "knowledge_units": [
    {
      "id": "unit-uuid",
      "topic": "decision/authentication",
      "summary": "Use JWT tokens | Stateless authentication",
      "consolidation_strategy": "topic",
      "confidence_score": 0.7,
      "memory_refs": [...]
    }
  ]
}
```

#### get_knowledge_unit

Retrieve a specific knowledge unit by ID.

```json
{
  "name": "get_knowledge_unit",
  "arguments": {
    "unit_id": "unit-uuid"
  }
}
```

#### list_knowledge_units

List consolidated knowledge units with optional filtering.

```json
{
  "name": "list_knowledge_units",
  "arguments": {
    "strategy": "topic",
    "limit": 20
  }
}
```

#### detect_conflicts

Detect conflicts between memories on the same topic.

```json
{
  "name": "detect_conflicts",
  "arguments": {
    "topic": "security",
    "memory_type": "general",
    "severity": "high"
  }
}
```

Response:
```json
{
  "conflicts_found": 1,
  "conflicts": [
    {
      "id": "conflict-uuid",
      "topic": "security",
      "severity": "high",
      "memory_refs": [
        {"memory_id": "...", "memory_content": "We approve all requests..."},
        {"memory_id": "...", "memory_content": "We reject all requests..."}
      ],
      "conflict_description": "Memories appear to conflict on topic: security",
      "resolution_status": "unresolved"
    }
  ]
}
```

#### get_consolidated_view

Get a comprehensive view of knowledge on a topic including conflicts.

```json
{
  "name": "get_consolidated_view",
  "arguments": {
    "topic": "authentication",
    "include_conflicts": true
  }
}
```

Response:
```json
{
  "topic": "authentication",
  "knowledge_units": [...],
  "conflicts": [...],
  "summary": "Found 2 knowledge unit(s) covering 5 memory(s).",
  "total_memories": 5,
  "conflict_count": 1
}
```

#### resolve_conflict

Mark a detected conflict as resolved.

```json
{
  "name": "resolve_conflict",
  "arguments": {
    "conflict_id": "conflict-uuid",
    "resolution": "Standardized on JWT after reviewing both proposals"
  }
}
```

## Conflict Detection

The service detects conflicts by analyzing:

1. **Negation patterns** - "X is Y" vs "X is not Y"
2. **State change indicators** - "changed from X to Y" vs "still using X"
3. **Opposite actions** - "approve" vs "reject"

Conflicts are surfaced for human review rather than auto-resolved, following OmniVia's governance model.

## Confidence Scoring

Knowledge units receive confidence scores based on:

- Number of supporting memories
- Agreement between memories
- Source reliability

Scores range from 0.0 (no confidence) to 1.0 (high confidence).

## Example Workflow

1. **Agent stores memories** during code analysis
2. **Consolidation runs** to group related memories into units
3. **Conflict detection** surfaces contradictions
4. **Human reviews** conflicts and approves/rejects
5. **Consolidated view** provides synthesized knowledge for future tasks

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| `KnowledgeUnitNotFoundError` | Unit ID does not exist | Check unit list first |
| `ConsolidationServiceError` | Conflict ID not found | Verify conflict exists |

## Related Documentation

- [OmniVia Dev Task List](../../../../docs/tasks/omnivia-dev-tasklist.md)
- [Memory Models](../memory/models.py)
- [MCP Server](../mcp/server.py)