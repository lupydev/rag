from datetime import datetime
from uuid import uuid4
from sqlmodel import SQLModel, Field


class DocumentBase(SQLModel):
    """Modelo base para documentos"""

    filename: str
    content_type: str | None = None
    size_bytes: int | None = None
    upload_date: datetime = Field(default_factory=datetime.now)


class Document(DocumentBase):
    """Modelo de base de datos"""

    id: str  # UUID como string
    document_id: str  # UUID como string
    text_length: int
    chunks_count: int
    vectors_count: int


class DocumentCreate(DocumentBase):
    """Para crear documentos (API request)"""

    pass


class DocumentResponse(DocumentBase):
    """Respuesta de API con info completa"""

    id: int | None = None  # ID de base de datos (opcional)
    document_id: str  # UUID como string
    text_length: int
    chunks_count: int
    vectors_count: int
    status: str = "success"
    message: str = ""
