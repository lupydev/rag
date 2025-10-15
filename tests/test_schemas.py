"""
🧪 Tests para Schemas

Tests para validación de modelos Pydantic/SQLModel
"""

import pytest
from pydantic import ValidationError
from app.schemas.query import QueryRequest, QueryResponse, QuerySource, QueryStats
from app.schemas.document import (
    DocumentCreate,
    DocumentResponse,
)


class TestQueryRequest:
    """Tests para QueryRequest"""

    def test_valid_query_request(self):
        """Test creación válida de QueryRequest"""
        data = {
            "query": "¿Qué es machine learning?",
            "max_results": 5,
            "similarity_threshold": 0.7,
        }

        request = QueryRequest(**data)

        assert request.query == "¿Qué es machine learning?"
        assert request.max_results == 5
        assert request.similarity_threshold == 0.7

    def test_default_values(self):
        """Test valores por defecto"""
        request = QueryRequest(query="test query")

        assert request.query == "test query"
        assert request.max_results == 5
        assert request.similarity_threshold == 0.7

    def test_query_validation_empty(self):
        """Test validación de query vacío"""
        with pytest.raises(ValidationError) as exc_info:
            QueryRequest(query="")

        # El error puede ser por min_length o por el validator personalizado
        error_msg = str(exc_info.value)
        assert (
            "String should have at least 1 character" in error_msg
            or "El query no puede estar vacío" in error_msg
        )

    def test_query_validation_whitespace(self):
        """Test validación de query solo espacios"""
        with pytest.raises(ValidationError) as exc_info:
            QueryRequest(query="   ")

        assert "El query no puede estar vacío" in str(exc_info.value)

    def test_query_strips_whitespace(self):
        """Test que se eliminen espacios en blanco"""
        request = QueryRequest(query="  test query  ")
        assert request.query == "test query"

    def test_max_results_validation(self):
        """Test validación de max_results"""
        # Valor válido
        request = QueryRequest(query="test", max_results=10)
        assert request.max_results == 10

        # Valor muy bajo
        with pytest.raises(ValidationError):
            QueryRequest(query="test", max_results=0)

        # Valor muy alto
        with pytest.raises(ValidationError):
            QueryRequest(query="test", max_results=25)

    def test_similarity_threshold_validation(self):
        """Test validación de similarity_threshold"""
        # Valor válido
        request = QueryRequest(query="test", similarity_threshold=0.5)
        assert request.similarity_threshold == 0.5

        # Valor muy bajo
        with pytest.raises(ValidationError):
            QueryRequest(query="test", similarity_threshold=-0.1)

        # Valor muy alto
        with pytest.raises(ValidationError):
            QueryRequest(query="test", similarity_threshold=1.1)


class TestQuerySource:
    """Tests para QuerySource"""

    def test_valid_query_source(self):
        """Test creación válida de QuerySource"""
        data = {
            "document_id": "test-doc-123",
            "filename": "test.txt",
            "chunk_id": "test-doc-123_0",
            "score": 0.85,
            "content_preview": "Este es un fragmento de contenido...",
        }

        source = QuerySource(**data)

        assert source.document_id == "test-doc-123"
        assert source.filename == "test.txt"
        assert source.chunk_id == "test-doc-123_0"
        assert source.score == 0.85
        assert "fragmento de contenido" in source.content_preview

    def test_document_id_as_string(self):
        """Test que document_id sea string (no UUID object)"""
        source = QuerySource(
            document_id="ff078d80-0434-418a-a6b3-91aee2b2858d",
            filename="test.txt",
            chunk_id="test_0",
            score=0.8,
            content_preview="test",
        )

        assert isinstance(source.document_id, str)
        assert source.document_id == "ff078d80-0434-418a-a6b3-91aee2b2858d"


class TestQueryResponse:
    """Tests para QueryResponse"""

    def test_valid_query_response(self):
        """Test creación válida de QueryResponse"""
        source = QuerySource(
            document_id="test-doc-123",
            filename="test.txt",
            chunk_id="test_0",
            score=0.85,
            content_preview="contenido de prueba",
        )

        response = QueryResponse(
            query="¿Qué es esto?",
            answer="Es un documento de prueba",
            sources=[source],
            confidence="high",
        )

        assert response.query == "¿Qué es esto?"
        assert response.answer == "Es un documento de prueba"
        assert len(response.sources) == 1
        assert response.sources[0].document_id == "test-doc-123"
        assert response.confidence == "high"

    def test_empty_sources(self):
        """Test respuesta sin fuentes"""
        response = QueryResponse(
            query="test", answer="No hay información", confidence="none"
        )

        assert len(response.sources) == 0
        assert response.confidence == "none"

    def test_optional_metadata(self):
        """Test metadata opcional"""
        response = QueryResponse(
            query="test",
            answer="respuesta",
            confidence="medium",
            guard_rail_triggered="short_query",
            average_similarity=0.75,
            context_chunks_used=3,
        )

        assert response.guard_rail_triggered == "short_query"
        assert response.average_similarity == 0.75
        assert response.context_chunks_used == 3
        # processing_time_ms no está en QueryResponse, está en QueryStats


class TestDocumentSchemas:
    """Tests para schemas de documentos"""

    def test_document_create(self):
        """Test DocumentCreate"""
        doc = DocumentCreate(
            filename="test.pdf", content_type="application/pdf", size_bytes=1024
        )

        assert doc.filename == "test.pdf"
        assert doc.content_type == "application/pdf"
        assert doc.size_bytes == 1024
        assert doc.upload_date is not None

    def test_document_response(self):
        """Test DocumentResponse"""
        response = DocumentResponse(
            filename="test.pdf",
            document_id="test-doc-123",
            text_length=5000,
            chunks_count=5,
            vectors_count=5,
            status="success",
            message="Procesado correctamente",
        )

        assert response.filename == "test.pdf"
        assert response.document_id == "test-doc-123"
        assert response.text_length == 5000
        assert response.chunks_count == 5
        assert response.vectors_count == 5
        assert response.status == "success"
        assert isinstance(response.document_id, str)  # Debe ser string, no UUID object


class TestQueryStats:
    """Tests para QueryStats"""

    def test_query_stats_creation(self):
        """Test creación de QueryStats"""
        stats = QueryStats(
            query="test query",
            response_length=100,
            sources_found=3,
            confidence="high",
            processing_time_ms=250.0,
        )

        assert stats.query == "test query"
        assert stats.response_length == 100
        assert stats.sources_found == 3
        assert stats.confidence == "high"
        assert stats.processing_time_ms == 250.0
        assert stats.timestamp is not None
