import logging
import sys

logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("main")


def get_logger(name: str, level=logging.INFO) -> logging.Logger:
    logger.setLevel(level)
    return logging.getLogger(f"main.{name}")
