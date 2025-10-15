from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.schemas.query import QueryResponse
from app.services.document import query_documents
from app.schemas.document import (
    DocumentResponse,
)
import logging

from app.utils.doc_to_vectores import delete_all_vectors, process_document
from app.schemas.query import QueryRequest

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Subir documento",
    description="Sube un documento (PDF, DOCX, TXT, MD, CSV)",
)
async def upload_document(file: UploadFile = File(...)):
    """
    📤 Sube y procesa un documento

    - Extrae texto del archivo
    - Divide en chunks inteligentes
    - Genera embeddings con OpenAI
    - Almacena vectores en Pinecone

    Formatos soportados: PDF, DOCX, TXT, MD, CSV
    """
    try:
        # Validaciones básicas
        if not file.filename:
            raise HTTPException(400, "Filename is required")

        # Validar tipo de archivo
        supported_types = [".pdf", ".docx", ".txt", ".md", ".csv"]
        if not any(file.filename.lower().endswith(ext) for ext in supported_types):
            raise HTTPException(
                400, f"Unsupported file type. Supported: {', '.join(supported_types)}"
            )

        # Procesar documento (función pura)
        result = process_document(file)

        # Convertir a modelo de respuesta
        return DocumentResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing error: {str(e)}",
        )


@router.post("/query", response_model=QueryResponse)
async def query_documents_endpoint(request: QueryRequest) -> QueryResponse:
    """
    🔍 Consulta documentos con RAG y guard rails

    - Busca documentos similares semánticamente
    - Aplica guard rails para calidad
    - Genera respuesta contextualizada con LLM
    - Incluye fuentes y nivel de confianza

    Guard rails automáticos:
    - Consultas vacías o muy cortas
    - Umbral de similitud configurable
    - Detección de respuestas genéricas
    - Control de calidad de contexto
    """
    try:
        # Delegar a función pura de service
        return query_documents(
            query=request.query,
            max_results=request.max_results,
            similarity_threshold=request.similarity_threshold,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query error: {str(e)}",
        )


@router.delete("/vectors/delete-all")
async def delete_all_vectors_endpoint():
    """
    🗑️ ELIMINA TODOS los vectores del índice de Pinecone

    ⚠️ **OPERACIÓN DESTRUCTIVA**: Esta acción NO se puede deshacer

    Utiliza esta función para:
    - Limpiar completamente el índice
    - Empezar de cero con nuevos documentos
    - Debugging y desarrollo

    **Importante**:
    - Todos los documentos subidos serán eliminados
    - Las consultas fallarán hasta que subas nuevos documentos
    - La operación puede tardar unos segundos en completarse
    """
    try:
        # Delegar a función pura de service
        result = delete_all_vectors()
        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Delete operation failed: {str(e)}",
        )
