from datetime import datetime
from pydantic import field_validator
from sqlmodel import SQLModel, Field


class QueryRequest(SQLModel):
    """Request para consultas"""

    query: str = Field(min_length=1, max_length=1000)
    max_results: int = Field(default=5, ge=1, le=20)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)

    @field_validator("query")
    @classmethod
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError("El query no puede estar vacío o solo espacios en blanco")
        return v.strip()


class QuerySource(SQLModel):
    """Fuente de información para respuesta"""

    document_id: str  # UUID como string
    filename: str
    chunk_id: str
    score: float
    content_preview: str


class QueryResponse(SQLModel):
    """Respuesta de consulta"""

    query: str
    answer: str
    sources: list[QuerySource] = []
    confidence: str  # 'high', 'medium', 'low', 'none'

    # Metadata opcional
    guard_rail_triggered: str | None = None
    average_similarity: float | None = None
    context_chunks_used: int | None = None


class QueryStats(SQLModel):
    """Estadísticas de consultas (opcional para aprendizaje)"""

    query: str
    response_length: int
    sources_found: int
    confidence: str
    processing_time_ms: float
    timestamp: datetime = Field(default_factory=datetime.now)
