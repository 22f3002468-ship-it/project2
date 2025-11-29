# app/main.py
from __future__ import annotations

import logging
from datetime import datetime

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .config import get_settings
from .models import QuizAck, QuizRequest
from .quiz_handler import process_quiz
from .utils import utc_now, logger

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


app = FastAPI(title=settings.app_name)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Spec: HTTP 400 for invalid JSON
    return JSONResponse(
        status_code=400,
        content={"detail": "Invalid request JSON", "errors": exc.errors()},
    )


@app.get("/health")
async def health_check():
    return {"status": "ok", "time": utc_now().isoformat()}


@app.post("/")
async def handle_quiz(request_body: QuizRequest, background_tasks: BackgroundTasks):
    """
    Main endpoint:

    - Verify secret (and optionally email).
    - If invalid JSON => handled by validation_exception_handler (400).
    - If invalid secret => 403.
    - On success:
        * immediately return 200 with small JSON
        * start background task to solve the quiz.
    """
    # Verify secret
    if request_body.secret != settings.secret:
        raise HTTPException(status_code=403, detail="Invalid secret")

    # Optionally, also verify email matches (not required by spec, but okay to be strict)
    # if request_body.email != settings.email:
    #     raise HTTPException(status_code=403, detail="Invalid email")

    started_at = utc_now()
    # 3 minutes from _this_ POST reaching your server
    from .utils import deadline_after_minutes
    deadline = deadline_after_minutes(3)

    background_tasks.add_task(process_quiz, request_body, deadline)

    ack = QuizAck(
        message="Quiz processing started.",
        started_at=started_at,
        deadline=deadline,
    )
    return ack
