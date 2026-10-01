from knowledge.business_constants import *
from knowledge.business_keywords import *
from utils.text_utils import contains_any
#-----------------------------------------
"""
==========================================================
Business Reasoning Engine
==========================================================

Purpose
-------
Transform business language into business decisions.

This module represents the reasoning layer of DataNex AI.
Its responsibility is to understand what the user wants
from a business perspective and produce a complete
Business Decision.

It answers business questions.

It does not build SQL.

----------------------------------------------------------
Input
----------------------------------------------------------

Reasoning Context

----------------------------------------------------------
Output
----------------------------------------------------------

Business Decision

A Business Decision is the complete set of business
decisions produced by the Business Reasoning Engine,
independent of any database implementation,
database schema, or SQL syntax.

----------------------------------------------------------
Responsibilities
----------------------------------------------------------

This module is responsible for:

    - Understanding the user's business objective.
    - Identifying the primary business entity.
    - Deciding whether business measures are required.
    - Selecting the appropriate business measure.
    - Choosing the appropriate aggregation strategy.
    - Determining how the result should be presented.
    - Applying business defaults when necessary.

----------------------------------------------------------
This module DOES NOT
----------------------------------------------------------

    - Generate SQL.
    - Read database schema directly.
    - Build Query Plans.
    - Compile SQL.
    - Know database tables or columns.
    - Make database-specific decisions.

----------------------------------------------------------
Design Philosophy
----------------------------------------------------------

Facts come in.

Business decisions go out.

Everything else belongs to another layer.

Think before coding.

Design before implementation.

A strong architecture is built one clear decision at a time.
"""
#-----------------------------------------
"""
 The structure of the output should reflect the structure of the reasoning.

Business Reasoning Pipeline
                    User Prompt
                         │
                         ▼
            What does the user want?
                         │
                         ▼
             Business Objective
                         │
                         ▼
        What business entity is involved?
                         │
                         ▼
              Primary Business Entity
                         │
                         ▼
        Does this require business measures?
                   │                 │
                 YES                 NO
                   │                 │
                   ▼                 ▼
         Which measure?         Build Raw Decision
                   │
                   ▼
       Does the measure require aggregation?
                   │
                   ▼
          Which aggregation fits best?
                   │
                   ▼
        How should the result be displayed?
                   │
                   ▼
      Are grouping / ranking / ordering needed?
                   │
                   ▼
         Apply business default decisions
                   │
                   ▼
             Business Decision
-----------------------------------------
"""
#-----------------------------------------
def resolve_business_objective(reasoning_context):
    """
    Determine the user's business objective.

    This is the first business decision produced by the
    Business Reasoning Engine.

    Input:
        Reasoning Context

    Output:
        One of the supported Business Objectives.
    """
    # --------------------------------------------------
    # Decision Rules
    # --------------------------------------------------

    # Rule 1 : Report Intent      -> REPORT
    # Rule 2 : Raw Intent         -> DETAIL
    # Rule 3 : Simple Listing     -> LIST
    # Rule 4 : Single Indicator   -> KPI
    # Rule 5 : Comparison Request -> COMPARISON
    # Rule 6 : Trend Analysis     -> TREND
    # Rule 7 : Business Summary   -> SUMMARY
    # Rule 8 : Default            -> REPORT

    # --------------------------------------------------
    # Implementation
    # --------------------------------------------------

    #  If the user requests aggregated business information
    #  If the user requests transaction-level or raw data
    #  If the user requests a simple business listing without calculations
    #  If the user requests one business indicator or one aggregated value
    #  If the user requests comparison between entities or periods
    #  If the user requests change over time
    #  If the user requests a high-level overview without specific detail
    #  Default
    # --------------------------------------------------

    prompt = reasoning_context.get(
        "prompt",
        ""
    )

    reasoning_facts = reasoning_context.get(
        "reasoning_facts",
        {}
    )

    intent = reasoning_facts.get(
        "intent"
    )

    if intent == "report":
        return REPORT

    if intent == "raw":
        return DETAIL




    # --------------------------------------------------
    # Rule 2 : Semantic Rules
    # --------------------------------------------------

    clean_prompt = prompt.lower()

    if contains_any(clean_prompt, COMPARISON_KEYWORDS):
        return COMPARISON

    if contains_any(clean_prompt, TREND_KEYWORDS):
        return TREND

    if contains_any(clean_prompt, SUMMARY_KEYWORDS):
        return SUMMARY

    # --------------------------------------------------
    # Rule 3 : Default
    # --------------------------------------------------

    return REPORT

