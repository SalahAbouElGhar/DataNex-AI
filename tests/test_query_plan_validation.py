import pytest

from validators.validators import validate_query_plan
# ------------------------------------------------------

@pytest.mark.parametrize(
    "query_plan",
    [
        None,
        [],
        "invalid query plan",
    ],
)
# ------------------------------------------------------
def test_validate_query_plan_rejects_invalid_input(query_plan):
    result = validate_query_plan(query_plan)

    assert result["valid"] is False
    assert result["errors"]
    assert result["warnings"] == []
# ------------------------------------------------------

def test_validate_query_plan_rejects_incomplete_join():
    query_plan = {
        "has_aggregation": False,
        "dimensions": [],
        "measures": [],
        "required_tables": ["prod_tbl"],
        "join_plan": {
            "joins": [
                {
                    "left_table": "prod_tbl",
                }
            ]
        },
    }

    result = validate_query_plan(query_plan)

    assert result["valid"] is False
    assert result["errors"]
    assert any(
        "right_table" in error
        for error in result["errors"]
    )
# ------------------------------------------------------

def test_validate_query_plan_rejects_none_joins():
    query_plan = {
        "has_aggregation": False,
        "dimensions": [],
        "measures": [],
        "required_tables": ["prod_tbl"],
        "join_plan": {
            "joins": None,
        },
    }

    result = validate_query_plan(query_plan)

    assert result["valid"] is False
    assert result["errors"]
# ------------------------------------------------------
def test_validate_query_plan_accepts_valid_aggregated_plan():
    query_plan = {
        "has_aggregation": True,
        "dimensions": ["factory_id"],
        "measures": ["qty"],
        "required_tables": ["prod_tbl"],
        "join_plan": {
            "joins": [],
        },
    }

    result = validate_query_plan(query_plan)

    assert result["valid"] is True
    assert result["errors"] == []
    assert result["warnings"] == []
# ------------------------------------------------------

def test_validate_query_plan_accepts_valid_join_plan():
    query_plan = {
        "has_aggregation": False,
        "dimensions": ["factory_id"],
        "measures": [],
        "required_tables": [
            "prod_tbl",
            "factory_tbl",
        ],
        "join_plan": {
            "joins": [
                {
                    "left_table": "prod_tbl",
                    "right_table": "factory_tbl",
                }
            ],
        },
    }

    result = validate_query_plan(query_plan)

    assert result["valid"] is True
    assert result["errors"] == []
    assert result["warnings"] == []