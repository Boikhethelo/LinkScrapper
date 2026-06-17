"""
Configures Loguru and sends messages to the console and a log file
"""

import sys
from loguru import logger

# Remove default handler
logger.remove()

# ── Console handler ───────────────────────────────────────────────────────────
logger.add(
    sys.stdout,
    colorize=True,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan> - "
        "<level>{message}</level>"
    ),
    level="INFO",
)

# ── File handler ──────────────────────────────────────────────────────────────
logger.add(
    "logs/scraper.log",
    rotation="10 MB",
    retention="7 days",
    encoding="utf-8",
    level="DEBUG",
)