#-----------------------------------------
def build_business_decision(reasoning_context):
    """
    Main entry point for Business Reasoning.
    Build a complete business decision from the reasoning context.

    """

    decision  = {

        # --------------------
        # Identity
        # --------------------

        "business_objective": None,

        "primary_entity": None,

        # --------------------
        # Data
        # --------------------

        "requires_measure": False,

        "measure": None,

        "aggregation": None,

        # --------------------
        # Presentation
        # --------------------

        "display_entities": [],

        "grouping_entities": [],

        "ordering": None,

        "ranking": None,

        # --------------------
        # Constraints
        # --------------------

        "time_filter": None,

        "defaults": {}

    }

    # --------------------------------------------------
    # Identity
    # --------------------------------------------------

    decision["business_objective"] = resolve_business_objective(
        reasoning_context
    )

    decision["primary_entity"] = resolve_primary_entity(
        reasoning_context
    )


    # --------------------------------------------------
    # Data
    # --------------------------------------------------
    decision["requires_measure"] = (
        resolve_requires_measure(
            reasoning_context
        )
    )

    decision["measure"] = resolve_measure(
        reasoning_context
    )

    decision["aggregation"] = resolve_aggregation(
        reasoning_context
    )

    # --------------------------------------------------
    # Presentation
    # --------------------------------------------------

    decision["display_entities"] = resolve_display_entities(
        reasoning_context
    )

    decision["grouping_entities"] = resolve_grouping_entities(
        reasoning_context
    )

    decision["ranking"] = (
        resolve_ranking(
            reasoning_context
        )
    )


    # --------------------------------------------------
    # Constraints
    # --------------------------------------------------

    decision["time_filter"] = (
        resolve_time_filter(
            reasoning_context
        )
    )

    # --------------------------------------------------
    # Business Defaults
    # --------------------------------------------------

    decision = apply_business_defaults(
        decision
    )

    # --------------------------------------------------
    # Return Business Decision
    # --------------------------------------------------

    return decision
#-----------------------------------------
def resolve_primary_entity(reasoning_context):
    """
    Determine the primary business entity.

    Input
    -----
    reasoning_context
        Complete Reasoning Context.

    Returns
    -------
    str
        Primary business entity.

    None
        If the primary entity cannot be resolved
        unambiguously.

    Rules
    -----
    - One business grouping dimension -> primary entity.
    - No grouping dimension -> None.
    - Multiple grouping dimensions -> None.

    Important
    ---------
    Returns a business concept, not a database column.
    """

    reasoning_facts = reasoning_context.get(
        "reasoning_facts",
        {}
    )

    business_group_dimensions = (
        reasoning_facts.get(
            "business_group_dimensions",
            []
        )
    )

    if len(business_group_dimensions) == 1:
        return business_group_dimensions[0]

    return None
# -------------------------------------------
def resolve_requires_measure(reasoning_context):
    """
    Determine whether the business request requires
    a business measure.

    Returns
    -------
    True
        When a business measure was resolved.

    False
        When no business measure was resolved.
    """

    reasoning_facts = reasoning_context.get(
        "reasoning_facts",
        {}
    )

    requested_measure = reasoning_facts.get(
        "requested_measure"
    )

    if requested_measure:
        return True

    return False

