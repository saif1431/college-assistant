"""Conditional-edge router.

The legacy prototype's router returned the node *function object* instead of
its registered *string name*, which `add_conditional_edges` silently
ignored (the retrieval nodes never ran). This version returns plain strings,
and `graph_builder.py` additionally passes an explicit path_map so any
future mismatch fails loudly at graph-build time instead of being dropped.
"""

from app.graph.state import ConversationState
from app.models.domain import QueryType


def route_query(state: ConversationState) -> str:
    query_type = state.get("query_type", QueryType.GENERAL.value)

    if query_type == QueryType.ACADEMIC.value:
        return "academic_rag_node"
    if query_type == QueryType.FEE.value:
        return "fee_rag_node"
    return "general_node"
