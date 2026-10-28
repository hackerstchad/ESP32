"""
Fonctions utilitaires générales.
"""

import os
import re
import sys
from pathlib import Path
from typing import Optional


def human_size(size_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    idx = 0
    size = float(size_bytes)
    while size >= 1024 and idx < len(units) - 1:
        size /= 1024
        idx += 1
    return f"{size:.1f} {units[idx]}"


def is_valid_python_identifier(name: str) -> bool:
    return bool(re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name))


def get_resource_path(relative_path: str) -> Path:
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent.parent
    return base / relative_path


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path