# -------------------------------------------
def resolve_measure(reasoning_context):
    """
    Determine the business measure for the request.

    Input
    -----
    reasoning_context
        Complete Reasoning Context.

    Returns
    -------
    str
        Business measure name.

    None
        If no business measure was resolved.
    """

    reasoning_facts = reasoning_context.get(
        "reasoning_facts",
        {}
    )

    requested_measure = reasoning_facts.get(
        "requested_measure"
    )

    if requested_measure:
        return requested_measure

    return None

#-----------------------------------------
def resolve_aggregation(reasoning_context):
    """
    Determine the aggregation strategy
    for the requested business measure.

    Returns
    -------
    str
        Business aggregation.

    None
        If no aggregation was resolved.
    """

    reasoning_facts = reasoning_context.get(
        "reasoning_facts",
        {}
    )

    aggregation_function = reasoning_facts.get(
        "aggregation_function"
    )

    if aggregation_function:
        return aggregation_function

    return None

# -----------------------------------------
def resolve_display_entities(reasoning_context):
    """
    Determine the business entities that should be displayed
    in the final business result.

    Returns business concepts, not database columns.
    """

    reasoning_facts = reasoning_context.get(
        "reasoning_facts",
        {}
    )

    business_group_dimensions = (
        reasoning_facts.get(
            "business_group_dimensions",
            []
        )
    )

    if business_group_dimensions:
        return list(
            business_group_dimensions
        )

    return []
# -----------------------------------------
def resolve_grouping_entities(reasoning_context):
    """
    Determine the business entities that should be used
    for business grouping.

    Returns business concepts, not database columns.
    """

    reasoning_facts = reasoning_context.get(
        "reasoning_facts",
        {}
    )

    business_group_dimensions = (
        reasoning_facts.get(
            "business_group_dimensions",
            []
        )
    )

    if business_group_dimensions:
        return list(
            business_group_dimensions
        )

    return []
# -----------------------------------------
def resolve_time_filter(reasoning_context):
    """
    Determine the business time constraint.

    Returns
    -------
    dict
        Business time decision.

    None
        If no time constraint was resolved.
    """

    reasoning_facts = reasoning_context.get(
        "reasoning_facts",
        {}
    )

    time_filter = reasoning_facts.get(
        "time_filter"
    )

    if time_filter:
        return time_filter

    return None
# -----------------------------------------
def resolve_ranking(reasoning_context):
    """
    Determine the business ranking strategy.

    Returns the resolved ranking strategy
    or None if no ranking was requested.
    """

    reasoning_facts = reasoning_context.get(
        "reasoning_facts",
        {}
    )

    ranking_strategy = reasoning_facts.get(
        "ranking_strategy"
    )

    if ranking_strategy:
        return ranking_strategy

    return None
# -----------------------------------------

def apply_business_defaults(decision):
    """
    Apply business-level default decisions.

    This function does not know database columns
    or SQL syntax.
    """

    # --------------------------------------------------
    # Rule 1 : Report ordering default
    # --------------------------------------------------

    if not decision.get("ranking"):

        if (
            decision.get("business_objective") == REPORT
            and decision.get("requires_measure")
            and decision.get("measure")
            and decision.get("grouping_entities")
            and not decision.get("ordering")
        ):
            decision["ordering"] = {
                "type": "measure_desc"
            }

    # --------------------------------------------------
    # Rule 2 : Detail ordering default
    # --------------------------------------------------

#    if (
#        decision.get("business_objective") == DETAIL
#        and not decision.get("ordering")
#    ):
#        decision["ordering"] = {
#            "type": "latest"
#        }

    if (
        decision.get("business_objective") == DETAIL
        and not decision.get("ranking")
        and not decision.get("ordering")
    ):
        decision["ordering"] = {
            "type": "latest"
        }

    return decision
