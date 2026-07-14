import re
from core.config import (
    BUSINESS_KEYWORDS,
    BUSINESS_TERMS,
    BUSINESS_TABLES,
    MEASURE_KEYWORDS,
    DATE_COLUMN_KEYWORDS,
    LIMIT_PATTERNS,
    RELATIONSHIP_SUFFIXES,
    RELATIONSHIP_HINTS,
    DISPLAY_KEYWORDS
)
from schema.schema_utils import (
    extract_all_columns,
    extract_id_columns,
    get_columns_for_tables,
    is_relationship_column,
    strip_relationship_suffix,
    extract_relationship_columns,
    
    build_display_targets
)
import traceback

# --------------------------------------------------   
def parse_multi_table_schema(schema_text: str):

    schema_text = schema_text.lower()

    result = {"tables": {}}

    # -------------------------
    # SPLIT TABLE BLOCKS
    # -------------------------

    blocks = re.split(r'\btable\b', schema_text)

    for block in blocks:

        block = block.strip()

        if not block:
            continue
        # -------------------------
        # MATCH TABLE STRUCTURE
        # -------------------------

#        match = re.match(r'(\w+)\s+columns\s+(.+)',block)

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

#        columns = [
#
#            col.strip()
#
#            for col in columns_text.split(",")
#
#            if col.strip()
#
#        ]

        result["tables"][table_name] = columns

    return result
#--------------------------------------------------
def is_candidate_key(col):

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
            
                if not is_candidate_key(lcol):
                    continue
            
                for rcol in right_columns:
            
                    if not is_candidate_key(rcol):
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
def detect_required_tables(prompt, schema):

    prompt_lower = prompt.lower()

    tables = schema["tables"]

    required_tables = set()
    # -------------------------
    # COLUMN MATCHING
    # -------------------------

    for table_name, columns in tables.items():

        for column in columns:

            if column.lower() in prompt_lower:

                if table_name not in required_tables:
                    required_tables.add(table_name)

    # -------------------------
    # BUSINESS KEYWORDS
    # -------------------------
    for keyword, related_tables in BUSINESS_KEYWORDS.items():

        if keyword in prompt_lower:
    
            for t in related_tables:
    
                if t in tables:
    
                    required_tables.add(t)
                    
    # -------------------------
    # BUSINESS TERMS
    # -------------------------
    
    for business_term, aliases in BUSINESS_TERMS.items():
    
        for alias in aliases:
 #--  
            if alias in prompt_lower:
    
                candidate_tables = (
                    BUSINESS_TABLES.get(
                        business_term,
                        []
                    )
                )
    
                for table_name in candidate_tables:
    
                    if table_name in tables:
                        required_tables.add(
                            table_name
                        )
    
                break
                
    # -------------------------
    # SAFE FALLBACK
    # -------------------------

    if not required_tables:

        # default to first table
        first_table = list(
            tables.keys()
        )[0]

        required_tables.add(
            first_table
        )

    return sorted(required_tables)
    
#---------------------------------------------------
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
#------------------------------------------------------

#def parse_schema(schema_text: str):
#
#    if not isinstance(schema_text, str):
#        raise Exception("Schema must be string")
#    
#    schema_text = schema_text.lower()
#
#    result = {
#        "table": None,
#        "columns": []
#    }
#
#    # -------------------
#    # EXTRACT TABLE NAME
#    # -------------------
#    table_match = re.search(
#        r'table name\s+([a-zA-Z0-9_]+)',
#        schema_text
#    )
#
#    if table_match:
#        result["table"] = table_match.group(1)
#
#    # -------------------
#    # EXTRACT COLUMNS
#    # -------------------
#    columns_match = re.search(
#        r'column names\s+(.+)',
#        schema_text
#    )
#
#    if columns_match:
#
#        columns_text = columns_match.group(1)
#
#        columns = [
#            col.strip()
#            for col in columns_text.split(",")
#        ]
#
#        result["columns"] = columns
#
#    return result
#-------------------------------------------------------
def detect_measures(columns):

    return [
        col
        for col in columns
        if any(
            keyword in col.lower()
            for keyword in MEASURE_KEYWORDS
        )
    ]
