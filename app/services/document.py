from typing import Any
import logging
from app.services.agent import create_llm
from app.services.embeddings import create_embeddings
from app.services.pinecone import get_pinecone_index
from app.schemas.query import QueryResponse, QuerySource


# Setup
logging.basicConfig(level=logging.INFO)


def query_documents(
    query: str,
    max_results: int = 5,
    similarity_threshold: float = 0.7,
) -> QueryResponse:
    """
    Procesa una consulta completa con guard rails

    Función principal que orquesta todo:
    1. Valida entrada
    2. Busca vectores similares
    3. Aplica guard rails
    4. Genera respuesta con LLM

    Args:
        query: Pregunta del usuario
        max_results: Máximo de resultados
        similarity_threshold: Umbral de similitud

    Returns:
        QueryResponse con respuesta completa
    """

    # 1. Validaciones básicas (guard rails simples)
    if not query.strip():
        return QueryResponse(
            query=query,
            answer="Por favor proporciona una pregunta válida.",
            confidence="none",
            guard_rail_triggered="empty_query",
        )

    if len(query.strip()) < 3:
        return QueryResponse(
            query=query,
            answer="La pregunta es demasiado corta. Mínimo 3 caracteres.",
            confidence="low",
            guard_rail_triggered="short_query",
        )

    # 2. Buscar documentos similares
    search_results = search_similar_documents(query, max_results)

    # 3. Filtrar por umbral
    relevant_results = filter_by_similarity(search_results, similarity_threshold)

    # 4. Guard rail: sin resultados relevantes
    if not relevant_results:
        max_score = max([r.get("score", 0) for r in search_results], default=0)
        return QueryResponse(
            query=query,
            answer=f"No encontré información suficientemente relevante (máx: {max_score:.3f}, requerido: {similarity_threshold:.3f})",
            confidence="low",
            guard_rail_triggered="low_similarity",
        )

    # 5. Crear contexto y generar respuesta
    context = create_context_from_results(relevant_results)
    answer = generate_answer_with_llm(query, context)

    # 6. Guard rail: respuesta demasiado genérica
    if is_answer_too_generic(answer):
        return QueryResponse(
            query=query,
            answer="No puedo dar una respuesta específica con la información disponible.",
            sources=results_to_sources(relevant_results),
            confidence="low",
            guard_rail_triggered="generic_response",
        )

    # 7. Respuesta exitosa
    confidence = calculate_confidence(relevant_results)
    sources = results_to_sources(relevant_results)
    avg_similarity = sum(r["score"] for r in relevant_results) / len(relevant_results)

    return QueryResponse(
        query=query,
        answer=answer,
        sources=sources,
        confidence=confidence,
        average_similarity=avg_similarity,
        context_chunks_used=len(relevant_results),
    )


def search_similar_documents(query: str, k: int) -> list[dict[str, Any]]:
    """Busca documentos similares en Pinecone"""
    embeddings = create_embeddings()
    index = get_pinecone_index()

    # Generar embedding de la query
    query_embedding = embeddings.embed_query(query)

    # Buscar en Pinecone
    results = index.query(vector=query_embedding, top_k=k, include_metadata=True)

    return results.get("matches", [])


def filter_by_similarity(
    results: list[dict[str, Any]], threshold: float
) -> list[dict[str, Any]]:
    """Filtra resultados por umbral de similitud"""
    return [r for r in results if r.get("score", 0) >= threshold]


def create_context_from_results(results: list[dict[str, Any]]) -> str:
    """Crea contexto combinado de los resultados"""
    contexts = []
    for result in results:
        text = result.get("metadata", {}).get("text", "")
        if text.strip():
            contexts.append(text.strip())

    return "\n\n".join(contexts)


def generate_answer_with_llm(query: str, context: str) -> str:
    """Genera respuesta usando LLM con prompt estricto"""
    llm = create_llm()

    prompt = f"""Eres un asistente que SOLO responde basándose en el contexto proporcionado.

REGLAS ESTRICTAS:
1. SOLO usa información del contexto
2. Si no está en el contexto, di "No tengo esa información"
3. NO inventes ni uses conocimiento externo
4. Sé específico y cita el contexto relevante

CONTEXTO:
{context}

PREGUNTA: {query}

RESPUESTA:"""

    response = llm.invoke(prompt)
    return response.content if hasattr(response, "content") else str(response)


def is_answer_too_generic(answer: str) -> bool:
    """Detecta respuestas demasiado genéricas"""
    generic_phrases = [
        "no tengo información específica",
        "no puedo proporcionar detalles",
        "consulta los documentos",
        "información no es suficiente",
    ]

    answer_lower = answer.lower()
    return (
        any(phrase in answer_lower for phrase in generic_phrases)
        or len(answer.strip()) < 20
    )


def calculate_confidence(results: list[dict[str, Any]]) -> str:
    """Calcula nivel de confianza basado en resultados"""
    if not results:
        return "none"

    avg_score = sum(r.get("score", 0) for r in results) / len(results)

    if avg_score >= 0.85 and len(results) >= 3:
        return "high"
    elif avg_score >= 0.75 and len(results) >= 2:
        return "medium"
    else:
        return "low"


def results_to_sources(results: list[dict[str, Any]]) -> list[QuerySource]:
    """Convierte resultados de Pinecone a QuerySource"""
    sources = []

    for result in results:
        metadata = result.get("metadata", {})
        text = metadata.get("text", "")

        source = QuerySource(
            document_id=metadata.get("document_id", ""),
            filename=metadata.get("filename", ""),
            chunk_id=result.get("id", ""),
            score=result.get("score", 0.0),
            content_preview=text[:200] + "..." if len(text) > 200 else text,
        )
        sources.append(source)

    return sources
