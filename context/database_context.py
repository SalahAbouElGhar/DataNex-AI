
"""
==========================================================
Database Context
==========================================================

Purpose
-------
Prepare all database-related information required by
the Reasoning Engine.

Responsibilities
----------------
- Resolve required tables.
- Detect table relationships.
- Build join plan.
- Collect available columns.
- Build table alias map.

Input
-----
Prompt
Schema

Output
------
Database Context

This module DOES NOT:
    - Perform Business Reasoning.
    - Generate SQL.
    - Interpret Business Language.
    - Read Domain Knowledge.

Database Context is a pure database representation
used by higher reasoning layers.
"""
from schema.schema_utils import (
    get_columns_for_tables,
    build_alias_map
    )

def prepare_database_context(
    schema,
    required_tables,
    relationships
):
    """
    Build the Database Context.
    """

    # ------------------------------
    # Columns
    # ------------------------------

    columns = get_columns_for_tables(
        schema,
        required_tables
    )

    # ------------------------------
    # Alias Map
    # ------------------------------

    alias_map = build_alias_map(
        required_tables
    )

    # ------------------------------
    # Return Database Context
    # ------------------------------

    return {

        "required_tables": required_tables,

        "relationships": relationships,

        "columns": columns,

        "alias_map": alias_map
    }