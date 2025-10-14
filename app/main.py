from fastapi import FastAPI
from .core.config import settings


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.0.1",
)
