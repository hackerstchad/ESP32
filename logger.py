"""
Journalisation centralisée de l'application.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from .constants import LOG_DIR


class TkinterLogHandler(logging.Handler):
    """Handler redirigeant les logs vers un widget Tkinter."""

    def __init__(self, widget=None):
        super().__init__()
        self.widget = widget
        self.formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        if self.widget:
            try:
                self.widget.after(0, lambda m=msg: self.widget.insert("end", m + "\n"))
            except Exception:
                pass


def setup_logging() -> logging.Logger:
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOG_DIR / f"esp32_ide_{today}.log"
    logger = logging.getLogger("esp32_ide")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
