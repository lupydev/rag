from datetime import datetime
from typing import Any
from uuid import uuid4

from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document as LangChainDocument
from ..core.config import settings


def create_embeddings() -> OpenAIEmbeddings:
    """Crea cliente de embeddings"""
    return OpenAIEmbeddings(
        api_key=settings.OPENAI_API_KEY, model="text-embedding-3-small"
    )


def create_text_splitter(
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> RecursiveCharacterTextSplitter:
    """Crea text splitter configurado"""
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=[
            "\n\n",
            "\n",
            " ",
            ".",
            ",",
            "",
            "",
        ],
    )


def create_text_chunks(text: str, filename: str) -> list[dict[str, Any]]:
    """
    Divide texto en chunks con metadata

    Args:
        text: Texto a dividir
        filename: Nombre del archivo

    Returns:
        Lista de chunks con metadata
    """
    splitter = create_text_splitter()
    doc_id = str(uuid4())  # Convertir a string inmediatamente

    # Crear documento de LangChain
    langchain_doc = LangChainDocument(
        page_content=text,
        metadata={
            "filename": filename,
            "document_id": doc_id,  # Ya es string
            "upload_date": datetime.now().isoformat(),
        },
    )

    # Dividir en chunks
    chunks = splitter.split_documents([langchain_doc])

    # Agregar metadata específica de chunk
    result = []
    for i, chunk in enumerate(chunks):
        chunk_data = {
            "document_id": doc_id,  # Ya es string
            "chunk_id": f"{doc_id}_{i}",
            "chunk_index": i,
            "text": chunk.page_content,
            "filename": filename,
            "metadata": chunk.metadata,
        }
        result.append(chunk_data)

    return result


def create_vectors_from_chunks(chunks: list[dict[str, Any]]):
    """
    Convierte chunks en vectores para Pinecone

    Args:
        chunks: Lista de chunks con metadata

    Returns:
        Lista de vectores para Pinecone
    """
    embeddings = create_embeddings()
    vectors = []

    for chunk in chunks:
        # Generar embedding
        embedding = embeddings.embed_query(chunk["text"])

        # Crear vector para Pinecone
        vector = {
            "id": chunk["chunk_id"],
            "values": embedding,
            "metadata": {
                "text": chunk["text"],
                "filename": chunk["filename"],
                "document_id": str(chunk["document_id"]),  # Asegurar que sea string
                "chunk_index": chunk["chunk_index"],
            },
        }
        vectors.append(vector)

    return vectors
