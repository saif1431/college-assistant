"""LangGraph conversation state.

Pure conversation-flow data — intentionally has no FastAPI/HTTP imports.
`messages` uses the `add_messages` reducer so, combined with a checkpointer
keyed by session id, LangGraph accumulates conversation history across turns
automatically instead of each turn only ever seeing the latest message.
"""

from typing import Any, TypedDict

from langgraph.graph.message import add_messages
from typing_extensions import Annotated


class ConversationState(TypedDict):
    programme: str
    messages: Annotated[list, add_messages]
    query_type: str
    retrieved_context: str
    sources: list[dict[str, Any]]
