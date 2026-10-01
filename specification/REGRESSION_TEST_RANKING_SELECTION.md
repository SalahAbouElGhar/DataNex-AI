# DataNex AI — Ranking / Selection Regression Test

## Purpose

This regression suite protects the currently verified end-to-end behavior for:

1. Top N report ranking
2. Bottom N report ranking
3. Latest N detail selection
4. First N detail selection

The expected behavior is checked across four conceptual layers:

Prompt
→ Reasoning Facts
→ Business Decision
→ Query Plan
→ AST
→ Final SQL

---

## Regression Cases

### Case 1 — Top 5 factories by production

Prompt:

    show top 5 factories by production

Expected Reasoning Facts:

    aggregation_function = "SUM"
    intent = "report"
    requested_measure = "production"
    business_group_dimensions = ["factory"]
    ranking_strategy = {
        "type": "top_n",
        "limit": 5
    }
    time_filter = None

Expected Business Decision:

    business_objective = "REPORT"
    primary_entity = "factory"
    requires_measure = True
    measure = "production"
    aggregation = "SUM"
    display_entities = ["factory"]
    grouping_entities = ["factory"]
    ranking = {
        "type": "top_n",
        "limit": 5
    }
    ordering = None
    time_filter = None

Expected Query Plan semantics:

    aggregation_function = "SUM"
    dimensions includes "factory_id"
    measures includes "qty"
    order_strategy = {
        "type": "measure_desc",
        "measure": "qty"
    }
    limit_strategy = {
        "type": "top_n",
        "limit": 5
    }
    has_aggregation = True

Expected AST semantics:

    group_by = ["factory_id"]
    order_by contains:
        column = "total_qty"
        direction = "DESC"
    limit contains:
        type = "top_n"
        count = 5

Expected SQL semantics:

    SELECT FIRST 5
        pt.factory_id,
        SUM(pt.qty) AS total_qty
    FROM prod_tbl pt
    GROUP BY pt.factory_id
    ORDER BY total_qty DESC

---

### Case 2 — Bottom 5 factories by production

Prompt:

    show bottom 5 factories by production

Expected Reasoning Facts:

    aggregation_function = "SUM"
    intent = "report"
    requested_measure = "production"
    business_group_dimensions = ["factory"]
    ranking_strategy = {
        "type": "bottom_n",
        "limit": 5
    }
    time_filter = None

Expected Business Decision:

    business_objective = "REPORT"
    primary_entity = "factory"
    requires_measure = True
    measure = "production"
    aggregation = "SUM"
    display_entities = ["factory"]
    grouping_entities = ["factory"]
    ranking = {
        "type": "bottom_n",
        "limit": 5
    }
    ordering = None
    time_filter = None

Expected Query Plan semantics:

    aggregation_function = "SUM"
    dimensions includes "factory_id"
    measures includes "qty"
    order_strategy = {
        "type": "measure_asc",
        "measure": "qty"
    }
    limit_strategy = {
        "type": "bottom_n",
        "limit": 5
    }
    has_aggregation = True

Expected AST semantics:

    group_by = ["factory_id"]
    order_by contains:
        column = "total_qty"
        direction = "ASC"
    limit contains:
        type = "bottom_n"
        count = 5

Expected SQL semantics:

    SELECT FIRST 5
        pt.factory_id,
        SUM(pt.qty) AS total_qty
    FROM prod_tbl pt
    GROUP BY pt.factory_id
    ORDER BY total_qty ASC

---

### Case 3 — Latest 5 production transactions

Prompt:

    latest 5 production transactions

Expected Reasoning Facts:

    aggregation_function = None
    intent = "raw"
    requested_measure = "production"
    business_group_dimensions = []
    ranking_strategy = {
        "type": "latest_n",
        "limit": 5
    }
    time_filter = None

