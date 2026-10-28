"""
Communication REPL MicroPython avec l'ESP32.
"""

import re
import threading
import time
from typing import Callable, List, Optional

import serial

from ..core.config import get_config
from ..core.constants import DEFAULT_BAUD, REPL_INTERRUPT, REPL_NORMAL_MODE, REPL_PROMPT, REPL_RAW_MODE, REPL_SOFT_REBOOT
from ..core.logger import get_logger

logger = get_logger(__name__)


class MicroPythonRepl:
    """Client série pour interagir avec le REPL MicroPython."""

    def __init__(self, port: Optional[str] = None, baud: int = DEFAULT_BAUD):
        self.port = port
        self.baud = baud
        self._serial: Optional[serial.Serial] = None
        self._lock = threading.Lock()
        self._reader_thread: Optional[threading.Thread] = None
        self._running = False
        self._data_callback: Optional[Callable[[str], None]] = None
        self._prompt_callback: Optional[Callable[[], None]] = None
        self._buffer = bytearray()
        self._last_prompt = time.time()

    @property
    def is_connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

    def set_data_callback(self, callback: Callable[[str], None]) -> None:
        self._data_callback = callback

    def set_prompt_callback(self, callback: Callable[[], None]) -> None:
        self._prompt_callback = callback

    def connect(self, port: str, baud: int = DEFAULT_BAUD) -> bool:
        self.disconnect()
        self.port = port
        self.baud = baud
        try:
            self._serial = serial.Serial(
                port=port,
                baudrate=baud,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.05,
                write_timeout=2.0,
            )
            self._running = True
            self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
            self._reader_thread.start()
            time.sleep(0.2)
            self.interrupt()
            self._enter_raw_repl()
            return True
        except Exception as e:
            logger.error(f"Connexion série échouée: {e}")
            self.disconnect()
            return False

    def disconnect(self) -> None:
        self._running = False
        if self._serial and self._serial.is_open:
            try:
                self._serial.close()
            except Exception:
                pass
        self._serial = None

    def write_raw(self, data: bytes) -> None:
        if self._serial and self._serial.is_open:
            try:
                self._serial.write(data)
                self._serial.flush()
            except Exception as e:
                logger.error(f"Écriture série échouée: {e}")

    def send_command(self, command: str, raw: bool = False, timeout: float = 3.0) -> List[str]:
        if not self.is_connected:
            return []
        with self._lock:
            if raw:
                self._enter_raw_repl()
            self._buffer.clear()
            self.write_raw((command + "\r\n").encode("utf-8"))
            deadline = time.time() + timeout
            lines: List[str] = []
            while time.time() < deadline:
                time.sleep(0.05)
                text = self._decode_buffer()
                if text:
                    lines.extend(text.splitlines())
                if REPL_PROMPT in text or (raw and b"OK" in self._buffer):
                    break
            return lines

    def interrupt(self) -> None:
        self.write_raw(REPL_INTERRUPT.encode("latin-1"))
        time.sleep(0.1)

    def soft_reboot(self) -> None:
        self.write_raw(REPL_SOFT_REBOOT.encode("latin-1"))

    def _enter_raw_repl(self) -> None:
        self.write_raw(REPL_NORMAL_MODE.encode("latin-1"))
        time.sleep(0.05)
        self.write_raw(REPL_RAW_MODE.encode("latin-1"))
        time.sleep(0.1)

    def _read_loop(self) -> None:
        while self._running and self._serial and self._serial.is_open:
            try:
                data = self._serial.read(self._serial.in_waiting or 1)
                if data:
                    self._buffer.extend(data)
                    text = self._decode_buffer()
                    if text and self._data_callback:
                        self._data_callback(text)
                    if REPL_PROMPT.encode("utf-8") in self._buffer:
                        self._last_prompt = time.time()
                        if self._prompt_callback:
                            self._prompt_callback()
            except Exception as e:
                logger.debug(f"Lecture série: {e}")
                time.sleep(0.1)

    def _decode_buffer(self) -> str:
        try:
            text = self._buffer.decode("utf-8")
            self._buffer.clear()
            return text
        except UnicodeDecodeError:
            try:
                text = self._buffer.decode("latin-1")
                self._buffer.clear()
                return text
            except Exception:
                return ""

    def list_files(self) -> List[str]:
        lines = self.send_command("import os; print(os.listdir())")
        result: List[str] = []
        for line in lines:
            try:
                items = eval(line)
                if isinstance(items, list):
                    result.extend(items)
            except Exception:
                continue
        return result

    def remove_file(self, remote_name: str) -> bool:
        lines = self.send_command(f"import os; os.remove({remote_name!r})")
        return not any("Error" in line for line in lines)
