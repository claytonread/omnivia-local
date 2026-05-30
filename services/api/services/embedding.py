from fastembed import TextEmbedding
from typing import List


class EmbeddingService:
    """Service for generating text embeddings using FastEmbed."""

    def __init__(self, model_name: str = "nomic-ai/nomic-embed-text-v1.5"):
        self.model_name = model_name
        self.model = TextEmbedding(model_name)

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        embeddings = list(self.model.embed([text]))
        return embeddings[0] if embeddings else []

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        return list(self.model.embed(texts))