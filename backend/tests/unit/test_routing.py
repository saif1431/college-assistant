"""Regression tests for the routing bug in the legacy prototype: the router
returned node *function objects* instead of their registered *string
names*, so `add_conditional_edges` silently dropped every transition and
retrieval never ran."""

from app.graph.routing import route_query


def test_route_query_returns_node_name_strings_for_each_category():
    assert route_query({"query_type": "academic"}) == "academic_rag_node"
    assert route_query({"query_type": "fee"}) == "fee_rag_node"
    assert route_query({"query_type": "general"}) == "general_node"


def test_route_query_defaults_to_general_for_unknown_category():
    assert route_query({"query_type": "something_unexpected"}) == "general_node"


def test_route_query_result_is_a_plain_string():
    result = route_query({"query_type": "fee"})
    assert isinstance(result, str)
    assert not callable(result)