#-------------------------------------------------------
def detect_dimensions(
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

    # -------------------------
    # REMOVE DUPLICATES
    # -------------------------

    dimensions = list(dict.fromkeys(dimensions))

    return dimensions
#-------------------------------------------------------
def detect_date_columns(columns):

    return [
        col
        for col in columns
        if any(
            keyword in col.lower()
            for keyword in DATE_COLUMN_KEYWORDS
        )
    ]

#-------------------------------------------------------
def detect_time_filter(prompt: str):

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
#-------------------------------------------------------
def detect_order_strategy(
    intent,
    measures,
    date_columns,
    time_filter
):

    # -------------------------
    # REPORT
    # -------------------------

    if intent == "report" and measures:

        return {
            "type": "measure_desc",
            "measure": measures[0]
        }

    # -------------------------
    # RAW
    # -------------------------
    if (
        intent == "raw"
        and date_columns
        and not (
            time_filter
            and time_filter.get("period") == "day"
        )
    ):
        return {
            "type": "latest_date",
            "column": date_columns[0]
            
        }

    return None
#-------------------------------------------------------
def detect_limit_strategy(prompt: str):

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
    
#-----------------------------------------------------------
def build_join_plan(
    required_tables,
    relationships
):

    # -------------------------
    # SINGLE TABLE
    # -------------------------
    print("REQUIRED =", required_tables)
    print("RELATIONSHIPS =", relationships)
    
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
#----------------------------------------------------------
def detect_count_target(prompt, semantic_targets):

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
#------------------------------------------------------------
def detect_grouping_dimensions(
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
                            display_targets[
                                business_term
                            ]
                        )

                else:

                    if business_term in semantic_targets:

                        dimensions.append(
                            semantic_targets[
                                business_term
                            ]
                        )

                break

    return dimensions
    
#def detect_grouping_dimensions(
#        prompt,
#        semantic_targets,
#        display_targets,
#        BUSINESS_TERMS
#    ):
#
#    prompt = prompt.lower()
#    
#    dimensions = []
#
#
#    words = prompt.split()
#
#    use_display = any( word in words for word in DISPLAY_KEYWORDS )
#
#    for business_term, aliases in BUSINESS_TERMS.items():
#        
#
#        for alias in aliases:
#            
#            if alias in words:
#
#                if use_display:
#            
#                    if business_term in display_targets:
#            
#                        dimensions.append(
#                            display_targets[
#                                business_term
#                            ]
#                        )
#            
#                else:
#            
#                    if business_term in semantic_targets:
#            
#                        dimensions.append(
#                            semantic_targets[
#                                business_term
#                            ]
#                        )
#            
#                break
#            
#            
#
##            if alias in words:
##            
##               
##                if business_term in semantic_targets:
##
##                    dimensions.append(
##                        semantic_targets[business_term]
##                    )
##                    
##                    break
#    
#    return dimensions
#------------------------------------------------------------
def detect_aggregation_function(prompt):

    prompt = prompt.lower()

    if "total" in prompt or "sum" in prompt:
        return "SUM"

    if "average" in prompt or "avg" in prompt:
        return "AVG"

    if "maximum" in prompt or "max" in prompt or "highest" in prompt:
        return "MAX"

    if "minimum" in prompt or "min" in prompt or "lowest" in prompt:
        return "MIN"

    if "count" in prompt or "number of" in prompt or "how many" in prompt:
        return "COUNT"

    return None
#----------------------------------------------------------
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
#----------------------------------------------------------
def extract_grouping_terms(prompt):
    
    match = re.search(
            r"\bby\b(.+)",
            prompt
        )
     
    if match:
        return match.group(1).strip()
    
    return  ""

#------------------------------------------------------------
def detect_requested_dimensions(prompt: str,columns: list,date_columns):
    
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
#----------------------------------------------------------
def detect_ranking_strategy(prompt):

    prompt = prompt.lower()

    if "highest" in prompt:

        return {
            "type": "top_n",
            "limit": 1
        }

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

    return None
#----------------------------------------------------------------------
def detect_ranking_dimensions(
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
#-----------------------------------------------------------------------------
def build_semantic_targets(schema, BUSINESS_TERMS):

    all_columns = extract_all_columns(schema)
    
    id_columns = extract_id_columns(all_columns)

    # -----------------------------
    # ROOT MAPPING
    # -----------------------------
    count_targets = {}

    for col in id_columns:
        
        root = strip_relationship_suffix(col)
        
        count_targets[root] = col

    # -----------------------------
    # SEMANTIC MATCHING (FIXED)
    # -----------------------------
    semantic_targets = {}

    for root, column in count_targets.items():

        for business_term, aliases in BUSINESS_TERMS.items():

            for alias in aliases:

                if (
                    root in alias
                    or alias in root
                ):
                    semantic_targets[business_term] = column
                    break

    return semantic_targets
#--------------------------------------------------------------------------
def detect_having_condition(
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
    
#---------------------------------------------------------------------------
def prepare_query_context(prompt,schema):
    
    
    try:
        required_tables = detect_required_tables(prompt,schema)
    
        relationships = detect_relationships(schema)
        #------------------------------------------
        print("SCHEMA =", schema)
        print("REQUIRED =", required_tables)
        #---------------------------------------
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
                
        display_targets = (
                build_display_targets(
                    schema,
                    BUSINESS_TERMS
                )
            )
        
        alias_map = build_alias_map(
                        required_tables
                    )
        
        
            
        semantic_targets = build_semantic_targets(schema, BUSINESS_TERMS)

        return {
            "required_tables": required_tables,
            "relationships": relationships,
            "join_plan": join_plan,
            "columns": columns,
            "alias_map": alias_map,
            "semantic_targets": semantic_targets,
            "display_targets": display_targets
        }
    except Exception as e:
        traceback.print_exc()
#---------------------------------------------------------------------------
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
    # RANKING
    # -------------------

    if ranking_strategy and intent == "raw":
        intent = "report"

    return intent
#-------------------------------------------------
def resolve_dimensions(
    prompt,
    columns,
    measures,
    date_columns,
    ranking_strategy,
    has_aggregation,
    group_dimensions,
    intent
):

    if ranking_strategy:

        ranking_dimensions = detect_ranking_dimensions(
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

        requested_dimensions = detect_requested_dimensions(
            prompt,
            columns,
            date_columns
        )

        if requested_dimensions:
            return requested_dimensions

        if intent == "report":

            return detect_dimensions(
                columns,
                measures,
                date_columns
            )

        return []

    return detect_dimensions(
        columns,
        measures,
        date_columns
    )

#--------------------------------------------------------------------------
def discover_relationships( schema, relationship_hints=None):
            
    if relationship_hints is None:
        relationship_hints = {}
        
    relationships = []
    
    tables = list(
        schema.keys()
    )
    
    for i in range(len(tables)):

        left_table = tables[i]
    
        for j in range(i + 1, len(tables)):
    
            right_table = tables[j]
    
            left_columns = set(
                schema[left_table]
            )
    
            right_columns = set(
                schema[right_table]
            )
    
            common_columns = (
                left_columns &
                right_columns
            )
    
            for column in common_columns:
    
                if not is_relationship_column(column):
                    continue
                    
                relationships.append({
    
                    "left_table": left_table,
                    "right_table": right_table,
    
                    "left_column": column,
                    "right_column": column
                })
        
    return relationships
#--------------------------------------------------------------------------
def build_query_plan(prompt: str, schema: dict):
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
    try:
        context = prepare_query_context(prompt,schema)
    except Exception as e:
        traceback.print_exc()
    
    required_tables = context["required_tables"]
    relationships = context["relationships"]
    join_plan = context["join_plan"]
    columns = context["columns"]
    alias_map = context["alias_map"]
    semantic_targets = context["semantic_targets"]
    
    display_targets = (context["display_targets"])
    
    print("DISPLAY_TARGETS =", display_targets)
    
    aggregation_function = detect_aggregation_function(prompt)
    
    count_target = None
    
    clean_prompt = prompt.lower()

    clean_prompt = clean_prompt.split("\n")[0]
    
    if ":" in clean_prompt:
        clean_prompt = clean_prompt.split(":")[-1].strip()
    
    count_part = clean_prompt
    group_part = ""
    
    if " by " in clean_prompt:
    
        parts = clean_prompt.split(" by ", 1)
    
        count_part = parts[0]
    
        group_part = parts[1]
    

    if aggregation_function and aggregation_function.lower() == "count":
        count_target = detect_count_target(
            count_part,
            semantic_targets
        )


    group_source = group_part if group_part else clean_prompt

    group_dimensions = detect_grouping_dimensions(
        group_source,
        semantic_targets,
        display_targets,
        BUSINESS_TERMS
    )

    ranking_strategy = detect_ranking_strategy(prompt)
   
    # -------------------
    # INTENT
    # -------------------
    
    intent = detect_intent(
            prompt,
            aggregation_function,
            group_dimensions,
            ranking_strategy
        )
    
    if intent == "report" and not aggregation_function:
        aggregation_function = "SUM"
    

    # -------------------
    # TIME FILTER
    # -------------------

    time_filter = detect_time_filter(prompt)
    

    # -------------------------
    # SAFE RAW POLICY
    # -------------------------
    
    if intent == "raw" and not time_filter:
    
        time_filter = {
            "type": "relative_period",
            "period": "day",
            "offset": 0
        }
    
    date_columns = detect_date_columns(columns)
    
#    print("COLUMNS =", columns)
#    print("DATE_COLUMNS =", date_columns)

    # -------------------
    # MEASURES
    # -------------------
#    print("COLUMNS =", columns)
#    print("REQUIRED =", required_tables)
    
    measures = detect_measures(columns)
    
    has_aggregation = (
        intent in ["report", "kpi"]
        and len(measures) > 0
    )

    # -------------------
    # DIMENSIONS
    # -------------------
    if ranking_strategy and not aggregation_function:
        aggregation_function = "SUM"
    
#    try:

    dimensions = resolve_dimensions(
                prompt,
                columns,
                measures,
                date_columns,
                ranking_strategy,
                has_aggregation,
                group_dimensions,
                intent
            )
#    except Exception as e:
#        traceback.print_exc()
        

    order_strategy = detect_order_strategy(
                        intent,
                        measures,
                        date_columns,
                        time_filter
                    )

    limit_strategy = detect_limit_strategy(
                        prompt
                    )
                    
    if ranking_strategy and not limit_strategy:
        
        limit_strategy = ranking_strategy
    

    if intent == "raw":

        for date_col in date_columns:
    
            if date_col not in dimensions:
                dimensions.append(date_col)
    # -------------------
    # TABLE
    # -------------------

    having_condition = detect_having_condition(
            prompt,
            measures,
            aggregation_function
        )
    # -------------------
    # RETURN PLAN
    # -------------------
#    print("REQUIRED =", required_tables)
#    print("COLUMNS =", columns)
#    print("MEASURES =", measures)
#    print("DIMENSIONS =", dimensions)
#    print("GROUP_DIMENSIONS =", group_dimensions)
    
    return {
        "intent": intent,
        "measures": measures,
        "dimensions": dimensions,
        "date_columns": date_columns,
        "time_filter": time_filter,
        "has_aggregation": has_aggregation,
        "order_strategy": order_strategy ,
        "limit_strategy": limit_strategy,
        "required_tables": required_tables,
        "relationships": relationships,
        "join_plan":join_plan,
        "alias_map": alias_map,
        "schema": schema,
        "aggregation_function": aggregation_function,
        "count_target": count_target,
        "group_dimensions": group_dimensions,
        "having_condition":having_condition
        
    }
