from fastapi.testclient import TestClient
import pytest
import api.routes as routes
from main import app
from core.result import ResultStatus, StructuredResult
# ----------------------------------------------------

client = TestClient(app)
# ----------------------------------------------------

def test_ask_returns_sql_on_success(monkeypatch):
    expected_sql = (
        "SELECT pt.factory_id, SUM(pt.qty) AS total_qty "
        "FROM prod_tbl pt GROUP BY pt.factory_id"
    )

    monkeypatch.setattr(
        routes,
        "ask_ai",
        lambda prompt, session_id: StructuredResult(
            status=ResultStatus.SUCCESS,
            stage="sql_compilation",
            code="SQL_COMPILED",
            data={"sql": expected_sql},
        ),
    )

    response = client.post(
        "/ask",
        json={
            "question": "total production by factory",
            "session_id": "api-success-test",
        },
    )

    assert response.status_code == 200
    assert response.json()["response"].startswith("SELECT")
# ----------------------------------------------------

def test_ask_returns_safe_error_on_failure(monkeypatch):
    safe_message = (
        "تعذّر إكمال طلبك حاليًا. "
        "يرجى المحاولة مرة أخرى."
    )

    monkeypatch.setattr(
        routes,
        "ask_ai",
        lambda prompt, session_id: StructuredResult(
            status=ResultStatus.FAILURE,
            stage="query_planning",
            code="QUERY_PLAN_BUILD_FAILED",
            message=safe_message,
        ),
    )

    response = client.post(
        "/ask",
        json={
            "question": "total production by factory",
            "session_id": "api-failure-test",
        },
    )

    assert response.status_code == 500
    assert response.json()["detail"] == safe_message
    assert "Simulated" not in response.text
# ----------------------------------------------------
@pytest.mark.parametrize(
    ("status", "code", "message"),
    [
        (
            ResultStatus.NEEDS_INPUT,
            "SCHEMA_REQUIRED",
            "يرجى تزويدنا باسم الجدول وأسماء الأعمدة المطلوبة.",
        ),
        (
            ResultStatus.AMBIGUOUS,
            "REQUEST_AMBIGUOUS",
            "يرجى توضيح المقصود من الطلب.",
        ),
        (
            ResultStatus.NO_RESULT,
            "NO_RESULT",
            "لم يتم العثور على نتيجة قابلة للاستخدام.",
        ),
    ],
)
# ----------------------------------------------------
def test_ask_returns_message_for_nonfailure_statuses(
    monkeypatch,
    status,
    code,
    message,
):
    monkeypatch.setattr(
        routes,
        "ask_ai",
        lambda prompt, session_id: StructuredResult(
            status=status,
            stage="business_reasoning",
            code=code,
            message=message,
        ),
    )

    response = client.post(
        "/ask",
        json={
            "question": "show me the report",
            "session_id": f"api-{code.lower()}-test",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"response": message}
# ----------------------------------------------------
def test_ask_stream_returns_sql_on_success(monkeypatch):
    expected_sql = (
        "SELECT pt.factory_id, "
        "SUM(pt.qty) AS total_qty "
        "FROM prod_tbl pt "
        "GROUP BY pt.factory_id"
    )

    monkeypatch.setattr(
        routes,
        "ask_ai",
        lambda prompt, session_id: StructuredResult(
            status=ResultStatus.SUCCESS,
            stage="sql_compilation",
            code="SQL_COMPILED",
            data={"sql": expected_sql},
        ),
    )

    response = client.post(
        "/ask-stream",
        json={
            "question": "total production by factory",
            "session_id": "stream-success-test",
        },
    )

    assert response.status_code == 200
    assert "SELECT" in response.text
    assert "SUM(pt.qty)" in response.text
# -------------------------------------------------------
def test_ask_stream_returns_safe_error_on_failure(monkeypatch):
    safe_message = (
        "تعذّر إكمال طلبك حاليًا. "
        "يرجى المحاولة مرة أخرى."
    )

    monkeypatch.setattr(
        routes,
        "ask_ai",
        lambda prompt, session_id: StructuredResult(
            status=ResultStatus.FAILURE,
            stage="query_planning",
            code="QUERY_PLAN_BUILD_FAILED",
            message=safe_message,
        ),
    )

    response = client.post(
        "/ask-stream",
        json={
            "question": "total production by factory",
            "session_id": "stream-failure-test",
        },
    )

    assert response.status_code == 500
    assert response.text == safe_message
    assert "[ERROR]:" not in response.text