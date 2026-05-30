import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker, Session

from services.api.database import init_db, get_engine
from services.api.models import (
    MemoryCreate, Memory,
    NodeCreate, NodeResponse,
    EdgeCreate, EdgeResponse,
    SourceCreate, SourceResponse,
    Node, Edge, Source,
)
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


# =============================================================================
# Node Endpoints
# =============================================================================

def _get_node_service(db: Session):
    """Get a NodeService instance (placeholder for future implementation)."""
    # TODO: Implement NodeService with full CRUD
    return db


@app.post("/nodes", response_model=NodeResponse, status_code=201)
def create_node(node_data: NodeCreate, db: Session = Depends(get_db)):
    """Create a new node in the knowledge graph.

    Nodes represent structured knowledge entities like concepts, people,
    projects, or decisions.
    """
    import uuid
    import json

    node = Node(
        id=str(uuid.uuid4()),
        node_type=node_data.node_type,
        title=node_data.title,
        body=node_data.body,
        tags=node_data.tags,
        source_ids=json.dumps(node_data.source_ids) if node_data.source_ids else None,
        metadata_json=json.dumps(node_data.metadata) if node_data.metadata else None,
    )
    db.add(node)
    db.commit()
    db.refresh(node)

    logger.info(f"Created node {node.id} of type {node.node_type}")
    return NodeResponse(
        id=node.id,
        node_type=node.node_type,
        title=node.title,
        body=node.body,
        tags=node.tags,
        source_ids=json.loads(node.source_ids) if node.source_ids else None,
        created_at=node.created_at,
        updated_at=node.updated_at,
        metadata=json.loads(node.metadata_json) if node.metadata_json else None,
    )


