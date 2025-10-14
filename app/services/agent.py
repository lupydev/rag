from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from app.core.config import settings


chat_model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    max_tokens=100,
    max_completion_tokens=100,
    api_key=settings.OPENAI_API_KEY,
)


def generate_response(query: str):
    print(chat_model.invoke([HumanMessage(content=query)]))
    # return chat_model.invoke([HumanMessage(content=query)])


generate_response("¿Qué es RAG en una sentencia corta?")
