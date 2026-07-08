import pytest

from tests.data.test_cases import AST_COMPILER_TEST_CASES

from compiler.ast_compiler import compile_sql_ast

#from ai.sql_reasoning import ( parse_multi_table_schema   )

#-----------------------------------------------
#RAW_SCHEMA = """
#table name prod_tbl
#column names
#factory_id
#prod_id
#prod_date
#qty
#"""

#SCHEMA = parse_multi_table_schema(RAW_SCHEMA)
#print("SCHEMA = " ,SCHEMA)
#-----------------------------------------------
def normalize_sql(sql):
    """
    Normalize SQL before comparison.
    """

    if sql is None:
        return ""

    lines = []

    for line in sql.splitlines():

        line = line.strip()

        if line:

            lines.append(line)

    return "\n".join(lines)
#-----------------------------------------------

def compile_case(case):
    
    input_data = case["input"]
#    print("ALISS MAP = ",input_data["alias_map"])
    return compile_sql_ast(
        input_data["ast"],
        input_data["schema"],
        input_data["alias_map"]
    )
#-----------------------------------------------

@pytest.mark.parametrize(
    "case",
    AST_COMPILER_TEST_CASES,
    ids=[case["name"] for case in AST_COMPILER_TEST_CASES]
)
#-----------------------------------------------
def test_ast_compiler(case):

    sql = compile_case(case)

#    print("\nGenerated SQL:")
#    print(sql)

    expected_sql = case["expected"]["sql"]

    if expected_sql is None:
        pytest.skip(
            "Golden SQL has not been approved yet."
        )

    assert ( normalize_sql(sql) ==  normalize_sql(expected_sql) )
#-----------------------------------------------