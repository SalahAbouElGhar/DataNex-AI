from context.database_context import (
    prepare_database_context
)

from context.knowledge_context import (
    prepare_knowledge_context
)

from reasoning.measure_reasoning import (
    resolve_requested_measure
)
from reasoning.business_facts import (
    resolve_business_grouping_dimensions
)
from core.config import (
    BUSINESS_TERMS)

"""
==========================================================
Reasoning Context
==========================================================

Purpose
-------
Build the complete Reasoning Context consumed by the
Business Reasoning Engine.

Responsibilities
----------------
- Build Database Context.
- Build Knowledge Context.
- Collect Reasoning Facts.
- Assemble a unified Reasoning Context.

Input
-----
Prompt
Schema
Domain Configuration

Output
------
Reasoning Context

This module DOES NOT:
    - Make Business Decisions.
    - Generate SQL.
    - Build Query Plans.
    - Compile SQL.

Reasoning Context is the complete business understanding
prepared before Business Reasoning begins.
"""
# ------------------------------

def prepare_reasoning_context(
    prompt,
    schema,
    domain_config,
    required_tables,
    relationships,
    aggregation_function,
    group_dimensions,
    time_filter,
    ranking_strategy,
    intent
):
    """
    Build the complete Reasoning Context.
    """

    # ------------------------------
    # Database Context
    # ------------------------------

    database_context = prepare_database_context(
        schema,
        required_tables,
        relationships
    )

    # ------------------------------
    # Knowledge Context
    # ------------------------------

    knowledge_context = prepare_knowledge_context(
        domain_config
    )

    business_group_dimensions = (
        resolve_business_grouping_dimensions(
            prompt,
            BUSINESS_TERMS
        )
    )

    # ------------------------------
    # Reasoning Facts
    # ------------------------------

    requested_measure = resolve_requested_measure(
        prompt,
        knowledge_context
    )

    # ------------------------------
    # Reasoning Facts
    # ------------------------------
    reasoning_facts = {

        "requested_measure":
            requested_measure,

        "business_group_dimensions":
            business_group_dimensions,

        "aggregation_function":
            aggregation_function,

        "group_dimensions":
            group_dimensions,

        "time_filter":
            time_filter,

        "ranking_strategy":
            ranking_strategy,

        "intent":
            intent
    }

    # ------------------------------
    # Return Reasoning Context
    # ------------------------------

    return {

        "prompt": prompt,

        "database_context":
            database_context,

        "knowledge_context":
            knowledge_context,

        "reasoning_facts":
            reasoning_facts
    }
