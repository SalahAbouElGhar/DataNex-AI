import pytest

import ai.ai_engine as ai_engine
from core.result import ResultStatus, StructuredResult


def test_query_plan_failure_stops_pipeline(monkeypatch):
    session = {
        "history": [],
        "user_schema": None,
    }

    monkeypatch.setattr(
        ai_engine,
        "get_session",
        lambda session_id: session,
    )

    monkeypatch.setattr(
        ai_engine,
        "validate_prompt",
        lambda prompt: None,
    )

    monkeypatch.setattr(
        ai_engine,
        "save_user_schema",
        lambda session, prompt: False,
    )

    monkeypatch.setattr(
        ai_engine,
        "get_active_schema",
        lambda session, prompt: "test schema",
    )

    def fail_query_plan(session, prompt):
        raise RuntimeError("Simulated query planning failure")

    monkeypatch.setattr(
        ai_engine,
        "create_query_plan",
        fail_query_plan,
    )

    def unexpected_build_ast(*args, **kwargs):
        pytest.fail("build_ast must not run after query plan failure")

    def unexpected_compile_sql(*args, **kwargs):
        pytest.fail("compile_sql_ast must not run after query plan failure")

    monkeypatch.setattr(
        ai_engine,
        "build_ast",
        unexpected_build_ast,
    )

    monkeypatch.setattr(
        ai_engine,
        "compile_sql_ast",
        unexpected_compile_sql,
    )

    result = ai_engine.ask_ai(
        "total production by factory",
        "test-failure-session",
    )

    assert isinstance(result, StructuredResult)
    assert result.status == ResultStatus.FAILURE
    assert result.stage == "query_planning"
    assert result.code == "QUERY_PLAN_BUILD_FAILED"
    assert result.data is None
# --------------------------------------------------------
def test_ast_failure_stops_sql_compilation(monkeypatch):
    session = {
        "history": [],
        "user_schema": None,
    }

    query_plan = {
        "alias_map": {},
    }

    monkeypatch.setattr(
        ai_engine,
        "get_session",
        lambda session_id: session,
    )

    monkeypatch.setattr(
        ai_engine,
        "validate_prompt",
        lambda prompt: None,
    )

    monkeypatch.setattr(
        ai_engine,
        "save_user_schema",
        lambda session, prompt: False,
    )

    monkeypatch.setattr(
        ai_engine,
        "get_active_schema",
        lambda session, prompt: "test schema",
    )

    monkeypatch.setattr(
        ai_engine,
        "create_query_plan",
        lambda session, prompt: (
            {"test_table": {}},
            query_plan,
        ),
    )

    monkeypatch.setattr(
        ai_engine,
        "validate_query_plan",
        lambda plan: {
            "valid": True,
            "errors": [],
            "warnings": [],
        },
    )

    def fail_build_ast(*args, **kwargs):
        raise RuntimeError("Simulated AST construction failure")

    def unexpected_compile(*args, **kwargs):
        pytest.fail(
            "SQL compilation must not run after AST failure"
        )

    monkeypatch.setattr(
        ai_engine,
        "build_ast",
        fail_build_ast,
    )

    monkeypatch.setattr(
        ai_engine,
        "compile_sql_ast",
        unexpected_compile,
    )

    result = ai_engine.ask_ai(
        "total production by factory",
        "test-ast-failure-session",
    )

    assert isinstance(result, StructuredResult)
    assert result.status == ResultStatus.FAILURE
    assert result.stage == "ast_construction"
    assert result.code == "AST_BUILD_FAILED"
    assert result.data is None
# ---------------------------------------------
def test_sql_compilation_failure_returns_failure(monkeypatch):
    session = {
        "history": [],
        "user_schema": None,
    }

    query_plan = {
        "alias_map": {},
    }

    monkeypatch.setattr(
        ai_engine,
        "get_session",
        lambda session_id: session,
    )

    monkeypatch.setattr(
        ai_engine,
        "validate_prompt",
        lambda prompt: None,
    )

    monkeypatch.setattr(
        ai_engine,
        "save_user_schema",
        lambda session, prompt: False,
    )

    monkeypatch.setattr(
        ai_engine,
        "get_active_schema",
        lambda session, prompt: "test schema",
    )

    monkeypatch.setattr(
        ai_engine,
        "create_query_plan",
        lambda session, prompt: (
            {"test_table": {}},
            query_plan,
        ),
    )

    monkeypatch.setattr(
        ai_engine,
        "validate_query_plan",
        lambda plan: {
            "valid": True,
            "errors": [],
            "warnings": [],
        },
    )

    monkeypatch.setattr(
        ai_engine,
        "build_ast",
        lambda plan: {"type": "SELECT"},
    )

    def fail_compile(*args, **kwargs):
        raise RuntimeError("Simulated SQL compilation failure")

    monkeypatch.setattr(
        ai_engine,
        "compile_sql_ast",
        fail_compile,
    )

    result = ai_engine.ask_ai(
        "total production by factory",
        "test-sql-compilation-failure-session",
    )

    assert isinstance(result, StructuredResult)
    assert result.status == ResultStatus.FAILURE
    assert result.stage == "sql_compilation"
    assert result.code == "SQL_COMPILATION_FAILED"
    assert result.data is None
