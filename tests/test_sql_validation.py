import pytest

from validators.validators import validate_sql


def test_accepts_plain_select():
    sql = "SELECT factory_id FROM prod_tbl"

    assert validate_sql(
        sql,
        {"has_aggregation": False},
    ) is True


def test_accepts_scalar_aggregate_without_group_by():
    sql = "SELECT SUM(qty) AS total_qty FROM prod_tbl"

    assert validate_sql(
        sql,
        {
            "has_aggregation": True,
            "dimensions": [],
        },
    ) is True


def test_requires_group_by_for_aggregate_with_dimensions():
    sql = (
        "SELECT factory_id, SUM(qty) AS total_qty "
        "FROM prod_tbl"
    )

    with pytest.raises(Exception, match="GROUP BY"):
        validate_sql(
            sql,
            {
                "has_aggregation": True,
                "dimensions": ["factory_id"],
            },
        )


def test_accepts_grouped_aggregate():
    sql = (
        "SELECT factory_id, SUM(qty) AS total_qty "
        "FROM prod_tbl GROUP BY factory_id"
    )

    assert validate_sql(
        sql,
        {
            "has_aggregation": True,
            "dimensions": ["factory_id"],
        },
    ) is True


def test_rejects_non_select_statement():
    with pytest.raises(Exception):
        validate_sql(
            "DELETE FROM prod_tbl",
            {"has_aggregation": False},
        )


def test_accepts_column_name_containing_forbidden_keyword():
    sql = "SELECT updated_at FROM prod_tbl"

    assert validate_sql(
        sql,
        {"has_aggregation": False},
    ) is True