Expected Business Decision:

    business_objective = "DETAIL"
    primary_entity = None
    requires_measure = True
    measure = "production"
    aggregation = None
    display_entities = []
    grouping_entities = []
    ranking = {
        "type": "latest_n",
        "limit": 5
    }
    ordering = None
    time_filter = None

Expected Query Plan semantics:

    aggregation_function = None
    dimensions includes:
        "factory_id"
        "prod_id"
        "prod_date"
    measures includes:
        "qty"
    order_strategy = {
        "type": "latest_date",
        "column": "prod_date"
    }
    limit_strategy = {
        "type": "latest_n",
        "limit": 5
    }
    has_aggregation = False

Expected AST semantics:

    group_by = []
    order_by contains:
        column = "prod_date"
        direction = "DESC"
    limit contains:
        type = "latest_n"
        count = 5

Expected SQL semantics:

    SELECT FIRST 5
        pt.factory_id,
        pt.prod_id,
        pt.prod_date,
        pt.qty
    FROM prod_tbl pt
    ORDER BY pt.prod_date DESC

Important regression rule:

    latest_n MUST NOT introduce:
        SUM(...)
        GROUP BY
        TODAY
    unless explicitly requested by the user.

---

### Case 4 — First 5 production transactions

Prompt:

    first 5 production transactions

Expected Reasoning Facts:

    aggregation_function = None
    intent = "raw"
    requested_measure = "production"
    business_group_dimensions = []
    ranking_strategy = {
        "type": "first_n",
        "limit": 5
    }
    time_filter = None

Expected Business Decision:

    business_objective = "DETAIL"
    primary_entity = None
    requires_measure = True
    measure = "production"
    aggregation = None
    display_entities = []
    grouping_entities = []
    ranking = {
        "type": "first_n",
        "limit": 5
    }
    ordering = None
    time_filter = None

Expected Query Plan semantics:

    aggregation_function = None
    dimensions includes:
        "factory_id"
        "prod_id"
        "prod_date"
    measures includes:
        "qty"
    order_strategy = {
        "type": "earliest_date",
        "column": "prod_date"
    }
    limit_strategy = {
        "type": "first_n",
        "limit": 5
    }
    has_aggregation = False

Expected AST semantics:

    group_by = []
    order_by contains:
        column = "prod_date"
        direction = "ASC"
    limit contains:
        type = "first_n"
        count = 5

Expected SQL semantics:

    SELECT FIRST 5
        pt.factory_id,
        pt.prod_id,
        pt.prod_date,
        pt.qty
    FROM prod_tbl pt
    ORDER BY pt.prod_date ASC

Important regression rule:

    first_n MUST NOT introduce:
        SUM(...)
        GROUP BY
        TODAY
    unless explicitly requested by the user.

---

## Cross-case Invariants

These invariants must remain true after future changes.

### Report ranking

    top_n      -> measure_desc -> DESC -> FIRST N
    bottom_n   -> measure_asc  -> ASC  -> FIRST N

### Detail selection

    latest_n   -> latest_date   -> DESC -> FIRST N
    first_n    -> earliest_date -> ASC  -> FIRST N

### Business / Database separation

Business Decision MUST use business concepts:

    factory
    product
    production
    top_n
    bottom_n
    latest_n
    first_n

Business Decision MUST NOT contain database-specific execution details such as:

    factory_id
    prod_id
    prod_date
    qty
    SUM(qty)
    ORDER BY ... SQL syntax

Query Plan / AST are responsible for resolving those database details.

### Explicit ranking versus defaults

When ranking is present:

    top_n
    bottom_n
    latest_n
    first_n

Business Defaults MUST NOT add a conflicting default ordering.

### Detail selection versus aggregation

For:

    latest_n
    first_n

the default state is:

    intent = raw
    aggregation_function = None
    has_aggregation = False

unless the user explicitly requests aggregation.

---

## Current Verified Status

Top N       : PASS
Bottom N    : PASS
Latest N    : PASS
First N     : PASS

This file records the currently verified behavior and should be updated whenever one of these contracts intentionally changes.
