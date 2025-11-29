# app/quiz_handler.py
from __future__ import annotations

from datetime import timedelta

from .config import get_settings
from .models import QuizRequest
from .solver import QuizSolver
from .utils import deadline_after_minutes, logger


async def process_quiz(request: QuizRequest, deadline) -> None:
    """
    Background task:
      - create solver
      - run quiz loop for up to 3 minutes from first POST
    """
    settings = get_settings()

    logger.info(
        "Starting quiz for email=%s url=%s deadline=%s",
        request.email,
        request.url,
        deadline,
    )

    solver = QuizSolver(settings=settings)
    await solver.run_quiz_loop(
        initial_url=str(request.url),
        email=request.email,
        secret=request.secret,
        deadline=deadline,
    )

    logger.info("Quiz processing finished for email=%s", request.email)
