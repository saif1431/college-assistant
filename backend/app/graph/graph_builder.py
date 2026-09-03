"""Builds and compiles the conversation StateGraph.

A `MemorySaver` checkpointer is attached, keyed at call time by
`thread_id = session_id` (see `services/chat_service.py`), which is what
actually gives the app multi-turn conversation memory — the biggest
behavioral gap in the legacy CLI prototype.
"""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langchain_core.vectorstores import VectorStoreRetriever

from app.graph.nodes import (
    general_node,
    make_classifier_node,
    make_response_node,
    make_retrieval_node,
)
from app.graph.routing import route_query
from app.graph.state import ConversationState
from app.models.domain import QueryType


def build_graph(llm, retrievers: dict[QueryType, VectorStoreRetriever]):
    graph = StateGraph(ConversationState)

    graph.add_node("classifier_node", make_classifier_node(llm))
    graph.add_node("academic_rag_node", make_retrieval_node(retrievers[QueryType.ACADEMIC]))
    graph.add_node("fee_rag_node", make_retrieval_node(retrievers[QueryType.FEE]))
    graph.add_node("general_node", general_node)
    graph.add_node("response_node", make_response_node(llm))

    graph.add_edge(START, "classifier_node")
    graph.add_conditional_edges(
        "classifier_node",
        route_query,
        {
            "academic_rag_node": "academic_rag_node",
            "fee_rag_node": "fee_rag_node",
            "general_node": "general_node",
        },
    )
    graph.add_edge("academic_rag_node", "response_node")
    graph.add_edge("fee_rag_node", "response_node")
    graph.add_edge("general_node", "response_node")
    graph.add_edge("response_node", END)

    return graph.compile(checkpointer=MemorySaver())
