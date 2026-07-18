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
    
#-------------------------------------------------
# NATURAL LANGUAGE
#-------------------------------------------------

# Legacy
# No longer used.
# Safe to remove after verification.

#DOMAIN_KEYWORDS = {
#     "employees": [
#        "employee",
#        "employees",
#        "staff",
#        "worker"
#    ],
#
#    "sales": [
#        "sales",
#        "sale",
#        "revenue",
#        "income"
#    ],
#
#    "production": [
#        "production",
#        "produce",
#        "factory",
#        "manufacturing",
#        "product"
#    ]
#}
#
#-------------------------------------------------
# Legacy
# Deprecated after Domain migration.
BUSINESS_TERMS = {

    "factory": [
        "factory",
        "factories",
        "fact",
        "fac"
    ],

    "product": [
        "product",
        "products",
        "prod",
        "item"
    ],

    "customer": [
        "customer",
        "customers",
        "cust",
        "client"
    ]
}
#---------------------------------------------------
# Legacy
#BUSINESS_TABLES = {
#
#    "factory": [
#        "prod_tbl"
#    ],
#
#    "product": [
#        "product_tbl",
#        "prod_desc",
#        "prod_tbl"
#    ],
#
#    "customer": [
#        "customer_tbl",
#        "sales_tbl"
#    ],
#    "supplier": [
#        "supplier_tbl",
#        "purchase_tbl"
#    ],
#
#    "employee": [
#        "employee_tbl",
#        "payroll_tbl"
#    ]
#}
#------------------------------------------------
# Legacy
# Deprecated after Domain entity migration.
#BUSINESS_KEYWORDS = {
#    "production": ["prod_tbl"],
#    "production data": ["prod_tbl"],
#    "product name": ["prod_desc"],
#    "products": ["prod_tbl"]
#}
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
#Legacy
#Unused
#Ready for Removal
#
#DEFAULT_REPORT_DIMENSIONS = {
#    "production": ["factory_id"],
#    "sales": ["customer_id"],
#    "inventory": ["item_id"]
#}    
#---------------------------------------------------
DOMAINS = {

    "sales": {

        "keywords": [
            "sales",
            "sale",
            "revenue",
            "income"
        ],

        "tables": [
            "sales_tbl",
            "customer_tbl",
            "product_tbl"
        ],

        "default_dimensions": [
            "cust_no"
        ],

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
        "demo_schema": "sales_demo"
    },

    "production": {

        "keywords": [
            "production",
            "produce",
            "factory",
            "manufacturing",
            "product"
        ],

        "tables": [
            "prod_tbl",
            "prod_desc"
        ],

        "default_dimensions": [
            "factory_id"
        ],

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
