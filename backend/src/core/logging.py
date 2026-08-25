import sys

from loguru import logger


def setup_logging():
    logger.remove()
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level> <dim>{extra}</dim>",
        level="INFO",
    )


__all__ = ["logger", "setup_logging"]