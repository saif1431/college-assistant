"""FastAPI application entry point.

All expensive resources (embeddings, FAISS retrievers, the LLM client, the
compiled graph) are built exactly once, in the lifespan handler below, and
stashed on `app.state` — not rebuilt per request, and not built at import
time (which would make the module untestable without live credentials).
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.graph.graph_builder import build_graph
from app.graph.llm import get_llm
from app.rag.retrievers import build_retrievers
from app.repositories.session_repository import InMemorySessionRepository
from app.services.chat_service import ChatService
from app.services.session_service import SessionService

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    logger.info("Building retrievers (loading from disk cache if available)...")
    retrievers = build_retrievers(settings)

    llm = get_llm()
    graph = build_graph(llm=llm, retrievers=retrievers)

    session_repository = InMemorySessionRepository()
    session_service = SessionService(session_repository)
    chat_service = ChatService(graph=graph, session_service=session_service)

    app.state.retrievers = retrievers
    app.state.graph = graph
    app.state.session_service = session_service
    app.state.chat_service = chat_service

    logger.info("Startup complete.")
    yield
    logger.info("Shutting down.")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="College Assistant API",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_router)
    return app


app = create_app()
