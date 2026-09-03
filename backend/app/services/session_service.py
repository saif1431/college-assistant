"""Session lifecycle — creation and lookup. Storage details are delegated to
a `SessionRepository`, not implemented here."""

import uuid
from datetime import datetime, timezone

from app.core.exceptions import SessionNotFoundError
from app.models.domain import Programme
from app.repositories.session_repository import Session, SessionRepository


class SessionService:
    def __init__(self, repository: SessionRepository) -> None:
        self._repository = repository

    def create_session(self, programme: Programme) -> Session:
        now = datetime.now(timezone.utc)
        session = Session(
            session_id=str(uuid.uuid4()),
            programme=programme,
            created_at=now,
            last_active_at=now,
        )
        self._repository.create(session)
        return session

    def get_session(self, session_id: str) -> Session:
        session = self._repository.get(session_id)
        if session is None:
            raise SessionNotFoundError(f"No session found for id '{session_id}'")
        return session

    def touch(self, session_id: str) -> None:
        self._repository.touch(session_id, datetime.now(timezone.utc))
