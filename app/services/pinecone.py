from typing import Any
from pinecone import Pinecone
from ..core.config import settings


def get_pinecone_index():
    """Obtiene índice de Pinecone"""
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)  # Corregido: usar PINECONE_API_KEY
    return pc.Index(settings.PINECONE_INDEX_NAME)


def store_vectors_in_pinecone(vectors: list[dict[str, Any]]) -> list[str]:
    """
    Almacena vectores en Pinecone

    Args:
        vectors: Lista de vectores

    Returns:
        Lista de IDs almacenados
    """
    index = get_pinecone_index()

    # Upsert en lotes si hay muchos vectores
    batch_size = 100
    stored_ids = []

    for i in range(0, len(vectors), batch_size):
        batch = vectors[i : i + batch_size]
        index.upsert(vectors=batch)
        stored_ids.extend([v["id"] for v in batch])

    return stored_ids
