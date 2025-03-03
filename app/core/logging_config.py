import logging
import sys
from typing import List


def setup_logging(log_level: str = "INFO") -> None:
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    loggers: List[str] = [
        "app",
        "uvicorn",
        "fastapi",
        "aiokafka",
    ]

    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)
        logger.addHandler(console_handler)
        logger.propagate = False
