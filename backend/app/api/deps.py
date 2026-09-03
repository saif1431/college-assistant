"""Shared FastAPI dependency providers.

Services are built once at startup (see `main.py`'s lifespan) and stashed on
`app.state`; these functions just hand them to route handlers. Route
handlers depend on these, never on `app.state` directly, so tests can swap
in fakes via `app.dependency_overrides`.
"""

from fastapi import Request

from app.services.chat_service import ChatService
from app.services.session_service import SessionService


def get_session_service(request: Request) -> SessionService:
    return request.app.state.session_service


def get_chat_service(request: Request) -> ChatService:
    return request.app.state.chat_service