@app.get("/nodes", response_model=list[NodeResponse])
def list_nodes(
    node_type: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all nodes, optionally filtered by type or tag."""
    query = db.query(Node)
    if node_type:
        query = query.filter(Node.node_type == node_type)
    if tag:
        query = query.filter(Node.tags.contains(tag))
    nodes = query.order_by(Node.created_at.desc()).limit(limit).all()

    import json
    return [
        NodeResponse(
            id=n.id,
            node_type=n.node_type,
            title=n.title,
            body=n.body,
            tags=n.tags,
            source_ids=json.loads(n.source_ids) if n.source_ids else None,
            created_at=n.created_at,
            updated_at=n.updated_at,
            metadata=json.loads(n.metadata_json) if n.metadata_json else None,
        )
        for n in nodes
    ]


@app.get("/nodes/{node_id}", response_model=NodeResponse)
def get_node(node_id: str, db: Session = Depends(get_db)):
    """Get a specific node by ID."""
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    import json
    return NodeResponse(
        id=node.id,
        node_type=node.node_type,
        title=node.title,
        body=node.body,
        tags=node.tags,
        source_ids=json.loads(node.source_ids) if node.source_ids else None,
        created_at=node.created_at,
        updated_at=node.updated_at,
        metadata=json.loads(node.metadata_json) if node.metadata_json else None,
    )


# =============================================================================
# Edge Endpoints
# =============================================================================

@app.post("/edges", response_model=EdgeResponse, status_code=201)
def create_edge(edge_data: EdgeCreate, db: Session = Depends(get_db)):
    """Create a new edge connecting two nodes.

    Edges define relationships in the knowledge graph like
    'relates_to', 'depends_on', or 'supports'.
    """
    import uuid
    import json

    # Verify both nodes exist
    source_node = db.query(Node).filter(Node.id == edge_data.source_node_id).first()
    if not source_node:
        raise HTTPException(status_code=404, detail=f"Source node {edge_data.source_node_id} not found")

    target_node = db.query(Node).filter(Node.id == edge_data.target_node_id).first()
    if not target_node:
        raise HTTPException(status_code=404, detail=f"Target node {edge_data.target_node_id} not found")

    edge = Edge(
        id=str(uuid.uuid4()),
        source_node_id=edge_data.source_node_id,
        target_node_id=edge_data.target_node_id,
        relationship_type=edge_data.relationship_type,
        direction=edge_data.direction,
        weight=edge_data.weight or 0.5,
        source_ids=json.dumps(edge_data.source_ids) if edge_data.source_ids else None,
    )
    db.add(edge)
    db.commit()
    db.refresh(edge)

    logger.info(f"Created edge {edge.id}: {edge.source_node_id} --[{edge.relationship_type}]--> {edge.target_node_id}")

    return EdgeResponse(
        id=edge.id,
        source_node_id=edge.source_node_id,
        target_node_id=edge.target_node_id,
        relationship_type=edge.relationship_type,
        direction=edge.direction,
        weight=edge.weight,
        source_ids=json.loads(edge.source_ids) if edge.source_ids else None,
        created_at=edge.created_at,
    )


@app.get("/edges", response_model=list[EdgeResponse])
def list_edges(
    relationship_type: Optional[str] = None,
    source_node_id: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all edges, optionally filtered by type or source node."""
    query = db.query(Edge)
    if relationship_type:
        query = query.filter(Edge.relationship_type == relationship_type)
    if source_node_id:
        query = query.filter(Edge.source_node_id == source_node_id)
    edges = query.order_by(Edge.created_at.desc()).limit(limit).all()

    import json
    return [
        EdgeResponse(
            id=e.id,
            source_node_id=e.source_node_id,
            target_node_id=e.target_node_id,
            relationship_type=e.relationship_type,
            direction=e.direction,
            weight=e.weight,
            source_ids=json.loads(e.source_ids) if e.source_ids else None,
            created_at=e.created_at,
        )
        for e in edges
    ]


@app.get("/nodes/{node_id}/edges")
def get_node_edges(node_id: str, db: Session = Depends(get_db)):
    """Get all edges connected to a specific node."""
    edges = db.query(Edge).filter(
        (Edge.source_node_id == node_id) | (Edge.target_node_id == node_id)
    ).all()

    import json
    return {
        "node_id": node_id,
        "edges": [
            EdgeResponse(
                id=e.id,
                source_node_id=e.source_node_id,
                target_node_id=e.target_node_id,
                relationship_type=e.relationship_type,
                direction=e.direction,
                weight=e.weight,
                source_ids=json.loads(e.source_ids) if e.source_ids else None,
                created_at=e.created_at,
            )
            for e in edges
        ],
        "count": len(edges),
    }


# =============================================================================
# Source Endpoints
# =============================================================================

@app.post("/sources", response_model=SourceResponse, status_code=201)
def create_source(source_data: SourceCreate, db: Session = Depends(get_db)):
    """Register a new source document or artefact.

    Sources track the origin of ingested content for provenance.
    """
    import uuid
    import json

    source = Source(
        id=str(uuid.uuid4()),
        source_type=source_data.source_type,
        uri=source_data.uri,
        title=source_data.title,
        file_hash=source_data.file_hash,
        file_size=source_data.file_size,
        metadata_json=json.dumps(source_data.metadata) if source_data.metadata else None,
    )
    db.add(source)
    db.commit()
    db.refresh(source)

    logger.info(f"Created source {source.id}: {source.uri}")

    return SourceResponse(
        id=source.id,
        source_type=source.source_type,
        uri=source.uri,
        title=source.title,
        file_hash=source.file_hash,
        file_size=source.file_size,
        imported_at=source.imported_at,
        last_indexed_at=source.last_indexed_at,
        metadata=json.loads(source.metadata_json) if source.metadata_json else None,
    )


@app.get("/sources", response_model=list[SourceResponse])
def list_sources(
    source_type: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all sources, optionally filtered by type."""
    query = db.query(Source)
    if source_type:
        query = query.filter(Source.source_type == source_type)
    sources = query.order_by(Source.imported_at.desc()).limit(limit).all()

    import json
    return [
        SourceResponse(
            id=s.id,
            source_type=s.source_type,
            uri=s.uri,
            title=s.title,
            file_hash=s.file_hash,
            file_size=s.file_size,
            imported_at=s.imported_at,
            last_indexed_at=s.last_indexed_at,
            metadata=json.loads(s.metadata_json) if s.metadata_json else None,
        )
        for s in sources
    ]


@app.get("/sources/{source_id}", response_model=SourceResponse)
def get_source(source_id: str, db: Session = Depends(get_db)):
    """Get a specific source by ID."""
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    import json
    return SourceResponse(
        id=source.id,
        source_type=source.source_type,
        uri=source.uri,
        title=source.title,
        file_hash=source.file_hash,
        file_size=source.file_size,
        imported_at=source.imported_at,
        last_indexed_at=source.last_indexed_at,
        metadata=json.loads(source.metadata_json) if source.metadata_json else None,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)