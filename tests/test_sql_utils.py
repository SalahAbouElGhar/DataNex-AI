from utils.sql_utils import clean_sql, fix_informix_sql

def test_fix_informix_sql_moves_first_after_select():
    sql = (
        "SELECT factory_id FROM prod_tbl "
        "FETCH FIRST 5 ROWS ONLY"
    )

    result = clean_sql(fix_informix_sql(sql))

    assert result == (
        "SELECT FIRST 5 factory_id FROM prod_tbl"
    )

def test_fix_informix_sql_handles_lowercase_select():
    sql = (
        "select factory_id from prod_tbl "
        "FETCH FIRST 5 ROWS ONLY"
    )

    result = clean_sql(fix_informix_sql(sql))

    assert "FIRST 5" in result.upper()

def test_fix_informix_sql_preserves_first_in_string_literal():
    sql = "SELECT 'FIRST 10' AS note FROM prod_tbl"

    result = fix_informix_sql(sql)

    assert result == sql

def test_clean_sql_removes_outer_whitespace():
    sql = "  SELECT factory_id FROM prod_tbl  "

    assert clean_sql(sql) == (
        "SELECT factory_id FROM prod_tbl"
    )

def test_sql_helpers_preserve_fetch_text_in_string_literal():
    sql = (
        "SELECT 'FETCH FIRST 10 ROWS ONLY' AS note "
        "FROM prod_tbl"
    )

    result = clean_sql(fix_informix_sql(sql))

    assert result == sql