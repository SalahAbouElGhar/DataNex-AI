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

def test_validate_sql_allows_forbidden_words_in_string_literal():
    sql = (
        "SELECT 'UPDATE DELETE INSERT DROP' AS note "
        "FROM prod_tbl"
    )

    assert validate_sql(
        sql,
        {"has_aggregation": False},
    ) is True

def test_validate_sql_allows_forbidden_words_in_comments():
    sql = (
        "SELECT factory_id FROM prod_tbl "
        "/* DELETE UPDATE INSERT DROP */"
    )

    assert validate_sql(
        sql,
        {"has_aggregation": False},
    ) is True

def test_validate_sql_still_rejects_forbidden_keyword():
    sql = (
        "SELECT factory_id FROM prod_tbl; "
        "DELETE FROM prod_tbl"
    )

    with pytest.raises(ValueError, match="Forbidden keyword: DELETE"):
        validate_sql(
            sql,
            {"has_aggregation": False},
        )

def test_rejects_multiple_select_statements():
    sql = (
        "SELECT factory_id FROM prod_tbl; "
        "SELECT qty FROM prod_tbl"
    )

    with pytest.raises(
        ValueError,
        match="Only one SQL statement is allowed",
    ):
        validate_sql(
            sql,
            {"has_aggregation": False},
        )

def test_accepts_single_select_with_trailing_semicolon():
    sql = "SELECT factory_id FROM prod_tbl;"

    assert validate_sql(
        sql,
        {"has_aggregation": False},
    ) is True

def test_accepts_semicolon_inside_string_literal():
    sql = "SELECT 'alpha; beta' AS note FROM prod_tbl"

    assert validate_sql(
        sql,
        {"has_aggregation": False},
    ) is True

def test_accepts_semicolon_inside_comment():
    sql = (
        "SELECT factory_id FROM prod_tbl "
        "/* separator; SELECT qty FROM prod_tbl */"
    )

    assert validate_sql(
        sql,
        {"has_aggregation": False},
    ) is True