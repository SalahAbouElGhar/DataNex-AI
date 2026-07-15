from tests.data.test_fixtures import (
    TEST_SALES_SCHEMA,
    TEST_PRODUCTION_SCHEMA,
    TEST_SALES_ALIAS_MAP,
    TEST_PRODUCTION_ALIAS_MAP
)
#---------------------------------------------------
"""
AST Compiler Golden Test Suite

This file contains the official Golden Test cases for the
AST Compiler.

Each test case defines the expected behavior of the compiler
and contains:
- AST input
- Schema input
- Alias map
- Expected SQL output

Any intentional change to the generated SQL must be approved
by updating the corresponding Golden Test.

Every approved test becomes part of the regression suite and
helps protect the compiler against future regressions.
"""

# ============================================================================
# 1 — Raw Queries
# ============================================================================
AST_COMPILER_TEST_CASES = []

AST_COMPILER_TEST_CASES += [
 
    {

        "id": "AST-001",
        "name": "Raw Select - Production Today",
        "description": "Verify compilation of a raw SELECT with today",

        "tags": [

            "raw",
            "relative_period",
            "Production",
            "today"
        
        ],
        
        "input": {

            "ast": {
                "select": [
                    {"type": "column", "column": "factory_id"},
                    {"type": "column", "column": "prod_id"},
                    {"type": "column", "column": "prod_date"},
                    {"type": "column", "column": "qty"}
                ],
    
                "from": "prod_tbl",
    
                "joins": [],
    
                "where": [
                    {
                        "type": "relative_period",
                        "column": "prod_date",
                        "period": "day",
                        "offset": 0
                    }
                ],
    
                "group_by": [],
    
                "having": [],
    
                "order_by": [
                    {
                        "column": "factory_id",
                        "direction": "ASC"
                    },
                    {
                        "column": "prod_id",
                        "direction": "ASC"
                    }
                ],
    
                "limit": None
            },
            "schema": TEST_PRODUCTION_SCHEMA,

            "alias_map": TEST_PRODUCTION_ALIAS_MAP
        },

        "expected": {
            "sql": """
SELECT
  pt.factory_id,
  pt.prod_id,
  pt.prod_date,
  pt.qty

FROM prod_tbl pt

WHERE pt.prod_date = TODAY

ORDER BY
  pt.factory_id ASC,
  pt.prod_id ASC
""".strip()
        }

    },
# -----------------------------------------------------------------------------------
    {

        "id": "AST-002",
        "name": "Raw Select - Production Yesterday",
        "description": "Verify compilation of a raw SELECT with yesterday's relative date filter.",

        "tags": [

            "raw",
            "relative_period",
            "Production",
            "yesterday"
        
        ],
        
        "input": {

            "ast": {
                    "select": [
                        {"type": "column", "column": "factory_id"},
                        {"type": "column", "column": "prod_id"},
                        {"type": "column", "column": "prod_date"},
                        {"type": "column", "column": "qty"}
                    ],
                    "from": "prod_tbl",
                    "joins": [],
                    "where": [{"type": "relative_period",
                                "column": "prod_date",
                                "period": "day",
                                "offset": -1}],
                    "group_by": [],
                    "having": [],
                    "order_by": [{"column": "factory_id", "direction": "ASC"},
                                {"column": "prod_id", "direction": "ASC"}],
                    "limit": None},
            "schema": TEST_PRODUCTION_SCHEMA,

            "alias_map": TEST_PRODUCTION_ALIAS_MAP
        },

        "expected": {
            "sql": """
SELECT
  pt.factory_id,
  pt.prod_id,
  pt.prod_date,
  pt.qty

FROM prod_tbl pt

WHERE pt.prod_date = TODAY - 1

ORDER BY
  pt.factory_id ASC,
  pt.prod_id ASC
""".strip()
        }

    }
    ]
    
# ============================================================================
# 2 — Basic Aggregation
# ============================================================================

