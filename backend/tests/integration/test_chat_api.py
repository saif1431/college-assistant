"""API-layer integration tests.

These build a lightweight FastAPI app around just `api_router`, with fake
service implementations injected via `dependency_overrides` — no real graph,
LLM, or embeddings involved, so no network access or API key is required to
run these tests.
"""

from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.deps import get_chat_service, get_session_service
from app.api.v1.router import api_router
from app.core.exceptions import SessionNotFoundError, register_exception_handlers
from app.models.domain import Programme, QueryType
from app.repositories.session_repository import Session
from app.schemas.chat import ChatResponse


class FakeSessionService:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def create_session(self, programme: Programme) -> Session:
        session = Session(
            session_id="test-session-id",
            programme=programme,
            created_at=datetime.now(timezone.utc),
            last_active_at=datetime.now(timezone.utc),
        )
        self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Session:
        session = self._sessions.get(session_id)
        if session is None:
            raise SessionNotFoundError()
        return session

    def touch(self, session_id: str) -> None:
        pass


class FakeChatService:
    """Delegates session lookup to the (fake) session service, like the real
    ChatService does, so the 404 path is exercised realistically."""

    def __init__(self, session_service: FakeSessionService) -> None:
        self._session_service = session_service
        self.last_call: tuple[str, str] | None = None

    def send_message(self, session_id: str, message: str) -> ChatResponse:
        self._session_service.get_session(session_id)
        self.last_call = (session_id, message)
        return ChatResponse(message="This is a fake answer.", query_type=QueryType.FEE, sources=[])


def _build_test_app(session_service: FakeSessionService, chat_service: FakeChatService) -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(api_router)
    app.dependency_overrides[get_session_service] = lambda: session_service
    app.dependency_overrides[get_chat_service] = lambda: chat_service
    return app


def test_create_session_then_chat_roundtrip():
    session_service = FakeSessionService()
    chat_service = FakeChatService(session_service)
    client = TestClient(_build_test_app(session_service, chat_service))

    create_resp = client.post(
        "/api/v1/sessions", json={"programme": Programme.COMPUTER_SCIENCE.value}
    )
    assert create_resp.status_code == 201
    session_id = create_resp.json()["session_id"]

    chat_resp = client.post(
        "/api/v1/chat", json={"session_id": session_id, "message": "What is the fee?"}
    )
    assert chat_resp.status_code == 200
    body = chat_resp.json()
    assert body["message"] == "This is a fake answer."
    assert body["query_type"] == "fee"
    assert chat_service.last_call == (session_id, "What is the fee?")


def test_chat_with_unknown_session_returns_404():
    session_service = FakeSessionService()
    chat_service = FakeChatService(session_service)
    client = TestClient(_build_test_app(session_service, chat_service))

    resp = client.post("/api/v1/chat", json={"session_id": "does-not-exist", "message": "Hi"})
    assert resp.status_code == 404


def test_health_endpoint_reports_not_ready_without_lifespan():
    session_service = FakeSessionService()
    chat_service = FakeChatService(session_service)
    client = TestClient(_build_test_app(session_service, chat_service))

    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "starting", "ready": False}
