import logging
import time
from contextlib import contextmanager

logger = logging.getLogger("llm_quiz")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)


@contextmanager
def time_limit(seconds: float):
    """
    Soft time limit helper. We don't hard-kill, but we can log if exceeded.
    """
    start = time.monotonic()
    yield
    elapsed = time.monotonic() - start
    if elapsed > seconds:
        logger.warning("Block exceeded soft time limit: %.2fs > %.2fs", elapsed, seconds)
