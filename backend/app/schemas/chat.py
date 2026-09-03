"""API-boundary models for chat endpoints."""

from pydantic import BaseModel, Field

from app.models.domain import QueryType


class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(min_length=1, max_length=2000)


class SourceSnippet(BaseModel):
    """A retrieved chunk cited in an answer, shown in the UI as a source."""

    source: str
    page: int | None = None
    excerpt: str


class ChatResponse(BaseModel):
    message: str
    query_type: QueryType
    sources: list[SourceSnippet] = Field(default_factory=list)
