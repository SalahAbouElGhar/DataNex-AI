import re

# -------------------------------------------------------
def clean_sql(sql):
    if not isinstance(sql, str):
        raise TypeError("SQL must be a string")

    # Formatting only: do not rewrite SQL semantics.
    return sql.strip()

# -------------------------------------------------------
def fix_informix_sql(sql):
    if not isinstance(sql, str):
        raise TypeError("SQL must be a string")

    # Convert a trailing FETCH FIRST N ROWS ONLY clause.
    # Only match the actual clause at the end of the query,
    # not text such as 'FIRST 10' inside a string literal.
    pattern = re.compile(
        r"\s+FETCH\s+FIRST\s+(\d+)\s+ROWS?\s+ONLY\s*(;?)\s*$",
        re.IGNORECASE,
    )

    match = pattern.search(sql)

    if not match:
        return sql

    n = match.group(1)
    terminator = match.group(2)

    # Remove the FETCH clause and preserve a trailing semicolon.
    sql = sql[:match.start()].rstrip() + terminator

    # Insert FIRST N immediately after SELECT, regardless of case.
    select_pattern = re.compile(
        r"^(\s*SELECT\b)",
        re.IGNORECASE,
    )

    if not select_pattern.match(sql):
        raise ValueError(
            "Cannot convert FETCH clause: expected a SELECT statement"
        )

    # Avoid producing two row-limit clauses.
    if re.match(r"^\s*SELECT\s+FIRST\b", sql, re.IGNORECASE):
        raise ValueError(
            "SQL contains both SELECT FIRST and FETCH FIRST limits"
        )

    return select_pattern.sub(
        lambda m: f"{m.group(1)} FIRST {n}",
        sql,
        count=1,
    )

# -------------------------------------------------------