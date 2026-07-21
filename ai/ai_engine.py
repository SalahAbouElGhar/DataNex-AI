
import logging
import pprint

from core.logger import logger

from compiler.sql_reasoning import (
    build_query_plan , 
    parse_multi_table_schema
    )

from ai.prompts import (
    system_prompt,
    detect_domain
    )
from validators.validators import (
    validate_prompt,
    validate_query_plan
    )
from compiler.query_ast import (
    build_ast
    )
from compiler.ast_compiler import (
    compile_sql_ast
    )
import traceback

from core.config import (
    DEMO_SCHEMAS,
    DEFAULT_DEMO_SCHEMA,
    ENABLE_DEMO_SCHEMA_FALLBACK,
    DOMAINS
)
#-------------------------------------------------------
sessions = {}
#-------------------------------------------------------
def get_session(session_id):

    if session_id not in sessions:

        sessions[session_id] = {
            "history": [],
            "user_schema": None
        }

    return sessions[session_id]
#-------------------------------------------------------

def select_demo_schema(prompt):

    domain = detect_domain(prompt)
    
#    print(" DOMAIN =", domain)
    
    if domain == "generic":
        return None

    return DOMAINS[domain]["demo_schema"]

#-------------------------------------------------------
def get_active_schema(session,prompt):
    
    if session.get("user_schema"):
        return session["user_schema"]
        
    demo_name = select_demo_schema(prompt)

    if demo_name:
        return DEMO_SCHEMAS[demo_name]["schema"]
    
    return None


#-----------------------------------------------------------
def add_user_message(session, prompt):

    session["history"].append({
        "role": "user",
        "content": prompt
    })

#----------------------------------------------------------------
def extract_schema_from_prompt(prompt: str):

    prompt_lower = prompt.lower()

    schema_keywords = [
        "table",
        "table name",
        "columns",
        "column",
        "fields"
    ]

    if any(word in prompt_lower for word in schema_keywords):
        
        return prompt

    return None
#------------------------------------------------------------
def save_user_schema(session, prompt):

    detected_schema = extract_schema_from_prompt(prompt)

    if detected_schema:

        session["user_schema"] = detected_schema
        
        session["history"] = []

        return True

    return False    
#---------------------------------------------------------
def create_query_plan(session, prompt):

#    raw_schema = session["user_schema"]
    
    raw_schema = get_active_schema(session,prompt)
    
    schema = parse_multi_table_schema(raw_schema)
    
    pprint.pprint(schema, sort_dicts=False)
    
    query_plan = build_query_plan(
                    prompt,
                    schema
                )
    print("\nFINAL QUERY PLAN :")
    pprint.pprint(query_plan, sort_dicts=False)
        
    return schema, query_plan
#---------------------------------------------------------
def ask_ai(prompt, session_id):

    logger.info(f"User Prompt: {prompt}")

    # -------------------
    # SESSION
    # -------------------
    session = get_session(session_id)
    
    chat_history = session["history"]

    # -------------------
    # HISTORY
    # -------------------
    add_user_message(session, prompt)

    # -------------------
    # VALIDATION
    # -------------------
    validation_error = validate_prompt(prompt)

    if validation_error:
        return validation_error

    # -------------------
    # SAVE SCHEMA
    # -------------------
    if save_user_schema(session, prompt):
        return "Schema received successfully."
        
    # -------------------
    # MUST HAVE SCHEMA
    # -------------------

    raw_schema = get_active_schema(session,prompt)

    if not raw_schema:
        return (
            "Schema information required.\n"
            "Please provide:\n"
            "- table name\n"
            "- relevant column names"
        )
    
    # -------------------------
    # QUERY PLAN
    # -------------------------
    try: 
        schema, query_plan = create_query_plan(
                                session,
                                prompt
                            )
    

        validation_result = validate_query_plan(query_plan)
        
        if not validation_result["valid"]:
        
            raise Exception(
                "\n".join(
                    validation_result["errors"]
                )
            )
    except Exception as e:
        traceback.print_exc()
    #----------------------------------
    # AST COMPILER
    #----------------------------------
    try:
        ast = build_ast(query_plan)
        alias_map = query_plan["alias_map"]
        
    except Exception as e:
        traceback.print_exc()
    
    try:
        sql = compile_sql_ast(
            ast,
            schema,
            alias_map
        )
        return sql
    
#    except Exception as e:
#        logger.error(str(e))
    except Exception as e:
        traceback.print_exc()
    
##------------------------------------------------------------
