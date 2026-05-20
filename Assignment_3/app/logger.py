from functools import lru_cache
import logging
import sys
from pathlib import Path


@lru_cache(maxsize=1)
def configure_logging() -> logging.Logger:
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return root_logger

    root_logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler = logging.FileHandler(Path("app.log"), encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)
    return root_logger


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)