AST_COMPILER_TEST_CASES += [
    {

        "id": "AST-010",
        "name": "Report - Row Count",
        "description": ("Verify compilation of a report with COUNT(*) aggregation."),

        "tags": [
                "report",
                "count",
                "count_rows",
                "Production"
                
            ],
        
        "input": {

            "ast":
                {
                "select": 
                    [
                    {
                    "type": "count_rows",
                    "alias": "row_count"
                    }
                    ],
                "from": "prod_tbl",
                "joins": [],
                "where": [],
                "group_by": [],
                "having": [],
                "order_by": [],
                "limit": None},
            "schema": TEST_PRODUCTION_SCHEMA,

            "alias_map": TEST_PRODUCTION_ALIAS_MAP
        },

        "expected": {
            "sql": """
SELECT
  COUNT(*) AS row_count

FROM prod_tbl pt
""".strip()
        }
    
    },
# -----------------------------------------------------------------------------------
    {

        "id": "AST-011",
        "name": "Report - Total Production by Factory",
        "description": (
                    "Verify compilation of a report with "
                    "SUM aggregation grouped by factory."
                ),

        "tags": [
                "report",
                "sum",
                "aggregation",
                "Production",
                "group_by"
            ],
        
        "input": {

            "ast": {
                    "select": [
                        {
                            "type": "column",
                            "column": "factory_id"
                        },
                        {
                            "type": "aggregation",
                            "function": "SUM",
                            "column": "qty",
                            "alias": "total_qty"
                        }
                    ],
                
                    "from": "prod_tbl",
                
                    "joins": [],
                
                    "where": [],
                
                    "group_by": [
                        "factory_id"
                    ],
                
                    "having": [],
                
                    "order_by": [
                        {
                            "column": "total_qty",
                            "direction": "DESC"
                        }
                    ],
                
                    "limit": None
                },
            "schema": TEST_PRODUCTION_SCHEMA,

            "alias_map": TEST_PRODUCTION_ALIAS_MAP
        },

        "expected": {
            "sql": """
SELECT
  pt.factory_id,
  SUM(pt.qty) AS total_qty

FROM prod_tbl pt

GROUP BY 
  pt.factory_id

ORDER BY
  total_qty DESC
""".strip()
        }

    },
# -----------------------------------------------------------------------------------
    {

        "id": "AST-012",
        "name": "Report - Average Production by Factory",
        "description": ("Verify compilation of a report with AVG aggregation grouped by factory."),

        "tags": [
                "report",
                "avg",
                "group_by",
                "Production"
                
            ],
        
        "input": {

            "ast": {
                "select": [
                            {
                            "type": "column",
                            "column": "factory_id"
                            },
                            {
                            "type": "aggregation",
                            "function": "AVG",
                            "column": "qty",
                            "alias": "average_qty"
                            }
                            ],
                "from": "prod_tbl",
                "joins": [],
                "where": [],
                "group_by": ["factory_id"],
                "having": [],
                "order_by": [
                            {
                            "column": "average_qty",
                            "direction": "DESC"
                            }
                            ],
                "limit": None
                },
            "schema": TEST_PRODUCTION_SCHEMA,

            "alias_map": TEST_PRODUCTION_ALIAS_MAP
        },

        "expected": {
            "sql": """
SELECT
  pt.factory_id,
  AVG(pt.qty) AS average_qty

FROM prod_tbl pt

GROUP BY 
  pt.factory_id

ORDER BY
  average_qty DESC
""".strip()
        }
    
    },
# -----------------------------------------------------------------------------------
   {

        "id": "AST-013",
        "name": "Report - Maximum Production by Factory",
        "description": ("Verify compilation of a report with MAX aggregation grouped by factory."),

        "tags": [
                "report",
                "max",
                "group_by",
                "Production"
                
            ],
        
        "input": {

            "ast": {
                "select": [
                            {
                            "type": "column",
                            "column": "factory_id"
                            },
                            {
                            "type": "aggregation",
                            "function": "MAX",
                            "column": "qty",
                            "alias": "maximum_qty"
                            }
                          ],
                "from": "prod_tbl",
                "joins": [],
                "where": [],
                "group_by": ["factory_id"],
                "having": [],
                "order_by": [
                            {
                            "column": "maximum_qty",
                            "direction": "DESC"
                            }
                            ],
                "limit": None},
            "schema": TEST_PRODUCTION_SCHEMA,

            "alias_map": TEST_PRODUCTION_ALIAS_MAP
        },

        "expected": {
            "sql": """
SELECT
  pt.factory_id,
  MAX(pt.qty) AS maximum_qty

FROM prod_tbl pt

GROUP BY 
  pt.factory_id

ORDER BY
  maximum_qty DESC
""".strip()
        }
    
    },
# -----------------------------------------------------------------------------------
    {

        "id": "AST-014",
        "name": "Report - Minimum Production by Factory",
        "description": ("Verify compilation of a report with MIN aggregation grouped by factory."),

        "tags": [
                "report",
                "min",
                "group_by",
                "Production"
                
            ],
        
        "input": {

            "ast": {
                "select": 
                    [
                    {
                    "type": "column",
                    "column": "factory_id"
                    },
                    {
                    "type": "aggregation",
                    "function": "MIN",
                    "column": "qty",
                    "alias": "minimum_qty"
                    }
                    ],
                "from": "prod_tbl",
                "joins": [],
                "where": [],
                "group_by": ["factory_id"],
                "having": [],
                "order_by": 
                    [
                    {
                    "column": "minimum_qty",
                    "direction": "DESC"
                    }
                    ],
                "limit": None},
            "schema": TEST_PRODUCTION_SCHEMA,

            "alias_map": TEST_PRODUCTION_ALIAS_MAP
        },

        "expected": {
            "sql": """
SELECT
  pt.factory_id,
  MIN(pt.qty) AS minimum_qty

FROM prod_tbl pt

GROUP BY 
  pt.factory_id

ORDER BY
  minimum_qty DESC
""".strip()
        }
    
    },
# -----------------------------------------------------------------------------------
    {

        "id": "AST-015",
        "name": "Report - Distinct Product Count by Factory",
        "description": ("Verify compilation of a report with COUNT DISTINCT aggregation grouped by factory."),

        "tags": [
                "report",
                "count_distinct",
                "group_by",
                "Production"
                
            ],
        
        "input": {

            "ast": {
                "select": [
                            {
                            "type": "column",
                            "column": "factory_id"
                            },
                            {
                            "type": "count_distinct",
                            "column": "prod_id",
                            "alias": "prod_count"
                            }
                            ],
                "from": "prod_tbl",
                "joins": [],
                "where": [],
                "group_by": [
                            "factory_id"
                            ],
                "having": [],
                "order_by": [
                            {
                            "column": "prod_count",
                            "direction": "DESC"
                            }
                            ],
                "limit": None
                },
            "schema": TEST_PRODUCTION_SCHEMA,

            "alias_map": TEST_PRODUCTION_ALIAS_MAP
        },

        "expected": {
            "sql": """
SELECT
  pt.factory_id,
  COUNT(DISTINCT pt.prod_id) AS prod_count

FROM prod_tbl pt

GROUP BY 
  pt.factory_id

ORDER BY
  prod_count DESC
""".strip()
        }
    
    }

    ]
