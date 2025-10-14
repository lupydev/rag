from fastapi import UploadFile, HTTPException, status
from pinecone import Pinecone
from llama_index.core import (
    VectorStoreIndex,
    Document,
    StorageContext,
)
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from core.config import settings
from .text_extraction import extract_text_buffer

pc = Pinecone(api_key=settings.PINECONE_API_KEY)
pinecone_index = pc.Index(settings.PINECONE_INDEX_NAME)

vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

llm = OpenAI(model="gpt-4o-mini")
embed_model = OpenAIEmbedding()


def create_vector_index(document: UploadFile):
    text = extract_text_buffer(document)
    documents = [Document(text=text)]
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embed_model,
        llm=llm,
    )
    index.storage_context.persist(persist_dir="rag_index")
    return HTTPException(
        status_code=status.HTTP_200_OK,
        detail=f"{document.filename} processed and created",
    )
