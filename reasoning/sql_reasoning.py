import re
from core.config import (
    BUSINESS_TERMS,
    AGGREGATION_KEYWORDS,
    MEASURE_KEYWORDS,
    DATE_COLUMN_KEYWORDS,
    LIMIT_PATTERNS,
    RELATIONSHIP_SUFFIXES,
    RELATIONSHIP_HINTS,
    DISPLAY_KEYWORDS,
    DOMAINS
)
from schema.schema_utils import (
    get_columns_for_tables,
    is_relationship_column,
    strip_relationship_suffix,
    extract_relationship_columns,

    build_alias_map,
    build_semantic_targets,
    build_display_targets,
    extract_measure_columns,
    extract_date_columns

)
from reasoning.business_reasoning import(build_business_decision)
from context.reasoning_context import (
    prepare_reasoning_context
)

from pprint import pprint

# ==========================================================
# Debug Flags
# ==========================================================
DEBUG_REASONING_CONTEXT = False

DEBUG_BUSINESS_REASONING = True #False

DEBUG_QUERY_PLANNER = False

DEBUG_AST = False

DEBUG_SQL_COMPILER = False

# ===============================
# TEXT HELPERS
# ===============================
def extract_words(text):

    return re.findall(r"\w+", text.lower())

#---------------------------------------------------

def extract_grouping_terms(prompt):

    match = re.search(
            r"\bby\b(.+)",
            prompt
        )

    if match:
        return match.group(1).strip()

    return  ""

#--------------------------------------------------------

# ===============================
# SCHEMA PARSER
# ===============================

def parse_multi_table_schema(schema_text: str):

    schema_text = schema_text.lower()

    result = {"tables": {}}


# SPLIT TABLE BLOCKS


    blocks = re.split(r'\btable\b', schema_text)

    for block in blocks:

        block = block.strip()

        if not block:
            continue
        # -------------------------
        # MATCH TABLE STRUCTURE
        # -------------------------

        match = re.match(r'(\w+)\s+columns\s*(.*)',block,re.DOTALL)

        if not match:
            continue

        table_name = match.group(1)

        columns_text = match.group(2)

        columns = []

        for col in re.split(r'[\n,]+',columns_text):

            col = col.strip()

            if col:
                columns.append(col)

        result["tables"][table_name] = columns

    return result
#----------------------------------------------------------------                                                                                                                   #

# ===============================
# DOMAIN
# ===============================

def detect_domain_from_keywords(prompt):

    prompt = prompt.lower()

    for domain_name, domain_config in DOMAINS.items():

        if any(
            keyword in prompt
            for keyword in domain_config["keywords"]
        ):
            return domain_name

    return None
#---------------------------------------------------------
def detect_domain_from_entities(prompt):

    words = extract_words(prompt)

    best_domain = None
    best_score = 0

    for domain_name, domain_config in DOMAINS.items():

        score = 0

        entities = domain_config.get("entities", {})

        for entity in entities:

            aliases = BUSINESS_TERMS.get(entity, [])

            if any(alias in words for alias in aliases):

                score += 1

        if score > best_score:

            best_score = score
            best_domain = domain_name

    if best_score == 0:
        return None

    return best_domain

#---------------------------------------------------------
def detect_domain(prompt):

    for detector in (

        detect_domain_from_keywords,

        detect_domain_from_entities,

    ):

        domain = detector(prompt)

        if domain:
            return domain

    return "generic"


# ===============================
# TABLE DETECTION
# ===============================

def detect_tables_from_columns(prompt,schema):

    prompt_lower = prompt.lower()

    tables = schema["tables"]

    required_tables = set()

    for table_name, columns in tables.items():

        for column in columns:

            if column.lower() in prompt_lower:

                required_tables.add(table_name)

    return required_tables
