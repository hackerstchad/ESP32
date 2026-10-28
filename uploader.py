"""
Téléversement de fichiers et firmware vers l'ESP32.
"""

import os
import re
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional

from ..core.config import get_config
from ..core.constants import DEFAULT_BAUD
from ..core.logger import get_logger
from .repl import MicroPythonRepl

logger = get_logger(__name__)


@dataclass
class UploadTask:
    local_path: Path
    remote_path: str
    content: Optional[bytes] = None


class Uploader:
    """Outil de transfert de fichiers via le REPL MicroPython."""

    def __init__(self, repl: MicroPythonRepl):
        self.repl = repl
        self._cancel = False
        self._progress_cb: Optional[Callable[[int, int, str], None]] = None

    def set_progress_callback(self, callback: Callable[[int, int, str], None]) -> None:
        self._progress_cb = callback

    def cancel(self) -> None:
        self._cancel = True

    def _report(self, current: int, total: int, message: str) -> None:
        if self._progress_cb:
            try:
                self._progress_cb(current, total, message)
            except Exception as e:
                logger.error(f"Progress callback error: {e}")

    def upload_file(self, local_path: Path, remote_name: Optional[str] = None) -> bool:
        if not self.repl.is_connected:
            return False
        remote = remote_name or local_path.name
        try:
            content = local_path.read_bytes()
        except Exception as e:
            logger.error(f"Lecture fichier impossible: {e}")
            return False
        return self._upload_bytes(content, remote)

    def upload_text(self, text: str, remote_name: str) -> bool:
        if not self.repl.is_connected:
            return False
        return self._upload_bytes(text.encode("utf-8"), remote_name)

    def _upload_bytes(self, content: bytes, remote_name: str) -> bool:
        chunk_size = 256
        total = len(content)
        self._report(0, total, f"Préparation de {remote_name}")

        header = f"f = open({remote_name!r}, 'wb')\r\n"
        self.repl.write_raw(header.encode("utf-8"))
        time.sleep(0.05)

        written = 0
        for i in range(0, total, chunk_size):
            if self._cancel:
                self.repl.write_raw(b"f.close()\r\n")
                return False
            chunk = content[i : i + chunk_size]
            escaped = chunk.replace(b"\\", b"\\\\").replace(b"'", b"\\'")
            line = f"f.write({escaped!r})\r\n".encode("utf-8")
            self.repl.write_raw(line)
            written += len(chunk)
            self._report(written, total, f"Écriture {remote_name}")
            time.sleep(0.02)

        self.repl.write_raw(b"f.close()\r\n")
        self._report(total, total, f"{remote_name} terminé")
        logger.info(f"Téléversé {remote_name} ({total} octets)")
        return True

    def upload_project(self, project_dir: Path) -> bool:
        files = [p for p in project_dir.rglob("*") if p.is_file()]
        total = len(files)
        for idx, f in enumerate(files, 1):
            if self._cancel:
                return False
            rel = f.relative_to(project_dir).as_posix()
            self._report(idx, total, f"[{idx}/{total}] {rel}")
            if not self.upload_file(f, rel):
                logger.error(f"Échec upload {rel}")
                return False
        return True

    def run_remote(self, remote_name: str) -> List[str]:
        return self.repl.send_command(f"exec(open({remote_name!r}).read())", raw=True, timeout=10.0)
