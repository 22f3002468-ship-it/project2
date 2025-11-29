from __future__ import annotations

from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from .config import settings
from .models import QuizRequest, QuizAcceptedResponse, ErrorResponse
from .quiz_handler import process_quiz_chain
from .utils import logger


app = FastAPI(title=settings.app_name)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Convert invalid body/JSON into 400 (spec wants 400, not 422).
    """
    logger.warning("Invalid JSON or body: %s", exc)
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            status="error",
            detail="Invalid JSON payload or missing required fields.",
        ).model_dump(),
    )


@app.get("/health", response_class=JSONResponse)
async def health():
    return {"status": "ok"}


@app.post("/", response_model=QuizAcceptedResponse)
async def root_quiz_endpoint(
    payload: QuizRequest,
    background_tasks: BackgroundTasks,
):
    """
    Entry point hit by the evaluator.

    1) Validate secret, return:
       - 403 for invalid secret
       - 200 JSON for valid secret
    2) Start background task to handle the quiz chain.
    """
    logger.info("Received quiz POST: email=%s url=%s", payload.email, payload.url)

    # Secret verification
    if payload.secret != settings.secret:
        logger.warning("Invalid secret for email=%s", payload.email)
        raise HTTPException(
            status_code=403,
            detail="Invalid secret.",
        )

    # Start async processing in background
    background_tasks.add_task(process_quiz_chain, payload)

    # Immediate 200 JSON response
    return QuizAcceptedResponse(
        status="ok",
        detail="Request accepted. Quiz processing started.",
    )
