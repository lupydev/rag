"""
🧪 Archivo __init__.py para el paquete de tests

Marca el directorio como un paquete Python y define imports comunes
"""

# Imports comunes para tests
from .conftest import (
    TestHelpers,
    mock_embeddings,
    mock_pinecone_index,
    mock_llm,
    sample_text,
    sample_chunks,
    sample_query_request,
)

__all__ = [
    "TestHelpers",
    "mock_embeddings",
    "mock_pinecone_index",
    "mock_llm",
    "sample_text",
    "sample_chunks",
    "sample_query_request",
]