#==================================================
#   3 — HAVING
#==================================================
AST_COMPILER_TEST_CASES += [
    {

        "id": "AST-020",
        "name": "Report - Factories with Total Production > 1000",
        "description": (
                "Verify compilation of a report with SUM aggregation "
                "grouped by factory and filtered using a HAVING clause."
                ),

        "tags": [
                "report",
                "sum",
                "group_by",
                "having",
                "Production"
            ],
        
        "input": {

            "ast": {
            "select": [
                {
                "type": "column", 
                "column": "factory_id"
                },
                
                { 
                "type": "aggregation",
                "function": "SUM",
                  "column": "qty",
                   "alias": "total_qty"
                   }
                   ],
            "from": "prod_tbl",
            "joins": [],
            "where": [],
            "group_by": ["factory_id"],
            "having": [
                        {
                        "function": "SUM",
                        "column": "qty",
                        "operator": ">",
                        "value": 1000
                        }
                        ],
            "order_by": [
                        {
                        "column": "total_qty",
                        "direction": "DESC"
                        }
                        ],
            "limit": None
            },
            "schema": TEST_PRODUCTION_SCHEMA,

            "alias_map": TEST_PRODUCTION_ALIAS_MAP
        },

        "expected": {
            "sql": """
SELECT
  pt.factory_id,
  SUM(pt.qty) AS total_qty

FROM prod_tbl pt

GROUP BY 
  pt.factory_id

HAVING
  SUM(pt.qty) > 1000

ORDER BY
  total_qty DESC
""".strip()
    }
    }
    ]
   
# ============================================================================
# 4 — Ranking
# ============================================================================