#---------------------------------------------------
def resolve_tables_from_entities(
    prompt,
    schema
):

    words = extract_words(prompt)

    tables = schema["tables"]

    domain = detect_domain(prompt)

    domain_entities = (
        DOMAINS
        .get(domain, {})
        .get("entities", {})
    )

    required_tables = set()

    for entity, candidate_tables in domain_entities.items():

        aliases = BUSINESS_TERMS.get(entity, [])

        for alias in aliases:

            if alias in words:

                for table_name in candidate_tables:

                    if table_name in tables:

                        required_tables.add(table_name)

                break

    return required_tables
#--------------------------------------------------
def resolve_required_tables(prompt,schema):

    for detector in (
        detect_tables_from_columns,
        resolve_tables_from_entities,
        ):

            result = detector(prompt, schema)

            if result:
                return sorted(result)
# 3. Fallback

    return get_default_table(schema)
#-----------------------------------------------

def get_default_table(schema):

#    return [list(schema["tables"])[0]]

    return [next(iter(schema["tables"]))]




# ===============================
# COLUMN ANALYSIS
# ===============================

def extract_candidate_dimensions(
    columns: list,
    measures: list,
    date_columns: list
):

    exclude = set(
        measures + date_columns
    )

    dimensions = [

        col for col in columns

        if col not in exclude

    ]


    # REMOVE DUPLICATES

    dimensions = list(dict.fromkeys(dimensions))

    return dimensions
#-------------------------------------------------------
# ===============================
# RELATIONSHIP DETECTION
# ===============================

def is_relationship_candidate(col):

    col = col.lower()

    return (
        col == "id"
        or
        is_relationship_column(col)
    )

#--------------------------------------------------
def calculate_relationship_score(
    left_column,
    right_column
):

    score = 0

    l = left_column.lower().strip()
    r = right_column.lower().strip()

    # RULE 1
    if l == r:
        score += 50

    left_is_rel = is_relationship_column(l)
    right_is_rel = is_relationship_column(r)

    # RULE 2
    if left_is_rel and right_is_rel:

        score += 30

    # RULE 3
    if (left_is_rel and right_is_rel
        and strip_relationship_suffix(l) == strip_relationship_suffix(r)):

        score += 40

    return score
#--------------------------------------------------
def detect_relationships(schema):

    tables = schema["tables"]

    relationships = []

    table_names = list(tables.keys())

    # -------------------------
    # NORMALIZE HELPERS
    # -------------------------

    def normalize(col):
        return col.lower().strip()

    # -------------------------
    # COMPARE TABLES
    # -------------------------

    for i in range(len(table_names)):
        for j in range(i + 1, len(table_names)):

            left_table = table_names[i]
            right_table = table_names[j]

            left_columns = tables[left_table]
            right_columns = tables[right_table]

            # -------------------------
            # COLUMN MATCHING
            # -------------------------

            for lcol in left_columns:

                if not is_relationship_candidate(lcol):
                    continue

                for rcol in right_columns:

                    if not is_relationship_candidate(rcol):
                        continue

                    score = calculate_relationship_score( lcol, rcol)

                    # -------------------------
                    # ACCEPT RELATIONSHIP
                    # -------------------------

                    if score >= 50:

                        already_exists = any(

                            (
                                r["left_table"] == right_table
                                and
                                r["right_table"] == left_table
                                and
                                r["left_column"] == rcol
                                and
                                r["right_column"] == lcol
                            )

                            for r in relationships
                        )

                        if already_exists:
                            continue

                        relationships.append({
                            "left_table": left_table,
                            "right_table": right_table,
                            "left_column": lcol,
                            "right_column": rcol,
                            "score": score
                        })

    return relationships
#--------------------------------------------------
# ===============================
# SEMANTIC HELPERS
# ===============================

def normalize_column_name(column):

    column = column.lower()

    column = column.replace("_", "")

    return column
#----------------------------------------------------------
def semantic_match(term_aliases, column):

    column = normalize_column_name(column)

    for alias in term_aliases:

        alias = normalize_column_name(alias)

        if alias in column:

            return True

    return False

# ===============================
# QUERY CONTEXT
# ===============================
# Legacy implementation still in active use.
def prepare_query_context(prompt,schema,domain_config):


#    try:
    # -------------------------
    # DATABASE PREPARATION
    # -------------------------

    required_tables = resolve_required_tables(prompt, schema)

    relationships = detect_relationships(schema)

    join_plan = None

    if len(required_tables) > 1:
        join_plan = build_join_plan(
            required_tables,
            relationships
        )

    columns = get_columns_for_tables(
        schema,
        required_tables
    )

    alias_map = build_alias_map(
        required_tables
    )

    # -------------------------
    # KNOWLEDGE PREPARATION
    # -------------------------

    semantic_targets = build_semantic_targets(
        domain_config
    )

    display_targets = build_display_targets(
        domain_config
    )

    return {

        # Database

        "required_tables": required_tables,
        "relationships": relationships,
        "join_plan": join_plan,
        "columns": columns,
        "alias_map": alias_map,

        # Knowledge

        "semantic_targets": semantic_targets,
        "display_targets": display_targets
    }

#---------------------------------------------------------------------------
# ===============================
# REASONING
# ===============================

def resolve_aggregation_function(prompt):

    prompt = prompt.lower()

    for function, keywords in AGGREGATION_KEYWORDS.items():

        if any(keyword in prompt for keyword in keywords):

            return function

    return None

# -------------------------------------------------------------
# -------------------------------------------------------------

def resolve_grouping_dimensions(
        prompt,
        semantic_targets,
        display_targets,
        BUSINESS_TERMS
):

    prompt = prompt.lower()

    words = prompt.split()

    use_display = any(
        word in words
        for word in DISPLAY_KEYWORDS
    )

    dimensions = []

    for business_term, aliases in BUSINESS_TERMS.items():

        for alias in aliases:

            if alias in words:

                if use_display:

                    if business_term in display_targets:

                        dimensions.append(
                            display_targets[ business_term  ]
                        )
                    elif business_term in semantic_targets:

                        dimensions.append(
                            semantic_targets[business_term]
                        )

                else:

                    if business_term in semantic_targets:

                        dimensions.append(
                            semantic_targets[business_term]
                        )




                break

    return dimensions

#--------------------------------------------------------------
def resolve_ranking_strategy(prompt):

    prompt = prompt.lower()

    # -------------------------
    # HIGHEST
    # -------------------------

    if "highest" in prompt:

        return {
            "type": "top_n",
            "limit": 1
        }

    # -------------------------
    # TOP N
    # -------------------------

    if "top" in prompt:

        words = prompt.split()

        for i, word in enumerate(words):

            if word == "top":

                if (
                    i + 1 < len(words)
                    and words[i + 1].isdigit()
                ):

                    return {
                        "type": "top_n",
                        "limit": int(
                            words[i + 1]
                        )
                    }

                return {
                    "type": "top_n",
                    "limit": 10
                }

    # -------------------------
    # BOTTOM N
    # -------------------------

    if "bottom" in prompt:

        words = prompt.split()

        for i, word in enumerate(words):

            if word == "bottom":

                if (
                    i + 1 < len(words)
                    and words[i + 1].isdigit()
                ):

                    return {
                        "type": "bottom_n",
                        "limit": int(
                            words[i + 1]
                        )
                    }

                return {
                    "type": "bottom_n",
                    "limit": 10
                }

    # -------------------------
    # LATEST N
    # -------------------------

    if "latest" in prompt:

        words = prompt.split()

        for i, word in enumerate(words):

            if word == "latest":

                if (
                    i + 1 < len(words)
                    and words[i + 1].isdigit()
                ):

                    return {
                        "type": "latest_n",
                        "limit": int(
                            words[i + 1]
                        )
                    }

                return {
                    "type": "latest_n",
                    "limit": 10
                }

    # -------------------------
    # FIRST N
    # -------------------------

    if "first" in prompt:

        words = prompt.split()

        for i, word in enumerate(words):

            if word == "first":

                if (
                    i + 1 < len(words)
                    and words[i + 1].isdigit()
                ):

                    return {
                        "type": "first_n",
                        "limit": int(
                            words[i + 1]
                        )
                    }

                return {
                    "type": "first_n",
                    "limit": 10
                }

    return None

#def detect_intent(
#    prompt,
#    aggregation_function,
#    group_dimensions,
#    ranking_strategy
#):
#
#    prompt_lower = prompt.lower()
#
#    # -------------------
#    # REPORT
#    # -------------------
#
#    if (
#        group_dimensions
#        or "report" in prompt_lower
#        or "by" in prompt_lower
#    ):
#        intent = "report"
#
#    # -------------------
#    # KPI
#    # -------------------
#
#    elif aggregation_function:
#        intent = "kpi"
#
#    # -------------------
#    # RAW
#    # -------------------
#
#    else:
#        intent = "raw"
#
#    # -------------------
#    # RANKING
#    # -------------------
#
#    if ranking_strategy and intent == "raw":
#        intent = "report"
#
#    return intent
#
def detect_intent(
    prompt,
    aggregation_function,
    group_dimensions,
    ranking_strategy
):

    prompt_lower = prompt.lower()

    # -------------------
    # REPORT
    # -------------------

    if (
        group_dimensions
        or "report" in prompt_lower
        or "by" in prompt_lower
    ):
        intent = "report"

    # -------------------
    # KPI
    # -------------------

    elif aggregation_function:
        intent = "kpi"

    # -------------------
    # RAW
    # -------------------

    else:
        intent = "raw"

    # -------------------
    # RANKING / SELECTION
    # -------------------

    if ranking_strategy and intent == "raw":

        ranking_type = ranking_strategy.get(
            "type"
        )

        if ranking_type in (
            "top_n",
            "bottom_n"
        ):
            intent = "report"

    return intent

# ----- Dimensions -----

def resolve_requested_dimensions(prompt: str,columns: list,date_columns):

    required_dimensions = []

    # -------------------------
    # BUSINESS TERMS
    # -------------------------

    group_part = (
        extract_grouping_terms(prompt.lower())
        or ""
    )

    if not group_part:
        return []


    for keyword, aliases in BUSINESS_TERMS.items():

        if keyword in group_part:


            for col in columns:

                if col in date_columns:
                    continue
                if semantic_match(
                    aliases,
                    col
                ):

                    if col not in required_dimensions:
                        required_dimensions.append(col)

    return required_dimensions

#-----------------------------------------------------------------


# ----- Count -----

def resolve_count_target(prompt, semantic_targets):

    prompt = prompt.lower()


    # count rows
    if "rows" in prompt:
        return {
            "type": "rows"
        }

    for business_term, aliases in BUSINESS_TERMS.items():

        for alias in aliases:

            if alias in prompt:


                return {
                    "type": "distinct",
                    "column": semantic_targets.get(business_term)
                }

    return None

# ----- Time -----

def resolve_time_filter(prompt: str):

    prompt = prompt.lower()

    # -------------------------
    # TODAY
    # -------------------------

    if "today" in prompt:

        return {
            "type": "relative_period",
            "period": "day",
            "offset": 0
        }

    # -------------------------
    # THIS MONTH
    # -------------------------

    if "this month" in prompt:

        return {
            "type": "relative_period",
            "period": "month",
            "offset": 0
        }

    # -------------------------
    # THIS YEAR
    # -------------------------

    if "this year" in prompt:

        return {
            "type": "relative_period",
            "period": "year",
            "offset": 0
        }

    # -------------------------
    # YESTERDAY
    # -------------------------

    if "yesterday" in prompt:

        return {
            "type": "relative_period",
            "period": "day",
            "offset": -1
        }

    # -------------------------
    # LAST MONTH
    # -------------------------

    if "last month" in prompt:

        return {
            "type": "relative_period",
            "period": "month",
            "offset": -1
        }

    # -------------------------
    # LAST YEAR
    # -------------------------

    if "last year" in prompt:

        return {
            "type": "relative_period",
            "period": "year",
            "offset": -1
        }
    return None

