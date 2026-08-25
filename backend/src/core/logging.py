import sys

from loguru import logger

from src.core.config import settings


def setup_logging():
    logger.remove()
    log_level = "DEBUG" if settings.MODE in ("DEV", "LOCAL", "TEST") else "INFO"
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}:{function}:{line}</cyan> - <level>{message}</level> <dim>{extra}</dim>",
        level=log_level,
    )


__all__ = ["logger", "setup_logging"]

