# schema_utils.py
from core.config import (
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
def build_semantic_targets(domain_config):

    return domain_config.get(
        "semantic_entities",
        {}
    ).copy()
#--------------------------------------------------

def build_display_targets(domain_config):

    return domain_config.get(
        "display_entities",
        {}
    ).copy()
#--------------------------------------------------
def build_alias_map(required_tables):

    alias_map = {}

    used_aliases = set()

    for table in required_tables:

        # -------------------------
        # DEFAULT ALIAS
        # -------------------------

        parts = table.split("_")

        alias = "".join(
            part[0]
            for part in parts
        ).lower()

        # -------------------------
        # HANDLE DUPLICATES
        # -------------------------

        counter = 1

        original = alias

        while alias in used_aliases:

            alias = f"{original}{counter}"

            counter += 1

        alias_map[table] = alias

        used_aliases.add(alias)

    return alias_map
#-------------------------------------------
def extract_measure_columns(columns):

    return [
        col
        for col in columns
        if any(
            keyword in col.lower()
            for keyword in MEASURE_KEYWORDS
        )
    ]
#------------------------------------------------
def extract_date_columns(columns):

    return [
        col
        for col in columns
        if any(
            keyword in col.lower()
            for keyword in DATE_COLUMN_KEYWORDS
        )
    ]
