from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, SearchParams
from typing import List, Optional, Dict, Any
import uuid


COLLECTION_NAME = "omnivia_memories"


class VectorStore:
    """Service for storing and searching vector embeddings using Qdrant."""

    def __init__(self, url: str, collection_name: str = COLLECTION_NAME):
        self.url = url
        self.collection_name = collection_name
        self.client = QdrantClient(url=url)
        self._ensure_collection()

    def _ensure_collection(self):
        """Ensure the collection exists, create if necessary."""
        collections = [c.name for c in self.client.get_collections().collections]
        if self.collection_name not in collections:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config={"size": 768, "distance": Distance.COSINE}
            )

    def upsert(self, text: str, vector: List[float], metadata: Dict[str, Any]) -> str:
        """Store a text embedding with metadata."""
        point_id = str(uuid.uuid4())
        self.client.upsert(
            collection_name=self.collection_name,
            points=[PointStruct(id=point_id, vector=vector, payload=metadata)]
        )
        return point_id

    def search(self, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit
        )
        return [{"id": r.id, "score": r.score, "payload": r.payload} for r in results.points]

    def search_by_text(
        self, query_text: str, embedding_service, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search by converting text to embedding first."""
        query_vector = embedding_service.embed_text(query_text)
        return self.search(query_vector, limit)

    def delete(self, point_id: str) -> bool:
        """Delete a point by ID."""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[point_id]
            )
            return True
        except Exception:
            return False