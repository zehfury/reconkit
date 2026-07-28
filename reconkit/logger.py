"""
Central logging setup. Every module logs through this instead of
print(), so a run produces one consistent, timestamped log — on
screen and in a log file — regardless of which modules succeed or
fail.
"""

import logging
import sys
from pathlib import Path


def get_logger(log_dir: str = "logs") -> logging.Logger:
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("reconkit")
    if logger.handlers:
        # Already configured (e.g. called more than once in one run)
        return logger

    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(fmt)

    file_handler = logging.FileHandler(Path(log_dir) / "reconkit.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)

    logger.addHandler(console)
    logger.addHandler(file_handler)
    return logger
