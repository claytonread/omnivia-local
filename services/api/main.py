import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker, Session

from services.api.database import init_db, get_engine
from services.api.models import MemoryCreate, Memory
from services.api.services.memory_service import MemoryService
from services.api.services.ingestion import scan_workspace
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


# =============================================================================
# Ingestion Endpoints
# =============================================================================


class WorkspaceScanRequest(BaseModel):
    """Request to scan a local workspace path."""
    workspace_path: str
    max_files: int = 10000
    follow_symlinks: bool = False


class FileInventoryItem(BaseModel):
    """One file entry in the scan inventory."""
    path: str
    extension: str
    size: int
    modified_ms: int
    file_type: str
    parse_status: str


class WorkspaceScanResponse(BaseModel):
    """Response from scanning a workspace."""
    workspace_path: str
    total_files: int
    supported_files: int
    unsupported_files: int
    errors: int
    scan_duration_ms: int
    items: list[FileInventoryItem]


@app.post("/ingest/scan", response_model=WorkspaceScanResponse)
def scan_workspace_endpoint(request: WorkspaceScanRequest):
    """Scan a local workspace and produce a file inventory.

    Returns metadata about all discoverable files without modifying them.
    Supported file types: markdown (.md, .markdown), plain text (.txt)
    """
    try:
        result = scan_workspace(
            workspace_path=request.workspace_path,
            max_files=request.max_files,
            follow_symlinks=request.follow_symlinks,
        )
        return WorkspaceScanResponse(
            workspace_path=result.workspace_path,
            total_files=result.total_files,
            supported_files=result.supported_files,
            unsupported_files=result.unsupported_files,
            errors=result.errors,
            scan_duration_ms=result.scan_duration_ms,
            items=[
                FileInventoryItem(
                    path=item.path,
                    extension=item.extension,
                    size=item.size,
                    modified_ms=item.modified_ms,
                    file_type=item.file_type,
                    parse_status=item.parse_status,
                )
                for item in result.items
            ],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Workspace scan error: {e}")
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)