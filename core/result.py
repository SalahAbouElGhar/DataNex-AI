from dataclasses import dataclass
from enum import Enum
from typing import Any


class ResultStatus(str, Enum):
    SUCCESS = "SUCCESS"
    NEEDS_INPUT = "NEEDS_INPUT"
    AMBIGUOUS = "AMBIGUOUS"
    NO_RESULT = "NO_RESULT"
    FAILURE = "FAILURE"


@dataclass
class StructuredResult:
    status: ResultStatus
    stage: str
    code: str
    message: str | None = None
    data: Any = None