import logging
from core.logger import logger
from reasoning.sql_reasoning import (
    build_query_plan ,
    parse_multi_table_schema
    )
from ai.prompts import (
    system_prompt,
    detect_domain
    )
from validators.validators import (
    validate_prompt,
    validate_query_plan,
    validate_sql,
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
from core.result import ResultStatus, StructuredResult
from core.messages import MESSAGES
from utils.sql_utils import clean_sql, fix_informix_sql
# -------------------------------------------------------
STAGE_FAILURES = {
    "query_planning": "QUERY_PLAN_BUILD_FAILED",
    "query_plan_validation": "QUERY_PLAN_VALIDATION_FAILED",
    "ast_construction": "AST_BUILD_FAILED",
    "sql_compilation": "SQL_COMPILATION_FAILED",
    "sql_validation": "SQL_VALIDATION_FAILED",
    "sql_normalization": "SQL_NORMALIZATION_FAILED",
}
# -------------------------------------------------------
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

    raw_schema = get_active_schema(session,prompt)

    schema = parse_multi_table_schema(raw_schema)

    query_plan = build_query_plan(
                    prompt,
                    schema
                )

    return schema, query_plan
# ---------------------------------------------------------
def ask_ai(prompt, session_id):

    logger.info("User Prompt: %s", prompt)

    stage = "session_setup"

    try:
        # -------------------
        # SESSION
        # -------------------
        session = get_session(session_id)

        add_user_message(session, prompt)

        # -------------------
        # PROMPT VALIDATION
        # -------------------
        stage = "prompt_validation"

        validation_error = validate_prompt(prompt)

        if validation_error:
            return StructuredResult(
                status=ResultStatus.NEEDS_INPUT,
                stage=stage,
                code="PROMPT_INVALID",
                message=MESSAGES["PROMPT_INVALID"],
            )

        # -------------------
        # SAVE SCHEMA
        # -------------------
        stage = "schema_processing"

        if save_user_schema(session, prompt):
            return StructuredResult(
                status=ResultStatus.SUCCESS,
                stage=stage,
                code="SCHEMA_RECEIVED",
                message=MESSAGES["SCHEMA_RECEIVED"],
                data={"schema_saved": True},
            )

        # -------------------
        # MUST HAVE SCHEMA
        # -------------------
        stage = "schema_check"

        raw_schema = get_active_schema(session, prompt)

        if not raw_schema:
            return StructuredResult(
                status=ResultStatus.NEEDS_INPUT,
                stage=stage,
                code="SCHEMA_REQUIRED",
                message=MESSAGES["SCHEMA_REQUIRED"],
            )

        # -------------------------
        # QUERY PLAN
        # -------------------------
        stage = "query_planning"

        schema, query_plan = create_query_plan(
            session,
            prompt,
        )

        # -------------------------
        # QUERY PLAN VALIDATION
        # -------------------------
        stage = "query_plan_validation"

        validation_result = validate_query_plan(query_plan)

        if not validation_result.get("valid", False):
            errors = validation_result.get("errors", [])

            logger.warning(
                "Query plan validation failed. Errors: %s",
                errors,
            )

            return StructuredResult(
                status=ResultStatus.FAILURE,
                stage=stage,
                code="QUERY_PLAN_INVALID",
                message=MESSAGES["QUERY_PLAN_INVALID"],
            )

        # -------------------------
        # AST CONSTRUCTION
        # -------------------------
        stage = "ast_construction"

        ast = build_ast(query_plan)
        alias_map = query_plan["alias_map"]

        # -------------------------
        # SQL COMPILATION
        # -------------------------
        stage = "sql_compilation"

        sql = compile_sql_ast(
            ast,
            schema,
            alias_map,
        )
        # -------------------------
        # SQL NORMALIZATION
        # -------------------------
        stage = "sql_normalization"

        sql = fix_informix_sql(sql)
        sql = clean_sql(sql)

        # -------------------------
        # SQL VALIDATION
        # -------------------------
        stage = "sql_validation"

        validate_sql(sql, query_plan)

        # -------------------------
        # SUCCESS
        # -------------------------
        return StructuredResult(
            status=ResultStatus.SUCCESS,
            stage=stage,
            code="SQL_COMPILED",
            data={"sql": sql},
        )

    except Exception:
        logger.exception(
            "DataNex processing failed at stage=%s",
            stage,
        )

        code = STAGE_FAILURES.get(
            stage,
            "INTERNAL_ERROR",
        )

        return StructuredResult(
            status=ResultStatus.FAILURE,
            stage=stage,
            code=code,
            message=MESSAGES.get(
                code,
                MESSAGES["INTERNAL_ERROR"],
            ),
        )
