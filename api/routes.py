from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from models.schemas import Question
from core.security import detect_injection
from ai.ai_engine import ask_ai, sessions#, system_prompt
from fastapi.responses import HTMLResponse, StreamingResponse

from core.logger import logger
from core.messages import MESSAGES
from core.result import ResultStatus


# ------------------------------------------------

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
templates = Jinja2Templates(directory="templates")

# ------------------------------------------------

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )
# ------------------------------------------------
def get_result_sql(result):
    if not isinstance(result.data, dict):
        return None

    sql = result.data.get("sql")

    if not isinstance(sql, str) or not sql.strip():
        return None

    return sql

# ------------------------------------------------
#  -------- ASK --------
@router.post("/ask")
@limiter.limit("5/minute")
def ask(request: Request, q: Question):

    prompt = q.question.strip()

    if not prompt:
        raise HTTPException(status_code=400, detail="Empty prompt")

    # حماية ضد prompt injection
    if detect_injection(prompt):
        raise HTTPException(
            status_code=400,
            detail="Potential prompt injection detected"
        )

    if "total" in prompt.lower():
        prompt = f"Calculate total using SUM(): {prompt}"

    elif "average" in prompt.lower():
        prompt = f"Calculate average using AVG(): {prompt}"

    elif "count" in prompt.lower():
        prompt = f"Count rows using COUNT(): {prompt}"

    result = ask_ai(prompt, q.session_id)

    # -------------------------
    # SUCCESS WITHOUT SQL
    # -------------------------
    if (
        result.status == ResultStatus.SUCCESS
        and result.code == "SCHEMA_RECEIVED"
    ):
        return {
            "response": result.message
        }

    # -------------------------
    # SUCCESS WITH SQL
    # -------------------------
    if result.status == ResultStatus.SUCCESS:
        sql = get_result_sql(result)

        if not sql:
            logger.error(
                "Successful result has no SQL. Stage=%s Code=%s",
                result.stage,
                result.code,
            )

            raise HTTPException(
                status_code=500,
                detail=MESSAGES["INTERNAL_ERROR"],
            )

        try:

            response = sql

        except Exception:
            logger.exception("SQL response formatting failed")

            raise HTTPException(
                status_code=500,
                detail=MESSAGES["INTERNAL_ERROR"],
            )

        return {
            "response": response
        }

    # -------------------------
    # USER INPUT / AMBIGUITY
    # -------------------------
    if result.status in {
        ResultStatus.NEEDS_INPUT,
        ResultStatus.AMBIGUOUS,
        ResultStatus.NO_RESULT,
    }:
        message = result.message or MESSAGES.get(
            result.code,
            MESSAGES["NO_RESULT"],
        )

        return {
            "response": message
        }

    # -------------------------
    # SYSTEM FAILURE
    # -------------------------
    logger.error(
        "Request failed. Stage=%s Code=%s",
        result.stage,
        result.code,
    )

    raise HTTPException(
        status_code=500,
        detail=result.message or MESSAGES["INTERNAL_ERROR"],
    )

# -------- STREAM --------
@router.post("/ask-stream")
@limiter.limit("5/minute")
def ask_stream(q: Question, request: Request):

    prompt = q.question.strip()

    if not prompt:
        raise HTTPException(
            status_code=400,
            detail="Empty prompt",
        )

    if detect_injection(prompt):
        raise HTTPException(
            status_code=400,
            detail="Potential prompt injection detected",
        )

    # Keep the same prompt preparation used by /ask.
    if "total" in prompt.lower():
        prompt = f"Calculate total using SUM(): {prompt}"

    elif "average" in prompt.lower():
        prompt = f"Calculate average using AVG(): {prompt}"

    elif "count" in prompt.lower():
        prompt = f"Count rows using COUNT(): {prompt}"


    try:
        result = ask_ai(prompt, q.session_id)

    except Exception:
        logger.exception("Unexpected failure in /ask-stream")

        return StreamingResponse(
            iter([MESSAGES["INTERNAL_ERROR"]]),
            status_code=500,
            media_type="text/plain",
        )

    # -------------------------
    # SUCCESS
    # -------------------------
    if result.status == ResultStatus.SUCCESS:

        # Schema was saved; no SQL is expected.
        if result.code == "SCHEMA_RECEIVED":
            response_text = (
                result.message
                or MESSAGES["SCHEMA_RECEIVED"]
            )

        else:
            sql = get_result_sql(result)

            if not sql:
                logger.error(
                    "Successful stream result contains no SQL. "
                    "Stage=%s Code=%s",
                    result.stage,
                    result.code,
                )

                return StreamingResponse(
                    iter([MESSAGES["INTERNAL_ERROR"]]),
                    status_code=500,
                    media_type="text/plain",
                )

            try:

                response_text = sql

            except Exception:
                logger.exception(
                    "Failed to format SQL in /ask-stream"
                )

                return StreamingResponse(
                    iter([MESSAGES["INTERNAL_ERROR"]]),
                    status_code=500,
                    media_type="text/plain",
                )

        return StreamingResponse(
            iter([response_text]),
            media_type="text/plain",
        )

    # -------------------------
    # NON-FAILURE RESULTS
    # -------------------------
    if result.status in {
        ResultStatus.NEEDS_INPUT,
        ResultStatus.AMBIGUOUS,
        ResultStatus.NO_RESULT,
    }:
        response_text = (
            result.message
            or MESSAGES.get(
                result.code,
                MESSAGES["INTERNAL_ERROR"],
            )
        )

        return StreamingResponse(
            iter([response_text]),
            media_type="text/plain",
        )

    # -------------------------
    # FAILURE
    # -------------------------
    logger.error(
        "Request failed in /ask-stream. "
        "Stage=%s Code=%s",
        result.stage,
        result.code,
    )

    return StreamingResponse(
        iter([
            result.message
            or MESSAGES["INTERNAL_ERROR"]
        ]),
        status_code=500,
        media_type="text/plain",
    )
# -------- CLEAR --------
@router.post("/clear")
def clear(q: Question):
#    sessions[q.session_id] = [system_prompt]

    sessions[q.session_id] = {
        "history": [],
        "user_schema": None,
    }
    return {"status": "cleared"}