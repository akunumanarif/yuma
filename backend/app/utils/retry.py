import asyncio
import functools
import logging
from typing import Type

logger = logging.getLogger(__name__)


class RetryExhausted(Exception):
    pass


def retry(max_attempts: int = 3, backoff_base: float = 2.0, retryable_exceptions: tuple = (Exception,)):
    def decorator(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_attempts):
                try:
                    return await fn(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exc = e
                    if attempt < max_attempts - 1:
                        wait = backoff_base ** attempt
                        logger.warning(f"{fn.__name__} attempt {attempt + 1} failed: {e}. Retrying in {wait}s...")
                        await asyncio.sleep(wait)
                    else:
                        logger.error(f"{fn.__name__} failed after {max_attempts} attempts: {e}")
            raise RetryExhausted(f"Failed after {max_attempts} attempts: {last_exc}") from last_exc
        return wrapper
    return decorator
