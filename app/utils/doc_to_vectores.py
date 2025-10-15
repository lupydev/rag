from typing import Any
from fastapi import HTTPException, UploadFile, status

from app.core.logging import app_logger as logger
from app.services.embeddings import create_text_chunks, create_vectors_from_chunks
from app.services.pinecone import get_pinecone_index
from app.utils.text_extraction import extract_text_from_file


def store_vectors_in_pinecone(vectors: list[dict[str, Any]]) -> list[str]:
    """
    Almacena vectores en Pinecone

    Args:
        vectors: Lista de vectores con metadata

    Returns:
        Lista de IDs de vectores almacenados
    """
    index = get_pinecone_index()

    # Upsert en batches de 100 vectores
    batch_size = 100
    vector_ids = []

    for i in range(0, len(vectors), batch_size):
        batch = vectors[i : i + batch_size]
        response = index.upsert(vectors=batch)
        vector_ids.extend([vector["id"] for vector in batch])

    return vector_ids


def process_document(file: UploadFile) -> dict[str, Any]:
    """
    Procesa un documento completo

    Función pura que orquesta todo el proceso:
    1. Extrae texto
    2. Divide en chunks
    3. Genera embeddings
    4. Almacena en Pinecone

    Args:
        file: Archivo subido

    Returns:
        Dict con resultado del procesamiento
    """
    # Validaciones simples
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Filename required"
        )

    # 1. Extraer texto
    text = extract_text_from_file(file)
    if not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document contains no valid text",
        )

    # 2. Crear chunks
    chunks = create_text_chunks(text, file.filename)
    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create text chunks",
        )

    # 3. Generar embeddings y vectorizar
    vectors = create_vectors_from_chunks(chunks)

    # 4. Almacenar en Pinecone
    vector_ids = store_vectors_in_pinecone(vectors)

    # 5. Resultado
    doc_id = chunks[0]["document_id"]  # Todos los chunks tienen el mismo doc_id

    return {
        "document_id": doc_id,
        "filename": file.filename,
        "text_length": len(text),
        "chunks_count": len(chunks),
        "vectors_count": len(vector_ids),
        "status": "success",
        "message": f"Document '{file.filename}' processed successfully",
    }


def delete_all_vectors() -> dict[str, Any]:
    """
    🗑️ Elimina TODOS los vectores del índice de Pinecone

    ⚠️ OPERACIÓN DESTRUCTIVA: No se puede deshacer

    Returns:
        Dict con información del proceso de eliminación
    """
    try:
        logger.info("🗑️ Iniciando eliminación de todos los vectores...")

        # Obtener índice
        index = get_pinecone_index()

        # Obtener estadísticas antes
        stats_before = index.describe_index_stats()
        total_vectors_before = stats_before.get("total_vector_count", 0)

        logger.info(f"📊 Vectores encontrados: {total_vectors_before}")

        if total_vectors_before == 0:
            return {
                "status": "success",
                "message": "No hay vectores para eliminar",
                "vectors_deleted": 0,
                "vectors_before": 0,
                "vectors_after": 0,
                "operation": "delete_all_vectors",
            }

        # Eliminar todos los vectores usando delete con namespace vacío
        # Esto elimina TODOS los vectores del índice
        index.delete(delete_all=True)

        logger.info("🗑️ Comando de eliminación enviado")

        # Nota: Pinecone puede tardar unos segundos en procesar la eliminación
        # Las estadísticas pueden no actualizarse inmediatamente

        return {
            "status": "success",
            "message": f"Eliminación iniciada. {total_vectors_before} vectores serán eliminados",
            "vectors_deleted": total_vectors_before,
            "vectors_before": total_vectors_before,
            "note": "La eliminación puede tardar unos segundos en completarse",
            "operation": "delete_all_vectors",
        }

    except Exception as e:
        logger.error(f"❌ Error eliminando vectores: {e}")
        raise HTTPException(500, f"Error deleting vectors: {str(e)}")


def get_index_stats() -> dict[str, Any]:
    """
    📊 Obtiene estadísticas del índice de Pinecone

    Returns:
        Dict con estadísticas del índice
    """
    try:
        logger.info("📊 Obteniendo estadísticas del índice...")

        index = get_pinecone_index()
        stats = index.describe_index_stats()

        # Formatear respuesta
        return {
            "status": "success",
            "total_vectors": stats.get("total_vector_count", 0),
            "dimension": stats.get("dimension", 0),
            "index_fullness": stats.get("index_fullness", 0.0),
            "namespaces": stats.get("namespaces", {}),
            "operation": "get_index_stats",
        }

    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas: {e}")
        raise HTTPException(500, f"Error getting index stats: {str(e)}")
