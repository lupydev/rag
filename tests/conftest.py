"""
🧪 Test Configuration

Configuración común para todos los tests de la aplicación RAG
"""

import os
import pytest
from unittest.mock import Mock
from typing import Any

# Configurar variables de entorno para testing
os.environ["OPENAI_API_KEY"] = "test-openai-key"
os.environ["PINECONE_API_KEY"] = "test-pinecone-key"
os.environ["PINECONE_INDEX_NAME"] = "test-index"
os.environ["LANGSMITH_API_KEY"] = "test-langsmith-key"

# No necesitamos importar la app para tests de funciones


@pytest.fixture
def mock_embeddings():
    """Mock para embeddings de OpenAI - usado en tests específicos"""
    mock_client = Mock()
    mock_client.embed_query.return_value = [
        0.1
    ] * 1536  # Vector fake de 1536 dimensiones
    yield mock_client


@pytest.fixture
def mock_pinecone_index():
    """Mock del índice de Pinecone - usado en tests específicos"""
    mock_index = Mock()

    # Mock de búsqueda que devuelve resultados simulados con scores altos
    mock_query_result = Mock()
    mock_query_result.get.return_value = [
        {
            "id": "test-chunk-1",
            "score": 0.95,
            "metadata": {
                "text": "Este es un texto de prueba sobre machine learning.",
                "filename": "test.txt",
                "document_id": "test-doc-123",
                "chunk_index": 0,
            },
        },
        {
            "id": "test-chunk-2",
            "score": 0.87,
            "metadata": {
                "text": "Machine learning es una rama de la inteligencia artificial.",
                "filename": "test.txt",
                "document_id": "test-doc-123",
                "chunk_index": 1,
            },
        },
    ]

    mock_index.query.return_value = mock_query_result
    mock_index.upsert.return_value = {"upserted_count": 2}
    mock_index.describe_index_stats.return_value = {
        "total_vector_count": 100,
        "dimension": 1536,
        "index_fullness": 0.1,
        "namespaces": {},
    }
    mock_index.delete.return_value = {}

    yield mock_index


@pytest.fixture
def mock_llm():
    """Mock para LLM de OpenAI - usado en tests específicos"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = "Esta es una respuesta generada por el LLM de prueba."
    mock_client.invoke.return_value = mock_response
    yield mock_client


@pytest.fixture
def sample_text() -> str:
    """Texto de muestra para testing"""
    return """
    Este es un documento de prueba para testing de RAG.
    
    Contiene múltiples párrafos para probar la división en chunks.
    El sistema debe ser capaz de procesar este texto correctamente.
    
    También incluye información sobre machine learning y procesamiento de lenguaje natural.
    Esto permite probar consultas específicas sobre el contenido.
    
    El documento tiene suficiente contenido para generar múltiples chunks
    y probar las funcionalidades de búsqueda semántica.
    """


@pytest.fixture
def sample_chunks() -> list[dict[str, Any]]:
    """Chunks de muestra para testing"""
    return [
        {
            "document_id": "test-doc-123",
            "chunk_id": "test-doc-123_0",
            "chunk_index": 0,
            "text": "Este es un documento de prueba para testing de RAG.",
            "filename": "test.txt",
            "metadata": {
                "filename": "test.txt",
                "document_id": "test-doc-123",
                "upload_date": "2025-10-14T12:00:00",
            },
        },
        {
            "document_id": "test-doc-123",
            "chunk_id": "test-doc-123_1",
            "chunk_index": 1,
            "text": "El sistema debe ser capaz de procesar este texto correctamente.",
            "filename": "test.txt",
            "metadata": {
                "filename": "test.txt",
                "document_id": "test-doc-123",
                "upload_date": "2025-10-14T12:00:00",
            },
        },
    ]


@pytest.fixture
def sample_query_request() -> dict[str, Any]:
    """Request de query de muestra"""
    return {
        "query": "¿Qué es machine learning?",
        "max_results": 5,
        "similarity_threshold": 0.7,
    }


class TestHelpers:
    """Funciones helper para tests"""

    @staticmethod
    def create_mock_file(filename: str, content: str):
        """Crea un mock de UploadFile"""
        from io import BytesIO
        from fastapi import UploadFile

        file_obj = BytesIO(content.encode())
        return UploadFile(filename=filename, file=file_obj)

    @staticmethod
    def assert_valid_uuid(uuid_string: str) -> bool:
        """Verifica que un string sea un UUID válido"""
        import uuid

        try:
            uuid.UUID(uuid_string)
            return True
        except ValueError:
            return False
