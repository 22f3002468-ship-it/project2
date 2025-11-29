from __future__ import annotations

import time
from typing import Dict, Any, Optional

import httpx

from .browser import render_page_html
from .config import settings
from .models import QuizRequest
from .solver import solve_quiz_from_html
from .utils import logger, time_limit


async def process_quiz_chain(initial_payload: QuizRequest) -> None:
    """
    Runs in background.

    1. Takes initial URL from evaluator.
    2. Loops: fetch page, solve with LLM, submit, follow next URL (if any).
    3. Stops when quiz ends, depth limit hit, or time limit exceeded.
    """
    logger.info("Starting quiz chain for email=%s url=%s",
                initial_payload.email, initial_payload.url)

    deadline = time.monotonic() + 170  # ~170s ~ <3 minutes margin
    current_url: Optional[str] = str(initial_payload.url)
    depth = 0

    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
        while current_url and depth < settings.max_quiz_depth:
            depth += 1

            if time.monotonic() > deadline:
                logger.warning("Time budget exceeded, stopping chain.")
                break

            logger.info("Depth %d, fetching quiz page: %s", depth, current_url)

            with time_limit(settings.request_timeout_seconds):
                html = render_page_html(current_url)

            # LLM: understand question, submit URL, and payload
            result = solve_quiz_from_html(
                html=html,
                quiz_url=current_url,
                email=str(initial_payload.email),
                secret=initial_payload.secret,
            )

            # Build submission payload
            submit_payload: Dict[str, Any] = {
                "email": str(initial_payload.email),
                "secret": initial_payload.secret,
                "url": current_url,
                "answer": result.answer,
            }

            # Merge any extra keys specified by LLM (may overwrite)
            submit_payload.update(result.extra_payload or {})

            logger.info("Submitting answer to %s (depth=%d)", result.submit_url, depth)
            logger.debug("Submit payload: %s", submit_payload)

            try:
                resp = await client.post(
                    str(result.submit_url),
                    json=submit_payload,
                )
            except Exception as e:
                logger.exception("Error submitting answer: %s", e)
                break

            logger.info("Submit status=%d", resp.status_code)

            # If not HTTP 200, probably stop
            if resp.status_code != 200:
                logger.warning("Non-200 response from submit endpoint: %s", resp.text)
                break

            # Interpret response JSON: look for 'correct' and 'url'
            try:
                data = resp.json()
            except Exception:
                logger.warning("Submit response is not JSON: %s", resp.text)
                break

            correct = data.get("correct")
            next_url = data.get("url")

            logger.info("Quiz result: correct=%s, next_url=%s", correct, next_url)

            if not next_url:
                logger.info("No next URL provided. Ending quiz chain.")
                break

            current_url = next_url

    logger.info("Quiz chain finished for email=%s", initial_payload.email)
