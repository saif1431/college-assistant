"""Session storage abstraction.

`SessionRepository` is a `Protocol` so the service layer depends on an
interface, not a concrete store. `InMemorySessionRepository` is enough for a
single-process deployment; swapping in a Redis- or Postgres-backed
implementation later does not require touching `SessionService`.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from app.models.domain import Programme


@dataclass
class Session:
    session_id: str
    programme: Programme
    created_at: datetime
    last_active_at: datetime


class SessionRepository(Protocol):
    def create(self, session: Session) -> None: ...

    def get(self, session_id: str) -> Session | None: ...

    def touch(self, session_id: str, at: datetime) -> None: ...


class InMemorySessionRepository:
    """Process-local session store. Lost on restart — acceptable at this
    scope; see docs/architecture.md for the swap-out path."""

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def create(self, session: Session) -> None:
        self._sessions[session.session_id] = session

    def get(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)

    def touch(self, session_id: str, at: datetime) -> None:
        session = self._sessions.get(session_id)
        if session is not None:
            session.last_active_at = at