AST_COMPILER_TEST_CASES += [
    {

        "id": "AST-030",
        "name": "Report - Top 10 Factories by Production",
        "description": ("Verify compilation of a report that returns the top 10 factories by total production."),

        "tags": [
                "report",
                "top_n",
                "first",
                "limit",
                "Production"
                               
            ],
        
        "input": {

            "ast":
                {
                "select": 
                    [
                    {
                    "type": "column",
                    "column": "factory_id"
                    },
                    {
                    "type": "aggregation",
                    "function": "SUM",
                    "column": "qty",
                    "alias": "total_qty"
                    }
                    ],
                "from": "prod_tbl",
                "joins": [],
                "where": [],
                "group_by": 
                    [
                    "factory_id"
                    ],
                "having": [],
                "order_by": 
                    [
                    {
                    "column": "total_qty",
                    "direction": "DESC"
                    }
                    ],
                "limit": 
                    {
                    "type": "top_n",
                    "count": 10
                    }
                },
            "schema": TEST_PRODUCTION_SCHEMA,

            "alias_map": TEST_PRODUCTION_ALIAS_MAP
        },

        "expected": {
            "sql": """
SELECT FIRST 10 
  pt.factory_id,
  SUM(pt.qty) AS total_qty

FROM prod_tbl pt

GROUP BY 
  pt.factory_id

ORDER BY
  total_qty DESC
""".strip()
        }
    
    }
    ]
# ============================================================================
# 5 — Time Intelligence
# ============================================================================

AST_COMPILER_TEST_CASES += [
    {

        "id": "AST-040",
        "name": "Report - Production Report This Year",
        "description": ("Verify compilation of a production report filtered to the current year."),

        "tags": [
                "report",
                "relative_period",
                "year",
                "Production"
                
            ],
        
        "input": {

            "ast":
                {
                "select": 
                    [
                    {
                    "type": "column",
                    "column": "factory_id"
                    },
                    {
                    "type": "column",
                    "column": "prod_id"
                    },
                    {
                    "type": "aggregation",
                    "function": "SUM",
                    "column": "qty",
                    "alias": "total_qty"
                    }
                    ],
                "from": "prod_tbl",
                "joins": [],
                "where": 
                    [
                    {
                    "type": "relative_period",
                    "column": "prod_date",
                    "period": "year",
                    "offset": 0
                    }
                    ],
                "group_by": 
                    [
                    "factory_id",
                    "prod_id"
                    ],
                "having": [],
                "order_by": 
                    [
                    {
                    "column": "total_qty",
                    "direction": "DESC"
                    }
                    ],
                "limit": None
                },
            "schema": TEST_PRODUCTION_SCHEMA,

            "alias_map": TEST_PRODUCTION_ALIAS_MAP
        },

        "expected": {
            "sql": """
SELECT
  pt.factory_id,
  pt.prod_id,
  SUM(pt.qty) AS total_qty

FROM prod_tbl pt

WHERE pt.prod_date >= TODAY - 365

GROUP BY 
  pt.factory_id,
  pt.prod_id

ORDER BY
  total_qty DESC
""".strip()
        }
    
    },
# ----------------------------------------------------------------------------------
    {

        "id": "AST-041",
        "name": "Report - Monthly Production by Factory and Product",
        "description": ("Verify compilation of a report with a monthly relative date filter."),

        "tags": [
                "report",
                "relative_period",
                "month",
                "Production"
                
            ],
        
        "input": {

            "ast":
                {
                "select": 
                    [
                    {
                    "type": "column",
                    "column": "factory_id"
                    },
                    {
                    "type": "column",
                    "column": "prod_id"
                    },
                    {
                    "type": "aggregation",
                    "function": "SUM",
                    "column": "qty",
                    "alias": "total_qty"
                    }
                    ],
                "from": "prod_tbl",
                "joins": [],
                "where": 
                    [
                    {
                    "type": "relative_period",
                    "column": "prod_date",
                    "period": "month",
                    "offset": 0
                    }
                    ],
                "group_by": 
                    [
                    "factory_id",
                    "prod_id"
                    ],
                "having": [],
                "order_by": 
                    [
                    {
                    "column": "total_qty",
                    "direction": "DESC"
                    }
                    ],
                "limit": None
                },
            "schema": TEST_PRODUCTION_SCHEMA,

            "alias_map": TEST_PRODUCTION_ALIAS_MAP
        },

        "expected": {
            "sql": """
SELECT
  pt.factory_id,
  pt.prod_id,
  SUM(pt.qty) AS total_qty

FROM prod_tbl pt

WHERE pt.prod_date >= TODAY - 30

GROUP BY 
  pt.factory_id,
  pt.prod_id

ORDER BY
  total_qty DESC
""".strip()
        }
    
    }
    ]
