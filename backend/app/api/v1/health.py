from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
def health(request: Request) -> dict:
    ready = getattr(request.app.state, "graph", None) is not None
    return {"status": "ok" if ready else "starting", "ready": ready}
