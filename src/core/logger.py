import sys
from loguru import logger
from src.core import settings

def configure_logger(level: str = "INFO") -> None:
    logger.remove()
    logger.add(
        sys.stdout,
        level=level,
        format=settings,
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )

# Initialize a centralized logger
configure_logger()