# ----- Limit -----

def resolve_limit_strategy(prompt: str):

    prompt_lower = prompt.lower()

    for limit_type, pattern in LIMIT_PATTERNS.items():

        match = re.search(
            pattern,
            prompt_lower
        )

        if match:

            return {
                "type": limit_type,
                "limit": int(match.group(1))
            }

    return None


#-------------------------------------------------------------------

def resolve_ranking_dimensions(
    prompt,
    columns,
    date_columns
):

    ranking_dimensions = []

    prompt = prompt.lower()

    words = prompt.split()

    for keyword, aliases in BUSINESS_TERMS.items():

        matched = any(
            alias in words
            for alias in aliases
        )

        if not matched:
            continue

        for col in columns:

            if col in date_columns:
                continue

            if semantic_match(
                aliases,
                col
            ):

                if col not in ranking_dimensions:

                    ranking_dimensions.append(col)

    return ranking_dimensions

#----------------------------------------------------------------------

def resolve_having_condition(
    prompt,
    measures,
    aggregation_function
):

    prompt = prompt.lower()

    match = re.search(
        r"(>=|<=|>|<|=)\s*(\d+)",
        prompt
    )

    if not match:
        return None

    # MAX / MIN comparisons will be handled later
    # by the Smart Measure Filter engine.
    if aggregation_function in ("MAX", "MIN"):
        return None

    function = aggregation_function

    # Implicit aggregation
    if not function and measures:
        function = "SUM"

    if not function:
        return None

    operator = match.group(1)

    value = int(match.group(2))

    return {
        "function": function,
        "column": measures[0],
        "operator": operator,
        "value": value
    }
#-------------------------------------------

def resolve_final_dimensions(
    prompt,
    columns,
    measures,
    date_columns,
    ranking_strategy,
    has_aggregation,
    group_dimensions,
    intent
):

#    if ranking_strategy:
#
#        ranking_dimensions = resolve_ranking_dimensions(
#            prompt,
#            columns,
#            date_columns
#        )
#
#        if ranking_dimensions:
#            return ranking_dimensions
#
#        return []

    if ranking_strategy:

        ranking_type = ranking_strategy.get(
            "type"
        )

        if ranking_type in (
            "top_n",
            "bottom_n"
        ):

            ranking_dimensions = resolve_ranking_dimensions(
                prompt,
                columns,
                date_columns
            )

            if ranking_dimensions:
                return ranking_dimensions

            return []

    if has_aggregation:

        if group_dimensions:
            return group_dimensions

        requested_dimensions = resolve_requested_dimensions(
            prompt,
            columns,
            date_columns
        )

        if requested_dimensions:
            return requested_dimensions

        if intent == "report":

            return extract_candidate_dimensions(
                columns,
                measures,
                date_columns
            )

        return []

    return extract_candidate_dimensions(
        columns,
        measures,
        date_columns
    )

# ===============================
# QUERY PLANNING
# ===============================
def build_join_plan(
    required_tables,
    relationships
):

    # -------------------------
    # SINGLE TABLE
    # -------------------------

    if len(required_tables) <= 1:

        return {
            "base_table": required_tables[0],
            "joins": []
        }

    # -------------------------
    # BASE TABLE
    # -------------------------

    base_table = None

    for relationship in relationships:

        if relationship["left_table"] in required_tables:

            base_table = relationship["left_table"]
            break

    joins = []

    for relationship in relationships:

        left_table = relationship["left_table"]
        right_table = relationship["right_table"]

        if (
            left_table not in required_tables
            or
            right_table not in required_tables
        ):
            continue

        joins.append({

            "join_type": "INNER",

            "left_table": left_table,
            "right_table": right_table,

            "left_column":
                relationship["left_column"],

            "right_column":
                relationship["right_column"]

        })

    # -------------------------
    # FINAL PLAN
    # -------------------------

    return {

        "base_table": base_table,

        "joins": joins

    }

