from typing import Any, Dict, Optional
from pydantic import BaseModel, AnyUrl, EmailStr, Field


class QuizRequest(BaseModel):
    email: EmailStr
    secret: str
    url: AnyUrl

    # Accept arbitrary extra fields from the evaluator
    class Config:
        extra = "allow"


class QuizAcceptedResponse(BaseModel):
    status: str = "ok"
    detail: str = "accepted"


class ErrorResponse(BaseModel):
    status: str = "error"
    detail: str


class SolverResult(BaseModel):
    submit_url: AnyUrl
    answer: Any
    # Extra fields to include when submitting
    extra_payload: Dict[str, Any] = Field(default_factory=dict)
    # Whether this quiz chain is complete
    done: bool = False
