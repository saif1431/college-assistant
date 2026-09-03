"""Orchestrates a single chat turn: look up the session, run the compiled
LangGraph with that session as the conversation thread, and shape the result
into the API's response schema. This is the only layer that knows both the
session store and the graph exist — routes never call the graph directly."""

import logging

from langchain_core.messages import HumanMessage

from app.core.exceptions import LLMError
from app.schemas.chat import ChatResponse, SourceSnippet
from app.services.session_service import SessionService

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, graph, session_service: SessionService) -> None:
        self._graph = graph
        self._session_service = session_service

    def send_message(self, session_id: str, message: str) -> ChatResponse:
        session = self._session_service.get_session(session_id)

        config = {"configurable": {"thread_id": session_id}}
        try:
            result = self._graph.invoke(
                {
                    "programme": session.programme.value,
                    "messages": [HumanMessage(content=message)],
                },
                config=config,
            )
        except Exception as exc:  # noqa: BLE001 - translated to a typed AppError
            logger.exception("Graph execution failed for session %s", session_id)
            raise LLMError() from exc

        self._session_service.touch(session_id)

        answer = result["messages"][-1].content
        sources = [SourceSnippet(**source) for source in result.get("sources", [])]
        return ChatResponse(
            message=answer,
            query_type=result["query_type"],
            sources=sources,
        )