#---------------------------------------------------------
# =====================================================
# MAIN QUERY PLANNER
# =====================================================
def build_query_plan(prompt: str, schema: dict):

    """
    Build the complete query plan.

    Steps:
    - Detect required tables
    - Discover relationships
    - Resolve semantics
    - Detect intent
    - Build final query plan

    Returns:
        dict: Query plan
    """
    # PIPELINE:
    # tables
    # joins
    # semantics
    # intent
    # filters
    # dimensions
    # ordering
    # return plan

    prompt_lower = prompt.lower()

    # -------------------------
    # DOMAIN
    # -------------------------

    domain_name = detect_domain(prompt)

    domain_config = DOMAINS[domain_name]

    # -------------------------
    # CONTEXT
    # -------------------------

    context = prepare_query_context(prompt,schema,domain_config)

    required_tables = context["required_tables"]

    relationships = context["relationships"]

    join_plan = context["join_plan"]

    columns = context["columns"]

    alias_map = context["alias_map"]

    semantic_targets = context["semantic_targets"]

    display_targets = (context["display_targets"])

    # -------------------------
    # PROMPT PREPARATION
    # -------------------------

    clean_prompt = prompt.lower()

    clean_prompt = clean_prompt.split("\n")[0]

    if ":" in clean_prompt:
        clean_prompt = clean_prompt.split(":")[-1].strip()


    # -------------------------
    # AGGREGATION
    # -------------------------

    aggregation_function = resolve_aggregation_function(prompt)

    # -------------------------
    # PROMPT GROUPING
    # -------------------------

    count_part = clean_prompt

    group_part = ""

    if " by " in clean_prompt:

        parts = clean_prompt.split(" by ", 1)

        count_part = parts[0]

        group_part = parts[1]

    # -------------------------
    # COUNT TARGET
    # -------------------------

    count_target = None

    if aggregation_function and aggregation_function.lower() == "count":
        count_target = resolve_count_target(
            count_part,
            semantic_targets
        )

    # -------------------------
    # GROUP DIMENSIONS
    # -------------------------

    group_source = group_part if group_part else clean_prompt


    group_dimensions = resolve_grouping_dimensions(
        group_source,
        semantic_targets,
        display_targets,
        BUSINESS_TERMS
    )

    # -------------------------
    # RANKING
    # -------------------------

    ranking_strategy = resolve_ranking_strategy(prompt)

    # -------------------
    # INTENT
    # -------------------

    intent = detect_intent(
            prompt,
            aggregation_function,
            group_dimensions,
            ranking_strategy
        )

    # -------------------------
    # DEFAULT AGGREGATION
    # -------------------------

    if intent == "report" and not aggregation_function:
        aggregation_function = "SUM"

#    if ranking_strategy and not aggregation_function:
#        aggregation_function = "SUM"

    # -------------------
    # TIME FILTER
    # -------------------

    time_filter = resolve_time_filter(prompt)


    # -------------------------
    # SAFE RAW POLICY
    # -------------------------

#    if intent == "raw" and not time_filter:
#
#        time_filter = {
#            "type": "relative_period",
#            "period": "day",
#            "offset": 0
#        }

    if (
        intent == "raw"
        and not time_filter
        and not (
            ranking_strategy
            and ranking_strategy.get("type") in (
                "latest_n",
                "first_n"
            )
        )
    ):
        time_filter = {
            "type": "relative_period",
            "period": "day",
            "offset": 0
        }

    # -------------------------
    # DATE COLUMNS
    # -------------------------

    date_columns = extract_date_columns(columns)

    # -------------------
    # MEASURES
    # -------------------

    measures = extract_measure_columns(columns)

    # -------------------------
    # AGGREGATION CONTEXT
    # -------------------------

    has_aggregation = (
        intent in ["report", "kpi"]
        and len(measures) > 0
    )

    # -------------------
    # DIMENSIONS
    # -------------------

