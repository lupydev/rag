from sqlmodel import SQLModel


class AgentRequest(SQLModel):
    query: str | None = None


class AgentResponse(SQLModel):
    response: str
