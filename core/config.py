import os
from dotenv import load_dotenv
#-------------------------------------------------
# ENVIRONMENT
#-------------------------------------------------
load_dotenv()

#-------------------------------------------------
# AI SETTINGS
#-------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("GROQ_MODEL_NAME")
MAX_HISTORY = int(os.getenv("MAX_HISTORY", 10))

if not MODEL_NAME:
    raise ValueError("GROQ_MODEL_NAME is not set")


#------------------------------------------------
# SCHEMA ANALYSIS
#------------------------------------------------

MEASURE_KEYWORDS = [
    "qty",
    "amount",
    "total",
    "price",
    "sales",
    "revenue",
    "cost",
    "profit",
    "expense",
    "balance",
    "stock",
    "weight"
]
#--------------------------------------------------
DATE_COLUMN_KEYWORDS = [
    "date",
    "time",
    "created",
    "updated",
    "timestamp",
    "datetime"
]
#-----------------------------------------------------
DISPLAY_KEYWORDS = [
    "name",
    "names",
    "description",
    "desc"
]
#-----------------------------------------------------
DISPLAY_SUFFIXES = [
    "_name",
    "_desc",
    "_title",
    "_text",
    "_label"
]
#------------------------------------------------------
RELATIONSHIP_SUFFIXES = [

    "_id",
    "_num",
    "_no",
    "_code",
    "_cod"
]
#------------------------------------------------------
RELATIONSHIP_HINTS = {}

#------------------------------------------------------
# SQL
#------------------------------------------------------
AGGREGATION_KEYWORDS = {
    "SUM": ["total" , "sum" ],
    "AVG": ["average" , "avg"],
    "MAX": ["maximum" , "max" , "highest" ],
    "MIN": [ "minimum" , "min" ,"lowest" ],
    "COUNT": ["count" ,"number of" , "how many" ]
}
#------------------------------------------------------
LIMIT_PATTERNS = {
    "top_n": r"top\s+(\d+)",
    "latest_n": r"latest\s+(\d+)",
    "bottom_n": r"bottom\s+(\d+)",
    "first_n": r"first\s+(\d+)"
}
#------------------------------------------------------
BUSINESS_TERMS = {
    "factory": ["factory", "factories", "fact", "fac"],
    "product": ["product", "products", "prod", "item"],
    "customer": ["customer", "customers", "cust", "client"]
}
# ======================================================
# BUSINESS KNOWLEDGE BASE
#
# Each business domain represents one business capability.
#
# Every domain should define:
#
# - keywords
#       Natural language terms used for domain detection.
#
# - entities
#       Business entities mapped to related tables.
#
# - display_entities
#       Business entities mapped to display columns.
#
# - tables
#       Database tables that belong to this domain.
#
# - default_measure
#       Default numeric measure used for aggregation.
#
# - default_date_column
#       Default date column used for time filtering.
#
# - default_dimensions
#       Default grouping dimensions for reports.
#
# - demo_schema
#       Default demo schema for this domain.
#
# ======================================================
DOMAINS = {

    "sales": {

        # -------------------------
        # DOMAIN DETECTION
        # -------------------------

        "keywords": [
            "sales",
            "sale",
            "revenue",
            "income"
        ],

        # -------------------------
        # BUSINESS KNOWLEDGE
        # -------------------------

        "entities": {

            "sales": [
                "sales_tbl"
            ],

            "customer": [
                "customer_tbl",
                "sales_tbl"
            ],

            "product": [
                "product_tbl",
                "sales_tbl"
            ]
        },

        "semantic_entities": {

            "customer": "cust_no",
            "product": "prod_id"
        },

        "display_entities": {

            "customer": "cust_name",
            "product": "prod_name"
        },

        # -------------------------
        # MEASURE KNOWLEDGE
        # -------------------------

        # Internal business measure
        # mapped directly to database column.

        "measures": {

            "sales": "sales_amt"
        },

        # User language / business vocabulary.
        # Different expressions can refer
        # to the same business measure.

        "measure_synonyms": {

            "sales": [
                "sales",
                "revenue",
                "income"
            ]
        },

        # -------------------------
        # DATABASE
        # -------------------------

        "tables": [

            "sales_tbl",
            "customer_tbl",
            "product_tbl"
        ],

        # -------------------------
        # REPORTING
        # -------------------------

        "default_measure": "sales",

        "default_date_column": "sale_date",

        "default_dimensions": [

            "customer"
        ],

        # -------------------------
        # DEMO
        # -------------------------

        "demo_schema": "sales_demo"
    },


    "production": {

        # -------------------------
        # DOMAIN DETECTION
        # -------------------------

        "keywords": [
            "production",
            "produce",
            "manufacturing"
        ],

        # -------------------------
        # BUSINESS KNOWLEDGE
        # -------------------------

        "entities": {

            "production": [
                "prod_tbl"
            ],

            "factory": [
                "prod_tbl"
            ],

            "product": [
                "prod_desc",
                "prod_tbl"
            ]
        },

        "semantic_entities": {

            "factory": "factory_id",
            "product": "prod_id"
        },

        "display_entities": {

            "product": "prod_name"
        },

        # -------------------------
        # MEASURE KNOWLEDGE
        # -------------------------

        # Internal business measure
        # mapped directly to database column.

        "measures": {

            "production": "qty"
        },

        # User language / business vocabulary.

        "measure_synonyms": {

            "production": [
                "production",
                "produce",
                "manufacturing",
                "output",
                "quantity",
                "qty"
            ]
        },

        # -------------------------
        # DATABASE
        # -------------------------

        "tables": [

            "prod_tbl",
            "prod_desc"
        ],

        # -------------------------
        # REPORTING
        # -------------------------

        "default_measure": "production",

        "default_date_column": "prod_date",

        "default_dimensions": [

            "factory"
        ],

        # -------------------------
        # DEMO
        # -------------------------

        "demo_schema": "production_demo"
    }
}
#---------------------------------------------------
# DEMO SCHEMAS
#---------------------------------------------------

DEMO_SCHEMAS = {

    "sales_demo": {
    "description":"Demo schema for sales reporting",
    "schema": """
table sales_tbl
columns
sale_no
cust_no
prod_id
sales_amount
sale_date

table customer_tbl
columns
cust_no
cust_name

table product_tbl
columns
prod_id
prod_name
"""
    },

    "production_demo": {
    "description":"Demo schema for production reporting",
    "schema": """
table prod_tbl
columns
factory_id
prod_id
prod_date
qty

table prod_desc
columns
prod_id
prod_name
"""
    }

}

DEFAULT_DEMO_SCHEMA = "sales_demo"

ENABLE_DEMO_SCHEMA_FALLBACK = True
#-----------------------------------------------------------
