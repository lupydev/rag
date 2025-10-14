from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API: str = "/api"
    PROJECT_NAME: str = "RAG con LangChain y FastAPI"

    # OPENAI
    OPENAI_API_KEY: str

    # PINECONE
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