#    try:

    dimensions = resolve_final_dimensions(
                prompt,
                columns,
                measures,
                date_columns,
                ranking_strategy,
                has_aggregation,
                group_dimensions,
                intent
            )

    # -------------------------
    # BUSINESS REASONING
    # -------------------------

    reasoning_context = prepare_reasoning_context(
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
    )

    decision = build_business_decision(
        reasoning_context
    )

    business_ordering = decision.get("ordering")
    business_ranking = decision.get("ranking")

    order_strategy = None

    # -------------------------
    # BUSINESS ORDERING
    # -------------------------

    if business_ordering:

        if business_ordering.get("type") == "measure_desc":

            if measures:
                order_strategy = {
                    "type": "measure_desc",
                    "measure": measures[0]
                }

        elif business_ordering.get("type") == "latest":

            if date_columns:
                order_strategy = {
                    "type": "latest_date",
                    "column": date_columns[0]
                }


    # -------------------------
    # RANKING ORDER
    # -------------------------

    if business_ranking and measures:

        ranking_type = business_ranking.get("type")

        if ranking_type == "top_n":

            order_strategy = {
                "type": "measure_desc",
                "measure": measures[0]
            }

        elif ranking_type == "bottom_n":

            order_strategy = {
                "type": "measure_asc",
                "measure": measures[0]
            }

        elif ranking_type == "latest_n":

            if date_columns:

                order_strategy = {
                    "type": "latest_date",
                    "column": date_columns[0]
                }

        elif ranking_type == "first_n":

            if date_columns:

                order_strategy = {
                    "type": "earliest_date",
                    "column": date_columns[0]
                }


    # -------------------------
    # LIMIT
    # -------------------------
    if business_ranking:
        limit_strategy = business_ranking
    else:
        limit_strategy = resolve_limit_strategy(prompt)

    # -------------------------
    # RAW OUTPUT POLICY
    # -------------------------
    if intent == "raw":

        for date_col in date_columns:

            if date_col not in dimensions:
                dimensions.append(date_col)
    # -------------------
    # HAVING
    # -------------------

    having_condition = resolve_having_condition(
            prompt,
            measures,
            aggregation_function
        )

    # --------------------------------------------------
    # Temporary Business Reasoning Test
    # --------------------------------------------------

    if DEBUG_BUSINESS_REASONING:

        print("Reasoning facts")
        print("=" * 60)

        pprint(
            reasoning_context["reasoning_facts"]
        )

        print("\n" + "=" * 60)
        print("Business Decision")
        print("=" * 60)

        pprint(
            decision
        )
    # --------------------------------------------------
    # End Temporary Business Reasoning Test
    # --------------------------------------------------

    # -------------------
    # RETURN PLAN
    # -------------------

    return {

    # Intent

    "intent": intent,

    # Query Structure

    "aggregation_function": aggregation_function,

    "count_target": count_target,

    "group_dimensions": group_dimensions,

    "measures": measures,

    "dimensions": dimensions,

    # Time

    "date_columns": date_columns,

    "time_filter": time_filter,

    # Execution

    "order_strategy": order_strategy,

    "limit_strategy": limit_strategy,

    "having_condition": having_condition,

    # Database

    "required_tables": required_tables,

    "relationships": relationships,

    "join_plan": join_plan,

    "alias_map": alias_map,

    "schema": schema,

    # Flags

    "has_aggregation": has_aggregation
}
#
#| الدالة الحالية              | مستقبلها       |
#| --------------------------- | -------------- |
#| detect_domain               | تبقى           |
#| detect_intent               | تبقى           |
#| prepare_query_context       | تبقى           |
#| resolve_limit_strategy      | تندمج          |
#| resolve_count_target        | تندمج          |
#| resolve_final_dimensions    | نراجعها لاحقًا |
#| resolve_grouping_dimensions | نراجعها لاحقًا |
