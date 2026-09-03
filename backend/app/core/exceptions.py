"""Application error hierarchy and FastAPI exception handlers.

Business/service/graph/RAG code raises these typed errors; the API layer
never has to know *why* something failed, only how to translate it into an
HTTP response. Internal details (stack traces, prompts, API keys) are never
sent to the client — they're logged server-side only.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base class for all application-raised errors."""

    status_code: int = 500
    detail: str = "Internal server error"

    def __init__(self, detail: str | None = None) -> None:
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


class SessionNotFoundError(AppError):
    status_code = 404
    detail = "Session not found"


class RetrievalError(AppError):
    status_code = 502
    detail = "Failed to retrieve context from the knowledge base"


class LLMError(AppError):
    status_code = 502
    detail = "Failed to generate a response"


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        logger.warning("AppError on %s %s: %s", request.method, request.url.path, exc.detail)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
