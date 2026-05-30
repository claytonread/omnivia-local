"""Text embedding service using FastEmbed.

FastEmbed generates local vector embeddings without requiring external API calls.
This preserves privacy and avoids per-request costs.
"""

from fastembed import TextEmbedding
from typing import List


class EmbeddingService:
    """Service for generating text embeddings using FastEmbed.

    Uses the nomic-embed-text-v1.5 model which is optimized for code and
    documentation. Embeddings are 768-dimensional vectors.

    The model is downloaded on first use (~100MB) and cached locally.
    """

    # Default embedding model: high quality, local, no API costs
    DEFAULT_MODEL = "nomic-ai/nomic-embed-text-v1.5"

    def __init__(self, model_name: str = DEFAULT_MODEL):
        """Initialize the embedding service with the specified model.

        Args:
            model_name: HuggingFace model identifier. Defaults to nomic-embed-text-v1.5
        """
        self.model_name = model_name
        # TextEmbedding downloads model on first instantiation if not cached
        self.model = TextEmbedding(model_name)

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text string.

        Args:
            text: The text to embed.

        Returns:
            768-dimensional embedding vector as a list of floats.
        """
        embeddings = list(self.model.embed([text]))
        return embeddings[0] if embeddings else []

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple text strings.

        More efficient than calling embed_text repeatedly for batch processing.

        Args:
            texts: List of text strings to embed.

        Returns:
            List of 768-dimensional embedding vectors.
        """
        return list(self.model.embed(texts))