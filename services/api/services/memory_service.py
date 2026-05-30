from sqlalchemy.orm import Session
from services.api.database import Memory
from services.api.services.embedding import EmbeddingService
from services.api.services.vector_store import VectorStore
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)


class MemoryService:
    """Service for managing memories with embeddings."""

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
        """Create a new memory with embedding.

        Agent-created memories default to 'proposed' status.
        Human-created memories default to 'observed' status.
        """
        # Agent-created memories default to proposed; human to observed
        approval_status = "observed" if created_by == "human" else "proposed"

        # Generate embedding
        vector = self.embedding.embed_text(content)

        # Create memory record
        memory = Memory(
            id=str(uuid.uuid4()),
            content=content,
            source=source,
            memory_type=memory_type,
            approval_status=approval_status,
            created_by=created_by,
            created_at=datetime.utcnow()
        )

        # Store in vector store
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
        """Search memories semantically."""
        # Search Qdrant for similar vectors
        results = self.vector_store.search_by_text(
            query, self.embedding, limit=limit * 2  # Fetch extra to account for filtering
        )

        # Get memory IDs and filter
        memory_ids = [r["payload"]["memory_id"] for r in results]
        if not memory_ids:
            return []

        memories = self.db.query(Memory).filter(Memory.id.in_(memory_ids)).all()

        # Apply approval status filter if specified
        if approval_status:
            memories = [m for m in memories if m.approval_status == approval_status]

        # Sort by Qdrant score order
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
        """Update the approval status of a memory."""
        memory = self.get_memory(memory_id)
        if not memory:
            return None

        old_status = memory.approval_status
        memory.approval_status = new_status
        self.db.commit()
        self.db.refresh(memory)

        logger.info(f"Updated memory {memory_id} status: {old_status} -> {new_status}")
        return memory