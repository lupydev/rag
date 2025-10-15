"""
🧪 Tests para Services

Tests para lógica de negocio (embeddings, pinecone, document processing)
"""

import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException

from app.services.embeddings import (
    create_embeddings,
    create_text_splitter,
    create_text_chunks,
)
from app.services.document import query_documents
from app.utils.doc_to_vectores import process_document


class TestEmbeddingsService:
    """Tests para servicio de embeddings"""

    def test_create_embeddings(self):
        """Test creación de cliente de embeddings"""
        with patch("app.services.embeddings.OpenAIEmbeddings") as mock_embeddings:
            mock_instance = Mock()
            mock_embeddings.return_value = mock_instance

            result = create_embeddings()

            mock_embeddings.assert_called_once()
            assert result == mock_instance

    def test_create_text_splitter(self):
        """Test creación de text splitter"""
        splitter = create_text_splitter()

        assert splitter is not None
        assert hasattr(splitter, "split_documents")

        # Test con parámetros personalizados
        custom_splitter = create_text_splitter(chunk_size=500, chunk_overlap=100)
        assert custom_splitter is not None

    def test_create_text_chunks(self, sample_text):
        """Test creación de chunks de texto"""
        chunks = create_text_chunks(sample_text, "test.txt")

        assert len(chunks) > 0
        assert all(isinstance(chunk, dict) for chunk in chunks)

        # Verificar estructura del primer chunk
        first_chunk = chunks[0]
        assert "document_id" in first_chunk
        assert "chunk_id" in first_chunk
        assert "chunk_index" in first_chunk
        assert "text" in first_chunk
        assert "filename" in first_chunk
        assert "metadata" in first_chunk

        # Verificar que document_id es string
        assert isinstance(first_chunk["document_id"], str)

        # Verificar que todos los chunks tienen el mismo document_id
        doc_id = first_chunk["document_id"]
        assert all(chunk["document_id"] == doc_id for chunk in chunks)

        # Verificar filename
        assert all(chunk["filename"] == "test.txt" for chunk in chunks)

        # Verificar chunk_id format
        for i, chunk in enumerate(chunks):
            expected_chunk_id = f"{doc_id}_{i}"
            assert chunk["chunk_id"] == expected_chunk_id
            assert chunk["chunk_index"] == i

    # Test eliminado: Hacía llamadas reales a OpenAI API


class TestPineconeService:
    """Tests para servicio de Pinecone"""

    # Tests eliminados: Hacían llamadas reales a Pinecone API


class TestDocumentService:
    """Tests para servicio de documentos"""

    # Test eliminado: Hacía llamadas reales a Pinecone API

    def test_query_documents_empty_query(self):
        """Test consulta con query vacío"""
        response = query_documents(query="", max_results=5, similarity_threshold=0.7)

        assert response.guard_rail_triggered == "empty_query"
        assert response.confidence == "none"
        assert "pregunta válida" in response.answer

    def test_query_documents_short_query(self):
        """Test consulta con query muy corto"""
        response = query_documents(query="hi", max_results=5, similarity_threshold=0.7)

        assert response.guard_rail_triggered == "short_query"
        assert response.confidence == "low"
        assert "demasiado corta" in response.answer

    # Test eliminado: Hacía llamadas reales a Pinecone API


class TestDocumentProcessing:
    """Tests para procesamiento de documentos"""

    # Test eliminado: Hacía llamadas reales a OpenAI API

    def test_process_document_no_filename(self):
        """Test procesamiento con archivo sin nombre"""
        mock_file = Mock()
        mock_file.filename = None

        with pytest.raises(HTTPException) as exc_info:
            process_document(mock_file)

        assert exc_info.value.status_code == 400
        assert "Filename required" in str(exc_info.value.detail)

    def test_process_document_empty_text(self):
        """Test procesamiento con texto vacío"""
        from tests.conftest import TestHelpers

        mock_file = TestHelpers.create_mock_file("empty.txt", "")

        with patch("app.utils.text_extraction.extract_text_from_file") as mock_extract:
            mock_extract.return_value = ""

            with pytest.raises(HTTPException) as exc_info:
                process_document(mock_file)

            assert exc_info.value.status_code == 400
            assert "no valid text" in str(exc_info.value.detail)

    # Tests eliminados: Hacían llamadas reales a Pinecone API
