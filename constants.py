"""
Constantes globales de l'application ESP32 IDE.
"""

import os
from pathlib import Path

APP_NAME = "ESP32 MicroPython IDE"
APP_VERSION = "2026.1.0"
APP_AUTHOR = "hackers_tchad"
APP_YEAR = "2026"
APP_REPO = "https://github.com/hackers_tchad/esp32-ide"

# Répertoires
BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
PROJECTS_DIR = Path.home() / "ESP32Projects"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Ports courants ESP32 par OS
ESP32_VID_PIDS = [
    (0x10C4, 0xEA60),  # CP210x
    (0x1A86, 0x7523),  # CH340
    (0x1A86, 0x55D4),  # CH340G
    (0x0403, 0x6001),  # FT232R
    (0x0403, 0x6010),  # FT2232H
    (0x303A, 0x0002),  # ESP32-S2/S3 native USB
    (0x303A, 0x1001),  # ESP32-C3/C6
    (0x303A, 0x0009),  # ESP32-S3 dual
    (0x0483, 0x5740),  # STM32 VCP
    (0x2E8A, 0x0005),  # Raspberry Pi Pico / RP2040
]

BAUD_RATES = [9600, 19200, 38400, 57600, 74880, 115200, 230400, 460800, 921600]
DEFAULT_BAUD = 115200

# Commandes REPL MicroPython
REPL_PROMPT = ">>> "
REPL_SOFT_REBOOT = "\x04"
REPL_RAW_MODE = "\x01"
REPL_NORMAL_MODE = "\x02"
REPL_INTERRUPT = "\x03"
REPL_PASTE_MODE = "\x05"
REPL_TAB = "    "

# Extensions prises en charge
SUPPORTED_EXTS = (".py", ".mpy", ".txt", ".json", ".xml", ".html", ".css", ".js", ".md")
EDITOR_FONT = ("JetBrains Mono", 12)
EDITOR_FONT_FALLBACK = ("Consolas", 12)
UI_FONT = ("Segoe UI", 10)

# Couleurs matérielles
COLORS = {
    "bg_dark": "#0d1117",
    "bg_panel": "#161b22",
    "bg_input": "#21262d",
    "border": "#30363d",
    "text": "#c9d1d9",
    "text_muted": "#8b949e",
    "accent": "#58a6ff",
    "accent_hover": "#79c0ff",
    "success": "#3fb950",
    "warning": "#d29922",
    "error": "#f85149",
    "info": "#a371f7",
}

# Messages
STATUS_DISCONNECTED = "Déconnecté"
STATUS_CONNECTED = "Connecté"
STATUS_SCANNING = "Détection en cours..."
STATUS_UPLOADING = "Transfert en cours..."
