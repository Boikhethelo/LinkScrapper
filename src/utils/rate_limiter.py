import asyncio
import random
import time
from src.utils.logger import logger
from config.settings import settings


class RateLimiter:
    """
    Adds randomised delays between requests to mimic human browsing
    and reduce the risk of being blocked by LinkedIn.
    """

    async def wait(self):
        """Async wait — use inside async scraping functions."""
        delay = random.uniform(settings.MIN_DELAY, settings.MAX_DELAY)
        logger.debug(f"⏳ Waiting {delay:.1f}s before next request...")
        await asyncio.sleep(delay)

    def sync_wait(self):
        """Sync wait — use inside non-async contexts (e.g. API calls)."""
        delay = random.uniform(settings.MIN_DELAY, settings.MAX_DELAY)
        logger.debug(f"⏳ Waiting {delay:.1f}s before next request...")
        time.sleep(delay)


# Shared singleton used across the project
rate_limiter = RateLimiter()