# ------------------------------------------------
def test_successful_pipeline_returns_sql(monkeypatch):
    session = {
        "history": [],
        "user_schema": None,
    }

    query_plan = {
        "alias_map": {},
    }

    # SQL الخام الناتج عن Compiler، قبل التحويل
    raw_sql = (
        "select factory_id from prod_tbl "
        "FETCH FIRST 5 ROWS ONLY"
    )

    # SQL المتوقع بعد تحويله إلى صيغة Informix
    expected_sql = "select FIRST 5 factory_id from prod_tbl"

    # سنسجل SQL الذي وصل فعلًا إلى مرحلة التحقق
    validated_sql = []

    # نحتفظ بالدالة الأصلية لتنفيذ التحقق الحقيقي
    original_validate_sql = ai_engine.validate_sql

    # تسجيل SQL قبل تمريره إلى المدقق الأصلي
    def capture_and_validate(sql, plan):
        validated_sql.append(sql)
        return original_validate_sql(sql, plan)

    # --------------------------------------------
    # إعداد المراحل السابقة
    # --------------------------------------------
    monkeypatch.setattr(
        ai_engine,
        "get_session",
        lambda session_id: session,
    )

    monkeypatch.setattr(
        ai_engine,
        "validate_prompt",
        lambda prompt: None,
    )

    monkeypatch.setattr(
        ai_engine,
        "save_user_schema",
        lambda session, prompt: False,
    )

    monkeypatch.setattr(
        ai_engine,
        "get_active_schema",
        lambda session, prompt: "test schema",
    )

    monkeypatch.setattr(
        ai_engine,
        "create_query_plan",
        lambda session, prompt: (
            {"test_table": {}},
            query_plan,
        ),
    )

    monkeypatch.setattr(
        ai_engine,
        "validate_query_plan",
        lambda plan: {
            "valid": True,
            "errors": [],
            "warnings": [],
        },
    )

    # --------------------------------------------
    # محاكاة بناء AST وتجميع SQL الخام
    # --------------------------------------------
    monkeypatch.setattr(
        ai_engine,
        "build_ast",
        lambda plan: {"type": "SELECT"},
    )

    monkeypatch.setattr(
        ai_engine,
        "compile_sql_ast",
        lambda ast, schema, alias_map: raw_sql,
    )

    # --------------------------------------------
    # تسجيل SQL الذي يصل إلى المدقق
    # --------------------------------------------
    monkeypatch.setattr(
        ai_engine,
        "validate_sql",
        capture_and_validate,
    )

    # --------------------------------------------
    # تنفيذ خط المعالجة
    # --------------------------------------------
    result = ai_engine.ask_ai(
        "total production by factory",
        "test-success-session",
    )

    # --------------------------------------------
    # التحقق من النتيجة النهائية
    # --------------------------------------------
    assert isinstance(result, StructuredResult)
    assert result.status == ResultStatus.SUCCESS
    assert result.stage == "sql_validation"
    assert result.code == "SQL_COMPILED"
    assert result.data == {"sql": expected_sql}

    # التأكد من أن SQL الذي تم التحقق منه
    # هو نفسه SQL الذي أعادته ask_ai()
    assert validated_sql == [expected_sql]

# ------------------------------------------------
def test_sql_validation_failure_returns_failure(monkeypatch):
    session = {
        "history": [],
        "user_schema": None,
    }

    query_plan = {
        "alias_map": {},
    }

    monkeypatch.setattr(
        ai_engine,
        "get_session",
        lambda session_id: session,
    )
    monkeypatch.setattr(
        ai_engine,
        "validate_prompt",
        lambda prompt: None,
    )
    monkeypatch.setattr(
        ai_engine,
        "save_user_schema",
        lambda session, prompt: False,
    )
    monkeypatch.setattr(
        ai_engine,
        "get_active_schema",
        lambda session, prompt: "test schema",
    )
    monkeypatch.setattr(
        ai_engine,
        "create_query_plan",
        lambda session, prompt: (
            {"test_table": {}},
            query_plan,
        ),
    )
    monkeypatch.setattr(
        ai_engine,
        "validate_query_plan",
        lambda plan: {
            "valid": True,
            "errors": [],
            "warnings": [],
        },
    )
    monkeypatch.setattr(
        ai_engine,
        "build_ast",
        lambda plan: {"type": "SELECT"},
    )
    monkeypatch.setattr(
        ai_engine,
        "compile_sql_ast",
        lambda ast, schema, alias_map: (
            "SELECT factory_id FROM prod_tbl"
        ),
    )

    def fail_validation(sql, plan):
        raise ValueError("Simulated SQL validation failure")

    monkeypatch.setattr(
        ai_engine,
        "validate_sql",
        fail_validation,
    )

    result = ai_engine.ask_ai(
        "total production by factory",
        "test-sql-validation-session",
    )

    assert isinstance(result, StructuredResult)
    assert result.status == ResultStatus.FAILURE
    assert result.stage == "sql_validation"
    assert result.code == "SQL_VALIDATION_FAILED"
    assert result.data is None
