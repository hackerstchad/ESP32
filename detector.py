"""
Détection automatique de périphériques ESP32 connectés.
"""

import platform
import re
import subprocess
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple

from ..core.constants import ESP32_VID_PIDS


@dataclass
class SerialPort:
    port: str
    description: str
    hwid: str
    vid: Optional[int] = None
    pid: Optional[int] = None
    is_esp32: bool = False
    chip_guess: str = "Inconnu"

    def __str__(self) -> str:
        return f"{self.port} - {self.description} ({self.chip_guess})"


def _parse_usb_ids(hwid: str) -> Tuple[Optional[int], Optional[int]]:
    match = re.search(r"VID[_:]PID=([0-9A-Fa-f]{4})[_:]([0-9A-Fa-f]{4})", hwid)
    if match:
        return int(match.group(1), 16), int(match.group(2), 16)
    return None, None


def _guess_chip(vid: Optional[int], pid: Optional[int], description: str) -> str:
    desc = description.upper()
    if (vid, pid) in ESP32_VID_PIDS:
        if "S3" in desc:
            return "ESP32-S3"
        if "S2" in desc:
            return "ESP32-S2"
        if "C6" in desc:
            return "ESP32-C6"
        if "C3" in desc:
            return "ESP32-C3"
        if "ESP32" in desc:
            return "ESP32"
        return "ESP32-compatible"
    if "CP210" in desc:
        return "CP210x (probable ESP32)"
    if "CH340" in desc or "CH341" in desc:
        return "CH340 (probable ESP32)"
    if "FTDI" in desc or "FT23" in desc:
        return "FTDI (probable ESP32)"
    return "Inconnu"


def _is_esp32_candidate(port: str, description: str, hwid: str) -> bool:
    vid, pid = _parse_usb_ids(hwid)
    if (vid, pid) in ESP32_VID_PIDS:
        return True
    desc = description.upper()
    if any(k in desc for k in ["CP210", "CH340", "CH341", "FTDI", "FT23", "ESP32"]):
        return True
    if "USB" in desc and ("SERIAL" in desc or "UART" in desc):
        return True
    return False


def list_serial_ports() -> List[SerialPort]:
    """Liste les ports série disponibles."""
    try:
        import serial.tools.list_ports
    except ImportError as exc:
        raise RuntimeError("pyserial non installé") from exc

    ports: List[SerialPort] = []
    for p in serial.tools.list_ports.comports():
        vid, pid = _parse_usb_ids(p.hwid)
        is_esp = _is_esp32_candidate(p.device, p.description or "", p.hwid or "")
        chip = _guess_chip(vid, pid, p.description or "")
        ports.append(
            SerialPort(
                port=p.device,
                description=p.description or "Périphérie inconnu",
                hwid=p.hwid or "",
                vid=vid,
                pid=pid,
                is_esp32=is_esp,
                chip_guess=chip,
            )
        )
    return ports


def detect_esp32_port(preferred: Optional[str] = None) -> Optional[SerialPort]:
    """Détecte le premier ESP32 branché ou le port préféré s'il existe."""
    ports = list_serial_ports()
    esp_ports = [p for p in ports if p.is_esp32]

    if preferred:
        for p in esp_ports:
            if p.port == preferred:
                return p

    if esp_ports:
        return esp_ports[0]
    return None


def wait_for_esp32(timeout_seconds: float = 30.0, preferred: Optional[str] = None) -> Optional[SerialPort]:
    """Attend le branchement d'un ESP32."""
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        port = detect_esp32_port(preferred)
        if port:
            return port
        time.sleep(0.5)
    return None
