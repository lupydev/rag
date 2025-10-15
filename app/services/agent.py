from langchain_openai import ChatOpenAI
from ..core.config import settings


def create_llm(temperature: float = 0.7) -> ChatOpenAI:
    """Crea cliente LLM"""
    return ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        model="gpt-4o-mini",
        temperature=temperature,
    )
