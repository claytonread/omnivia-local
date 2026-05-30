import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from services.api.database import Base, init_db, get_engine
from services.api.models import MemoryCreate, Memory
from services.api.services.memory_service import MemoryService
from services.api.services.embedding import EmbeddingService
from services.api.services.vector_store import VectorStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration from environment
DB_PATH = os.getenv("OMNIVIA_DB_PATH", "/data/omnivia.sqlite")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

# Global service instances (initialized on startup)
embedding_service: Optional[EmbeddingService] = None
vector_store: Optional[VectorStore] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    global embedding_service, vector_store
    logger.info("Starting OmniVia API...")

    # Startup: Initialize services
    engine = get_engine(DB_PATH)
    init_db(engine)
    logger.info(f"Database initialized at {DB_PATH}")

    embedding_service = EmbeddingService()
    logger.info(f"Embedding service initialized with model: {embedding_service.model_name}")

    vector_store = VectorStore(QDRANT_URL)
    logger.info(f"Vector store connected to {QDRANT_URL}")

    logger.info("OmniVia API started successfully")
    yield

    # Shutdown
    logger.info("Shutting down OmniVia API...")


app = FastAPI(
    title="OmniVia API",
    description="Local-first AI memory layer for agents",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    """Dependency for database sessions."""
    engine = get_engine(DB_PATH)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_memory_service(db: Session = Depends(get_db)) -> MemoryService:
    """Dependency for memory service."""
    return MemoryService(db, embedding_service, vector_store)


@app.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "omnivia-api",
        "version": "0.1.0"
    }


@app.post("/memories", response_model=Memory, status_code=201)
def create_memory(
    memory_data: MemoryCreate,
    db: Session = Depends(get_db)
):
    """Create a new memory.

    - Human-created memories default to 'observed' status
    - Agent-created memories default to 'proposed' status (require approval)
    """
    service = MemoryService(db, embedding_service, vector_store)
    memory = service.create_memory(
        content=memory_data.content,
        source=memory_data.source,
        memory_type=memory_data.memory_type,
        created_by=memory_data.created_by
    )
    return memory


@app.get("/memories", response_model=list[Memory])
def list_memories(
    limit: int = 100,
    approval_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all memories, optionally filtered by approval status."""
    service = MemoryService(db, embedding_service, vector_store)
    return service.get_all_memories(limit=limit, approval_status=approval_status)


@app.get("/memories/search")
def search_memories(
    query: str,
    limit: int = 5,
    approval_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Search memories semantically using natural language query."""
    service = MemoryService(db, embedding_service, vector_store)
    memories = service.search_memories(
        query=query,
        limit=limit,
        approval_status=approval_status
    )
    return {
        "query": query,
        "results": memories,
        "count": len(memories)
    }


@app.get("/memories/{memory_id}", response_model=Memory)
def get_memory(
    memory_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific memory by ID."""
    service = MemoryService(db, embedding_service, vector_store)
    memory = service.get_memory(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


@app.patch("/memories/{memory_id}/status", response_model=Memory)
def update_memory_status(
    memory_id: str,
    status: str,
    db: Session = Depends(get_db)
):
    """Update the approval status of a memory.

    Valid statuses: proposed, observed, approved
    """
    valid_statuses = ["proposed", "observed", "approved"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )

    service = MemoryService(db, embedding_service, vector_store)
    memory = service.update_approval_status(memory_id, status)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)