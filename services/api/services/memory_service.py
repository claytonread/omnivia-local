from sqlalchemy.orm import Session
from services.api.database import Memory
from services.api.services.embedding import EmbeddingService
from services.api.services.vector_store import VectorStore
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)


class MemoryService:
    """Service for managing memories with vector embeddings.

    Memories are the core unit of knowledge in OmniVia. Each memory has:
    - Text content that gets embedded for semantic search
    - An approval status that controls visibility and trust
    - Provenance via optional source reference

    The approval status lifecycle:
    - proposed: AI-created, requires human review
    - observed: Human-created or AI-approved, visible to agents
    - approved: Verified, trusted knowledge
    """

    def __init__(
        self,
        db: Session,
        embedding_service: EmbeddingService,
        vector_store: VectorStore
    ):
        self.db = db
        self.embedding = embedding_service
        self.vector_store = vector_store

    def create_memory(
        self,
        content: str,
        source: str = None,
        memory_type: str = "general",
        created_by: str = "human"
    ) -> Memory:
        """Create a new memory with vector embedding.

        Agent-created memories default to 'proposed' status so AI cannot
        silently turn unverified observations into approved business truth.
        Human-created memories default to 'observed' as the human is assumed
        to be a trusted source.
        """
        # Agent-created memories default to proposed; human to observed
        approval_status = "observed" if created_by == "human" else "proposed"

        # Generate embedding for semantic search
        vector = self.embedding.embed_text(content)

        # Create memory record in SQLite
        memory = Memory(
            id=str(uuid.uuid4()),
            content=content,
            source=source,
            memory_type=memory_type,
            approval_status=approval_status,
            created_by=created_by,
            created_at=datetime.utcnow()
        )

        # Also store in Qdrant vector store for semantic search
        # The metadata tracks approval_status so we can filter at query time
        metadata = {
            "memory_id": memory.id,
            "content": content,
            "approval_status": approval_status,
            "memory_type": memory_type,
            "created_by": created_by,
            "created_at": memory.created_at.isoformat()
        }
        embedding_id = self.vector_store.upsert(content, vector, metadata)
        memory.embedding_id = embedding_id

        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)

        logger.info(f"Created memory {memory.id} with status {approval_status}")
        return memory

    def search_memories(
        self,
        query: str,
        limit: int = 5,
        approval_status: str = None
    ) -> list:
        """Search memories semantically using natural language query.

        Uses vector similarity search via Qdrant, then filters by approval_status
        if specified. We fetch extra results to account for filtering.
        """
        # Search Qdrant for similar vectors
        # Fetch limit * 2 because filtering by approval_status may remove results
        results = self.vector_store.search_by_text(
            query, self.embedding, limit=limit * 2
        )

        # Get memory IDs from Qdrant results
        memory_ids = [r["payload"]["memory_id"] for r in results]
        if not memory_ids:
            return []

        memories = self.db.query(Memory).filter(Memory.id.in_(memory_ids)).all()

        # Apply approval status filter if specified
        if approval_status:
            memories = [m for m in memories if m.approval_status == approval_status]

        # Maintain Qdrant's relevance ordering after DB filtering
        id_to_memory = {m.id: m for m in memories}
        ordered_memories = [
            id_to_memory[mid] for mid in memory_ids if mid in id_to_memory
        ]

        return ordered_memories[:limit]

    def get_memory(self, memory_id: str) -> Memory:
        """Get a specific memory by ID."""
        return self.db.query(Memory).filter(Memory.id == memory_id).first()

    def get_all_memories(
        self,
        limit: int = 100,
        approval_status: str = None
    ) -> list:
        """Get all memories, optionally filtered by approval status."""
        query = self.db.query(Memory)
        if approval_status:
            query = query.filter(Memory.approval_status == approval_status)
        return query.order_by(Memory.created_at.desc()).limit(limit).all()

    def update_approval_status(
        self, memory_id: str, new_status: str
    ) -> Memory:
        """Update the approval status of a memory.

        Valid transitions:
        - proposed -> observed (AI memory reviewed by human)
        - observed -> approved (human confirms memory is correct)
        - approved -> observed (can be downgraded if facts change)
        """
        memory = self.get_memory(memory_id)
        if not memory:
            return None

        old_status = memory.approval_status
        memory.approval_status = new_status
        self.db.commit()
        self.db.refresh(memory)

        logger.info(f"Updated memory {memory_id} status: {old_status} -> {new_status}")
        return memory