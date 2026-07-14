# tests/test_fixtures.py

# -------------------------------------------------------
# SALES SCHEMA
# -------------------------------------------------------

TEST_SALES_SCHEMA = {
    "tables": {

        "sales_tbl": [
            "sale_no",
            "cust_no",
            "prod_id",
            "sales_amount",
            "sale_date"
        ],

        "customer_tbl": [
            "cust_no",
            "cust_name"
        ],

        "product_tbl": [
            "prod_id",
            "prod_name"
        ]
    }
}

# -------------------------------------------------------
# PRODUCTION SCHEMA
# -------------------------------------------------------

TEST_PRODUCTION_SCHEMA = {
    "tables": {

        "prod_tbl": [
            "factory_id",
            "prod_id",
            "prod_date",
            "qty"
        ],

        "prod_desc": [
            "prod_id",
            "prod_name"
        ]
    }
}

# -------------------------------------------------------
# SALES ALIAS MAP
# -------------------------------------------------------

TEST_SALES_ALIAS_MAP = {

    "sales_tbl": "st",
    "customer_tbl": "ct",
    "product_tbl": "pt"
}

# -------------------------------------------------------
# PRODUCTION ALIAS MAP
# -------------------------------------------------------

TEST_PRODUCTION_ALIAS_MAP = {

    "prod_tbl": "pt",
    "prod_desc": "pd"
}
#----------------------------------------------------------
TEST_TAGS = {

    "REPORT": "report",
    "RAW": "raw",

    "JOIN": "join",
    "GROUP_BY": "group-by",
    "HAVING": "having",

    "DISPLAY_COLUMN": "display-column",

    "SALES": "sales",
    "PRODUCTION": "production"
}


#-------------------------------------------------------
TEST_TAGS = {

    "QUERY_TYPES": [
        "raw",
        "report",
        "kpi",
        "ranking"
    ],

    "FEATURES": [
        "aggregation",
        "join",
        "group-by",
        "having",
        "order-by",
        "limit",
        "time-filter"
    ],

    "SEMANTICS": [
        "display-column",
        "semantic-target",
        "relationship",
        "domain-detection"
    ],

    "DOMAINS": [
        "sales",
        "production",
        "inventory"
    ]
}