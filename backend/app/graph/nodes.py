"""LangGraph node functions.

Each node is a pure function of `(state) -> partial state update`. Nodes
that need a collaborator (an LLM, a retriever) are built by small factory
functions instead of reaching for a module-level global — `graph_builder.py`
is the only place that wires concrete instances in, which keeps this module
easy to unit test with fakes.
"""

import logging
from pathlib import Path
from typing import Callable

from langchain_core.messages import SystemMessage
from langchain_core.vectorstores import VectorStoreRetriever

from app.core.exceptions import LLMError, RetrievalError
from app.graph.prompts import CLASSIFICATION_PROMPT, build_response_system_prompt
from app.graph.state import ConversationState
from app.models.domain import QueryType

logger = logging.getLogger(__name__)

NodeFn = Callable[[ConversationState], dict]


def make_classifier_node(llm) -> NodeFn:
    def classifier_node(state: ConversationState) -> dict:
        last_message = state["messages"][-1].content
        prompt = CLASSIFICATION_PROMPT.format(query=last_message)

        try:
            response = llm.invoke(prompt)
        except Exception as exc:  # noqa: BLE001 - translated to a typed AppError
            logger.exception("Classification call failed")
            raise LLMError() from exc

        category = response.content.strip().lower()
        if "academic" in category:
            query_type = QueryType.ACADEMIC.value
        elif "fee" in category:
            query_type = QueryType.FEE.value
        else:
            query_type = QueryType.GENERAL.value

        return {"query_type": query_type}

    return classifier_node


def make_retrieval_node(retriever: VectorStoreRetriever) -> NodeFn:
    def retrieval_node(state: ConversationState) -> dict:
        query = state["messages"][-1].content

        try:
            docs = retriever.invoke(query)
        except Exception as exc:  # noqa: BLE001 - translated to a typed AppError
            logger.exception("Retrieval failed")
            raise RetrievalError() from exc

        context = "\n\n".join(doc.page_content for doc in docs)
        sources = [
            {
                "source": Path(doc.metadata.get("source", "unknown")).name,
                "page": (
                    doc.metadata["page"] + 1 if doc.metadata.get("page") is not None else None
                ),
                "excerpt": doc.page_content[:200],
            }
            for doc in docs
        ]
        return {"retrieved_context": context, "sources": sources}

    return retrieval_node


def general_node(state: ConversationState) -> dict:
    """No retrieval needed — the response node answers from the LLM's own
    knowledge when query_type == 'general'."""
    return {"retrieved_context": "", "sources": []}


def make_response_node(llm) -> NodeFn:
    def response_node(state: ConversationState) -> dict:
        programme = state.get("programme", "Unknown")
        context = state.get("retrieved_context", "")
        query_type = state.get("query_type", QueryType.GENERAL.value)

        system_prompt = build_response_system_prompt(programme, context, query_type)
        # Full accumulated history (not just the latest message) is sent so the
        # model actually has multi-turn context, not just storage of it.
        conversation = [SystemMessage(content=system_prompt), *state["messages"]]

        try:
            response = llm.invoke(conversation)
        except Exception as exc:  # noqa: BLE001 - translated to a typed AppError
            logger.exception("Response generation failed")
            raise LLMError() from exc

        return {"messages": [response]}

    return response_node
