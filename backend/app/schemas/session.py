"""API-boundary models for session endpoints."""

from datetime import datetime

from pydantic import BaseModel

from app.models.domain import Programme


class SessionCreateRequest(BaseModel):
    programme: Programme


class SessionResponse(BaseModel):
    session_id: str
    programme: Programme
    created_at: datetime
