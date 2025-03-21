import logging
import sys
import os

logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("main")

for key, value in os.environ.items():
    print(f"{key}: {value}")


def get_logger(name: str, level=logging.INFO) -> logging.Logger:
    logger.setLevel(level)
    return logging.getLogger(f"main.{name}")
