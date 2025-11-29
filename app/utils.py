# app/utils.py
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from typing import AsyncIterator

logger = logging.getLogger("llm-quiz")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def deadline_after_minutes(minutes: int) -> datetime:
    return utc_now() + timedelta(minutes=minutes)


def within_deadline(deadline: datetime) -> bool:
    return utc_now() < deadline


@asynccontextmanager
async def log_time(scope: str) -> AsyncIterator[None]:
    start = utc_now()
    logger.info("Starting %s", scope)
    try:
        yield
    finally:
        dur = (utc_now() - start).total_seconds()
        logger.info("Finished %s in %.2fs", scope, dur)
