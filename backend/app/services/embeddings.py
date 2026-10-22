"""
Embedding service for AgenticBuy.

Handles text embedding generation via Ollama/Gemma and ChromaDB
indexing/search operations for semantic product search.
"""

import logging
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


async def generate_embedding(text: str) -> list[float]:
    """Generate a text embedding using the Ollama API.

    Calls the Ollama embeddings endpoint with the configured model
    to produce a vector representation of the input text.

    Args:
        text: The text to generate an embedding for.

    Returns:
        A list of floats representing the embedding vector.

    Raises:
        httpx.HTTPStatusError: If the Ollama API returns an error.
        RuntimeError: If the embedding response is malformed.
    """
    settings = get_settings()
    ollama_url = settings.OLLAMA_BASE_URL.rstrip("/")
    model_name = getattr(settings, "GEMMA_MODEL", "gemma2:9b")

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{ollama_url}/api/embeddings",
            json={
                "model": model_name,
                "prompt": text,
            },
        )
        response.raise_for_status()
        data = response.json()

    embedding = data.get("embedding")
    if embedding is None:
        raise RuntimeError(
            f"Ollama returned no embedding. Response: {data}"
        )

    return embedding


async def index_product(
    product_id: str,
    product_text: str,
    chroma_client: Any,
) -> None:
    """Index a product into ChromaDB for semantic search.

    Generates an embedding for the product text and upserts it into
    the "products" collection in ChromaDB.

    Args:
        product_id: The unique identifier for the product.
        product_text: The text content to embed (name + description, etc.).
        chroma_client: The ChromaDB client instance.
    """
    try:
        embedding = await generate_embedding(product_text)

        collection = chroma_client.get_or_create_collection(name="products")
        collection.upsert(
            ids=[product_id],
            embeddings=[embedding],
            documents=[product_text],
            metadatas=[{"product_id": product_id}],
        )
        logger.info("Indexed product %s into ChromaDB", product_id)
    except Exception:
        logger.exception("Failed to index product %s", product_id)
        raise


async def search_products(
    query: str,
    chroma_client: Any,
    limit: int = 10,
) -> list[dict]:
    """Search for products using semantic similarity via ChromaDB.

    Generates an embedding for the query text and performs a nearest-neighbor
    search against the "products" collection.

    Args:
        query: The natural language search query.
        chroma_client: The ChromaDB client instance.
        limit: Maximum number of results to return.

    Returns:
        A list of dicts, each containing:
            - id: The product ID.
            - document: The indexed product text.
            - score: The similarity distance (lower is more similar).
            - metadata: Any stored metadata.
    """
    if not chroma_client:
        return []

    try:
        embedding = await generate_embedding(query)

        collection = chroma_client.get_or_create_collection(name="products")
        results = collection.query(
            query_embeddings=[embedding],
            n_results=limit,
        )

        products = []
        if results and results.get("ids") and results["ids"][0]:
            ids = results["ids"][0]
            documents = results.get("documents", [[]])[0]
            distances = results.get("distances", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]

            for i, product_id in enumerate(ids):
                products.append({
                    "id": product_id,
                    "document": documents[i] if i < len(documents) else "",
                    "score": distances[i] if i < len(distances) else 0.0,
                    "metadata": metadatas[i] if i < len(metadatas) else {},
                })

        return products
    except Exception as e:
        logger.warning("ChromaDB/Gemma embedding search unavailable (%s), returning empty for fallback.", e)
        return []