# ============================================================================
# 6 — JOIN & Display Columns
# ============================================================================
AST_COMPILER_TEST_CASES += [


    {

        "id": "AST-050",

        "name": "Report - Production summary by product name",
        
        "description": "Verify SQL generation for production aggregated by product display name using INNER JOIN.",

        "tags": [
                    "report",
                    "aggregation",
                    "join",
                    "group-by",
                    "display-column",
                    "production"
                ],
        
        "input": {

            "ast":
                {
                'select': [
                            {'type': 'column', 'column': 'prod_name'},
                            {
                            'type': 'aggregation',
                            'function': 'SUM',
                            'column': 'qty',
                            'alias': 'total_qty'
                            }
                        ],
                'from': 'prod_tbl',
                'joins': [
                            {'join_type': 'INNER',
                            'left_table': 'prod_tbl',
                            'right_table': 'prod_desc',
                            'left_column': 'prod_id',
                            'right_column': 'prod_id'}
                        ],
                'where': [],
                'group_by': ['prod_name'],
                'having': [],
                'order_by': [
                            {'column': 'total_qty', 'direction': 'DESC'}
                            ],
                'limit': None
                 },
            "schema": TEST_PRODUCTION_SCHEMA,

            "alias_map": TEST_PRODUCTION_ALIAS_MAP
            },

        "expected": {
            "sql": """
SELECT
  pd.prod_name,
  SUM(pt.qty) AS total_qty

FROM prod_tbl pt

INNER JOIN prod_desc pd
    ON pt.prod_id = pd.prod_id

GROUP BY 
  pd.prod_name

ORDER BY
  total_qty DESC
""".strip()
        }
    },
# -----------------------------------------------------------------------------------
    {

        "id": "AST-051",

        "name": "Report - Total sales by customer name and product name",
        
        "description":(
                        "Verify SQL generation for sales aggregated by customer and product display names ",
                        "across multiple INNER JOIN operations."
                        ),

        "tags": [
                    "report",
                    "aggregation",
                    "join",
                    "group-by",
                    "display-column",
                    "sales"
                ],
        
        "input": {

            "ast":
                {
                'select': [
                    {'type': 'column', 'column': 'prod_name'},
                    {'type': 'column', 'column': 'cust_name'},
                    {'type': 'aggregation',
                    'function': 'SUM',
                    'column': 'sales_amount',
                    'alias': 'total_sales_amount'}
                    ],
                'from': 'sales_tbl',
                'joins': [
                        {'join_type': 'INNER',
                        'left_table': 'sales_tbl',
                        'right_table': 'customer_tbl',
                        'left_column': 'cust_no',
                        'right_column': 'cust_no'},
                        {'join_type': 'INNER',
                        'left_table': 'sales_tbl',
                        'right_table': 'product_tbl',
                        'left_column': 'prod_id',
                        'right_column': 'prod_id'}
                        ],
                'where': [],
                'group_by': ['prod_name', 'cust_name'],
                'having': [],
                'order_by': [
                        {'column': 'total_sales_amount', 'direction': 'DESC'}
                        ],
                'limit': None},
            "schema": TEST_SALES_SCHEMA,

            "alias_map": TEST_SALES_ALIAS_MAP
            },

        "expected": {
            "sql": """
SELECT
  pt.prod_name,
  ct.cust_name,
  SUM(st.sales_amount) AS total_sales_amount

FROM sales_tbl st

INNER JOIN customer_tbl ct
    ON st.cust_no = ct.cust_no
INNER JOIN product_tbl pt
    ON st.prod_id = pt.prod_id

GROUP BY 
  pt.prod_name,
  ct.cust_name

ORDER BY
  total_sales_amount DESC
""".strip()
        }
    }
    
    ]
# -----------------------------------------------------------------------------------


