from fastapi import APIRouter
from .routes import documents

api_router = APIRouter()

# Incluir rutas de documentos
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
