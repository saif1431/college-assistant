from fastapi import APIRouter, Depends

from app.api.deps import get_session_service
from app.schemas.session import SessionCreateRequest, SessionResponse
from app.services.session_service import SessionService

router = APIRouter()


@router.post("/sessions", response_model=SessionResponse, status_code=201)
def create_session(
    payload: SessionCreateRequest,
    service: SessionService = Depends(get_session_service),
) -> SessionResponse:
    session = service.create_session(payload.programme)
    return SessionResponse(
        session_id=session.session_id,
        programme=session.programme,
        created_at=session.created_at,
    )


@router.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: str,
    service: SessionService = Depends(get_session_service),
) -> SessionResponse:
    session = service.get_session(session_id)
    return SessionResponse(
        session_id=session.session_id,
        programme=session.programme,
        created_at=session.created_at,
    )
