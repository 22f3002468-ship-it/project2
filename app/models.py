# app/models.py
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, HttpUrl, Field


class QuizRequest(BaseModel):
    email: str = Field(..., description="Student email ID")
    secret: str = Field(..., description="Student-provided secret")
    url: HttpUrl = Field(..., description="Quiz URL")


class QuizAck(BaseModel):
    status: str = "ok"
    message: str
    started_at: datetime
    deadline: datetime


class SubmitResult(BaseModel):
    correct: bool
    url: Optional[HttpUrl] = None
    reason: Optional[str] = None
    raw_response: Optional[Any] = None


class SolverAnswer(BaseModel):
    answer: Any
    answer_type: str  # "number" | "string" | "bool" | "object" | "file_base64"
