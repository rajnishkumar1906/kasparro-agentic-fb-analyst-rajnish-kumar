"""
src/utils/logger.py

Provides a simple colored logger using Rich.
"""

from rich.console import Console
from rich.logging import RichHandler
import logging


def get_logger(name: str):
    console = Console()

    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console)]
    )

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger
