"""Regression contracts for ranking and detail selection."""

RANKING_SELECTION_REGRESSION_CASES = [
    {
        "id": "REG-001",
        "name": "Top 5 factories by production",
        "prompt": "show top 5 factories by production",
        "expected": {
            "intent": "report",
            "aggregation_function": "SUM",
            "has_aggregation": True,
            "dimensions": ["factory_id"],
            "group_dimensions": [],
            "order_strategy": {
                "type": "measure_desc",
                "measure": "qty",
            },
            "limit_strategy": {
                "type": "top_n",
                "limit": 5,
            },
            "ast_group_by": ["factory_id"],
            "ast_order_by": [
                {"column": "total_qty", "direction": "DESC"}
            ],
            "ast_limit": {
                "type": "top_n",
                "count": 5,
            },
            "sql_required": [
                "SELECT FIRST 5",
                "SUM(pt.qty) AS total_qty",
                "GROUP BY",
                "pt.factory_id",
                "ORDER BY",
                "total_qty DESC",
            ],
            "sql_forbidden": [],
        },
    },
    {
        "id": "REG-002",
        "name": "Bottom 5 factories by production",
        "prompt": "show bottom 5 factories by production",
        "expected": {
            "intent": "report",
            "aggregation_function": "SUM",
            "has_aggregation": True,
            "dimensions": ["factory_id"],
            "group_dimensions": [],
            "order_strategy": {
                "type": "measure_asc",
                "measure": "qty",
            },
            "limit_strategy": {
                "type": "bottom_n",
                "limit": 5,
            },
            "ast_group_by": ["factory_id"],
            "ast_order_by": [
                {"column": "total_qty", "direction": "ASC"}
            ],
            "ast_limit": {
                "type": "bottom_n",
                "count": 5,
            },
            "sql_required": [
                "SELECT FIRST 5",
                "SUM(pt.qty) AS total_qty",
                "GROUP BY",
                "pt.factory_id",
                "ORDER BY",
                "total_qty ASC",
            ],
            "sql_forbidden": [],
        },
    },
    {
        "id": "REG-003",
        "name": "Latest 5 production transactions",
        "prompt": "latest 5 production transactions",
        "expected": {
            "intent": "raw",
            "aggregation_function": None,
            "has_aggregation": False,
            "dimensions": ["factory_id", "prod_id", "prod_date"],
            "group_dimensions": [],
            "order_strategy": {
                "type": "latest_date",
                "column": "prod_date",
            },
            "limit_strategy": {
                "type": "latest_n",
                "limit": 5,
            },
            "time_filter": None,
            "ast_group_by": [],
            "ast_order_by": [
                {"column": "prod_date", "direction": "DESC"}
            ],
            "ast_limit": {
                "type": "latest_n",
                "count": 5,
            },
            "sql_required": [
                "SELECT FIRST 5",
                "pt.factory_id",
                "pt.prod_id",
                "pt.prod_date",
                "pt.qty",
                "ORDER BY",
                "pt.prod_date DESC",
            ],
            "sql_forbidden": [
                "SUM(",
                "GROUP BY",
                "WHERE pt.prod_date = TODAY",
            ],
        },
    },
    {
        "id": "REG-004",
        "name": "First 5 production transactions",
        "prompt": "first 5 production transactions",
        "expected": {
            "intent": "raw",
            "aggregation_function": None,
            "has_aggregation": False,
            "dimensions": ["factory_id", "prod_id", "prod_date"],
            "group_dimensions": [],
            "order_strategy": {
                "type": "earliest_date",
                "column": "prod_date",
            },
            "limit_strategy": {
                "type": "first_n",
                "limit": 5,
            },
            "time_filter": None,
            "ast_group_by": [],
            "ast_order_by": [
                {"column": "prod_date", "direction": "ASC"}
            ],
            "ast_limit": {
                "type": "first_n",
                "count": 5,
            },
            "sql_required": [
                "SELECT FIRST 5",
                "pt.factory_id",
                "pt.prod_id",
                "pt.prod_date",
                "pt.qty",
                "ORDER BY",
                "pt.prod_date ASC",
            ],
            "sql_forbidden": [
                "SUM(",
                "GROUP BY",
                "WHERE pt.prod_date = TODAY",
            ],
        },
    },
]
