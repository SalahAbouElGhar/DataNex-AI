from core.messages import MESSAGES
import re
# -----------------------------------------------
def validate_prompt(prompt):
    if not isinstance(prompt, str):
        return MESSAGES["PROMPT_INVALID"]

    if not prompt.strip():
        return MESSAGES["PROMPT_INVALID"]

    return None
# -----------------------------------------------
def validate_query_plan(query_plan):

    errors = []
    warnings = []

    # --------------------------------------------
    # Validate the query plan itself
    # --------------------------------------------
    if not isinstance(query_plan, dict):
        return {
            "valid": False,
            "errors": ["Query plan must be a dictionary"],
            "warnings": warnings,
        }

    # --------------------------------------------
    # Validate collection fields
    # --------------------------------------------
    dimensions = query_plan.get("dimensions", [])
    measures = query_plan.get("measures", [])
    required_tables = query_plan.get("required_tables", [])

    if not isinstance(dimensions, list):
        errors.append("'dimensions' must be a list")
        dimensions = []

    if not isinstance(measures, list):
        errors.append("'measures' must be a list")
        measures = []

    if not isinstance(required_tables, list):
        errors.append("'required_tables' must be a list")
        required_tables = []

    has_aggregation = query_plan.get("has_aggregation")

    # --------------------------------------------
    # A measure cannot also be a dimension
    # --------------------------------------------
    for measure in measures:
        if measure in dimensions:
            errors.append(
                f"Column '{measure}' cannot be both measure and dimension"
            )

    # --------------------------------------------
    # Validate join plan
    # --------------------------------------------
    join_plan = query_plan.get("join_plan", {})

    if join_plan is None:
        join_plan = {}

    elif not isinstance(join_plan, dict):
        errors.append("'join_plan' must be a dictionary")
        join_plan = {}

    # An omitted joins field means there are no joins.
    if "joins" not in join_plan:
        joins = []

    else:
        joins = join_plan["joins"]

        if not isinstance(joins, list):
            errors.append("Join plan 'joins' must be a list")
            joins = []

    # --------------------------------------------
    # Validate each join safely
    # --------------------------------------------
    for index, join in enumerate(joins, start=1):

        if not isinstance(join, dict):
            errors.append(
                f"Join #{index} must be a dictionary"
            )
            continue

        left_table = join.get("left_table")
        right_table = join.get("right_table")

        if not left_table:
            errors.append(
                f"Join #{index} is missing left_table"
            )

        elif left_table not in required_tables:
            errors.append(
                f"Join references left_table '{left_table}' "
                "not present in required_tables"
            )

        if not right_table:
            errors.append(
                f"Join #{index} is missing right_table"
            )

        elif right_table not in required_tables:
            errors.append(
                f"Join references right_table '{right_table}' "
                "not present in required_tables"
            )

    # --------------------------------------------
    # Aggregation requires at least one measure
    # --------------------------------------------
    if has_aggregation and not measures:
        errors.append("Aggregation requires measure")

    # --------------------------------------------
    # At least one required table must exist
    # --------------------------------------------
    if not required_tables:
        errors.append("No required tables found")

    # --------------------------------------------
    # Validation result
    # --------------------------------------------
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }

#-----------------------------------------------
def _mask_sql_literals_and_comments(sql: str) -> str:
    """
    Mask quoted strings, quoted identifiers, and SQL comments
    while preserving positions and newline characters.
    """
    result = list(sql)
    state = "normal"
    i = 0

    while i < len(sql):
        char = sql[i]

        if state == "normal":
            if char == "'":
                result[i] = " "
                state = "single_quote"

            elif char == '"':
                result[i] = " "
                state = "double_quote"

            elif sql.startswith("--", i):
                result[i] = result[i + 1] = " "
                state = "line_comment"
                i += 2
                continue

            elif sql.startswith("/*", i):
                result[i] = result[i + 1] = " "
                state = "block_comment"
                i += 2
                continue

        elif state in ("single_quote", "double_quote"):
            delimiter = "'" if state == "single_quote" else '"'

            if char != "\n":
                result[i] = " "

            if char == delimiter:
                # SQL escapes a quote by doubling it.
                if i + 1 < len(sql) and sql[i + 1] == delimiter:
                    result[i + 1] = " "
                    i += 2
                    continue

                state = "normal"

        elif state == "line_comment":
            if char == "\n":
                state = "normal"
            else:
                result[i] = " "

        elif state == "block_comment":
            if char != "\n":
                result[i] = " "

            if sql.startswith("*/", i):
                result[i] = result[i + 1] = " "
                state = "normal"
                i += 2
                continue

        i += 1

    if state in ("single_quote", "double_quote", "block_comment"):
        raise ValueError("Unterminated SQL literal or comment")

    return "".join(result)
#-----------------------------------------------
def validate_sql(sql: str, query_plan: dict):

    if not isinstance(sql, str) or not sql.strip():
        raise ValueError("SQL must be a non-empty string")

    if not isinstance(query_plan, dict):
        raise ValueError("Query plan must be a dictionary")

    # Ignore literals and comments when examining SQL structure.
    sql_code = _mask_sql_literals_and_comments(sql)
    sql_upper = sql_code.upper()

    # RULE: Reject SELECT INTO table/file clauses
    into_pattern = (
        r"\bINTO\s+(?:TEMP|SCRATCH|STANDARD|RAW|EXTERNAL)\b"
    )

    if re.search(into_pattern, sql_upper):
        raise ValueError(
            "SELECT INTO table clauses are not allowed"
        )

    # RULE 1: Aggregation check
    dimensions = query_plan.get("dimensions") or []

    if query_plan.get("has_aggregation") and dimensions:
        if not re.search(r"\bGROUP\s+BY\b", sql_upper):
            raise ValueError("Invalid SQL: missing GROUP BY")

    # RULE 2: SELECT only
    if not sql_upper.lstrip().startswith("SELECT"):
        raise ValueError("Only SELECT queries allowed")

    # RULE 3: No forbidden SQL keywords
    forbidden = ["DELETE", "UPDATE", "INSERT", "DROP"]

    for word in forbidden:
        pattern = rf"\b{re.escape(word)}\b"

        if re.search(pattern, sql_upper):
            raise ValueError(f"Forbidden keyword: {word}")

    # RULE 0: Allow at most one SQL statement.
    # A single trailing semicolon is allowed.
    sql_statement = sql_code.strip()

    semicolon_positions = [
        match.start()
        for match in re.finditer(";", sql_statement)
    ]

    if semicolon_positions and semicolon_positions != [
        len(sql_statement) - 1
    ]:
        raise ValueError("Only one SQL statement is allowed")

    return True