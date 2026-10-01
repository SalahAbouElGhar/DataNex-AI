import pytest

from tests.data.regression_test_cases import (
    RANKING_SELECTION_REGRESSION_CASES,
)
from tests.data.test_fixtures import TEST_PRODUCTION_SCHEMA

from reasoning.sql_reasoning import build_query_plan
from compiler.query_ast import build_ast
from compiler.ast_compiler import compile_sql_ast


# ---------------------------------------------------
# Helpers
# ---------------------------------------------------

def normalize_sql(sql):
    """Normalize SQL before semantic substring assertions."""

    if sql is None:
        return ""

    return " ".join(
        line.strip()
        for line in sql.splitlines()
        if line.strip()
    )


def compile_case(case):
    query_plan = build_query_plan(
        case["prompt"],
        TEST_PRODUCTION_SCHEMA,
    )

    ast = build_ast(query_plan)

    sql = compile_sql_ast(
        ast,
        query_plan["schema"],
        query_plan["alias_map"],
    )

    return query_plan, ast, sql


# ---------------------------------------------------
# End-to-end regression suite
# ---------------------------------------------------

@pytest.mark.parametrize(
    "case",
    RANKING_SELECTION_REGRESSION_CASES,
    ids=[case["id"] for case in RANKING_SELECTION_REGRESSION_CASES],
)
def test_ranking_selection_regression(case):
    query_plan, ast, sql = compile_case(case)
    expected = case["expected"]

    # -------------------------
    # Query Plan
    # -------------------------

    assert query_plan["intent"] == expected["intent"]
    assert (
        query_plan["aggregation_function"]
        == expected["aggregation_function"]
    )
    assert query_plan["has_aggregation"] == expected["has_aggregation"]
    assert query_plan["dimensions"] == expected["dimensions"]
    assert query_plan["group_dimensions"] == expected["group_dimensions"]
    assert query_plan["order_strategy"] == expected["order_strategy"]
    assert query_plan["limit_strategy"] == expected["limit_strategy"]

    if "time_filter" in expected:
        assert query_plan["time_filter"] == expected["time_filter"]

    # -------------------------
    # AST
    # -------------------------

    assert ast["group_by"] == expected["ast_group_by"]
    assert ast["order_by"] == expected["ast_order_by"]
    assert ast["limit"] == expected["ast_limit"]

    # -------------------------
    # SQL
    # -------------------------

    normalized = normalize_sql(sql).lower()

    for required in expected["sql_required"]:
        assert required.lower() in normalized, (
            f"Missing expected SQL fragment {required!r}\n"
            f"Generated SQL: {sql}"
        )

    for forbidden in expected["sql_forbidden"]:
        assert forbidden.lower() not in normalized, (
            f"Forbidden SQL fragment {forbidden!r} was generated.\n"
            f"Generated SQL: {sql}"
        )
