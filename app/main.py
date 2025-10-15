from fastapi import FastAPI, HTTPException, status
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .core.config import settings
from .core.logging import configure_logging
from .api.main import api_router

# Configurar logging
logger = configure_logging("INFO")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Iniciando aplicación RAG...")
    logger.info("📝 Documentación disponible en: /docs")
    yield
    logger.info("🛑 Cerrando aplicación RAG...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.0.1",
    description="Sistema RAG con FastAPI, LangChain y Pinecone para procesamiento y consulta de documentos",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Manejador global de excepciones
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(
        f"HTTP Exception: {exc.status_code} - {exc.detail} - Path: {request.url.path}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled Exception: {str(exc)} - Path: {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        },
    )


# Incluir rutas de la API
app.include_router(api_router, prefix=settings.API)


@app.get("/")
async def root():
    """Endpoint raíz de la API"""
    return {
        "message": "RAG API with FastAPI and Pinecone",
        "description": "Sistema para procesamiento y consulta de documentos usando IA",
        "docs": "/docs",
        "version": "0.0.1",
        "endpoints": {
            "upload": f"{settings.API}/documents/upload",
            "query": f"{settings.API}/documents/query",
            "health": f"{settings.API}/documents/health",
        },
    }
