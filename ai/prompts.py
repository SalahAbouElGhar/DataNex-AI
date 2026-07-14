from core.config import (
    DOMAIN_KEYWORDS
)
"""
Legacy / Future Hybrid AI Prompt Layer

Currently DataNex uses:

Prompt
→ Query Plan
→ AST
→ SQL Compiler

This module may be reused later for:
- Complex reasoning
- Ambiguous requests
- Hybrid AI mode
"""
# =========================
# SYSTEM PROMPT
# =========================
system_prompt = {
    "role": "system",
    "content": """
You are DataNex AI, an expert IBM Informix SQL assistant.

STRICT RULES:
- Return ONLY SQL
- No explanations
- No markdown
- No comments
- Always return complete SQL
- Never truncate output

INFORMIX RULES:
- Use IBM Informix syntax only
- Use TODAY for current date
- Prefer YEAR(TODAY)
- Never mix SQL dialects

QUERY RULES:
- Only generate SELECT queries
- Never modify data
- Never use DROP, DELETE, UPDATE, INSERT

SCHEMA RULES:
- Use ONLY provided schema
- Do NOT invent tables
- Do NOT invent columns

OUTPUT:
Return one valid executable SQL query only.
"""
}
# =========================
# DATABASE SCHEMAS
# =========================
# Legacy demo definitions
# May be removed after Demo Schema migration
SCHEMAS = {
    "employees": """
employees(
    employee_number,
    name,
    date_of_birth
)
""",

    "sales": """
sales(
    sales_amount,
    sales_date
)
"""
}
#------------------------------------------------------------
#DOMAIN_KEYWORDS = {
#    "employees": [
#        "employee",
#        "employees",
#        "staff",
#        "worker"
#    ],
#
#    "sales": [
#        "sales",
#        "revenue",
#        "income"
#    ]
#}
#--------------------------------------------
GENERIC_MODE_RESPONSE = """
Schema information required.

Please provide:
- table name
- relevant column names
"""
#--------------------------------------------
def detect_domain(prompt):

    prompt = prompt.lower()

    for domain, keywords in DOMAIN_KEYWORDS.items():

        if any(word in prompt for word in keywords):
            return domain

    return "generic"
#-------------------------------------------------------------
#def build_schema_context(schema: dict, query_plan: dict):
#
#    return {
#        "role": "system",
#        "content": f"""
#        USER SCHEMA:
#        
#        Table: {schema.get('table')}
#        Columns: {", ".join(schema.get('columns', []))}
#        
#        QUERY PLAN:
#        {query_plan}
#        
#        STRICT RULES:
#        - Use ONLY provided schema
#        - Do NOT invent tables
#        - Do NOT invent columns
#        - Follow query plan strictly
#        """
#    }
def build_schema_context(schema,query_plan):

    tables = schema.get(
        "tables",
        {}
    )

    schema_text = ""

    for table_name, columns in tables.items():

        schema_text += (
            f"Table: {table_name}\n"
        )

        schema_text += (
            f"Columns: "
            f"{', '.join(columns)}\n\n"
        )

    return {
        "role": "system",
        "content": f"""
USER SCHEMA:

{schema_text}

QUERY PLAN:
{query_plan}

STRICT RULES:
- Use ONLY provided schema
- Do NOT invent tables
- Do NOT invent columns
- Follow query plan strictly
"""
    }
#------------------------------------------------------------
