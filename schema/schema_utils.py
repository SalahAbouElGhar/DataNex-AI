# schema_utils.py
from core.config import (
    BUSINESS_TERMS,
    MEASURE_KEYWORDS,
    DATE_COLUMN_KEYWORDS,
    LIMIT_PATTERNS,
    RELATIONSHIP_SUFFIXES,
    RELATIONSHIP_HINTS,
    DISPLAY_SUFFIXES
)
#-------------------------------------------------------
def extract_all_columns(schema):

    all_columns = []

    for table, cols in schema["tables"].items():
        all_columns.extend(cols)

    return list(set(all_columns))

#-------------------------------------------------------
def get_column_owner(column,schema):

    for table, cols in schema["tables"].items():

        if column in cols:

            return table

    return None
#------------------------------------------------
def get_columns_for_tables(
    schema,
    required_tables
):

    columns = []

    for table in required_tables:

        if table in schema["tables"]:

            columns.extend(
                schema["tables"][table]
            )

    return list(
        dict.fromkeys(columns)
    )
#-----------------------------------------------------------
def build_aggregation_alias(
    function_name,
    measure,
    query_plan=None
):
    count_target = None
    if (
            function_name.upper() == "COUNT"
            and query_plan is not None
        ):
            count_target = query_plan.get(
                "count_target"
            )
    
    if count_target:

        if count_target["type"] == "rows":
    
            return "row_count"
    
        if count_target["type"] == "distinct":
    
            root = (
                count_target["column"]
                .replace("_id", "")
            )
    
            return f"{root}_count"
    
    if not function_name:
        return measure

    match function_name.upper():

        case "SUM":
            prefix = "total"

        case "AVG":
            prefix = "average"

        case "MAX":
            prefix = "maximum"

        case "MIN":
            prefix = "minimum"

        case "COUNT":
            prefix = "count"

        case _:
            prefix = function_name.lower()

    return f"{prefix}_{measure}"
#-----------------------------------------------------------
# Relationship Intelligence Helpers
#-----------------------------------------------------------
def is_relationship_column(column):

    column = column.lower()

    return any(
        column.endswith(suffix)
        for suffix in RELATIONSHIP_SUFFIXES
    )
#-----------------------------------------------------------
def strip_relationship_suffix(
    column
):

    column = column.lower()

    for suffix in RELATIONSHIP_SUFFIXES:

        if column.endswith(suffix):

            return column[:-len(suffix)]

    return column
#-----------------------------------------------------------
def extract_relationship_columns(
    all_columns
):

    relationship_columns = []

    for col in all_columns:

        if is_relationship_column(col):
            relationship_columns.append(col)

    return relationship_columns
#--------------------------------------------------
def extract_id_columns(
    all_columns
):

    return extract_relationship_columns(
        all_columns
    )
#--------------------------------------------------
def is_display_column(column):

    column = column.lower()

    return any(
        column.endswith(suffix)
        for suffix in DISPLAY_SUFFIXES
    )
#--------------------------------------------------
def strip_display_suffix(column):

    column = column.lower()

    for suffix in DISPLAY_SUFFIXES:

        if column.endswith(suffix):

            return column[:-len(suffix)]

    return column
#--------------------------------------------------

def extract_display_columns(
    all_columns
):

    return [
        col
        for col in all_columns
        if is_display_column(col)
    ]
#--------------------------------------------------
def build_display_targets(
        schema,
        BUSINESS_TERMS
):

    all_columns = extract_all_columns(
        schema
    )

    display_columns = (
        extract_display_columns(
            all_columns
        )
    )

    display_targets = {}

    for col in display_columns:

        root = strip_display_suffix(
            col
        )

        for business_term, aliases in BUSINESS_TERMS.items():

            for alias in aliases:

                if (
                    root in alias
                    or
                    alias in root
                ):

                    display_targets[
                        business_term
                    ] = col

                    break

    return display_targets
#--------------------------------------------------

#--------------------------------------------------