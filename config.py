"""
Gestion persistante de la configuration utilisateur.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from .constants import BASE_DIR

CONFIG_PATH = BASE_DIR / "config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "theme": "dark",
    "editor": {
        "font_family": "JetBrains Mono",
        "font_size": 12,
        "tab_size": 4,
        "show_line_numbers": True,
        "word_wrap": False,
        "auto_save": True,
        "highlight_syntax": True,
    },
    "serial": {
        "baud_rate": 115200,
        "auto_connect": True,
        "preferred_port": None,
        "reconnect_interval_ms": 2000,
        "read_timeout_ms": 100,
    },
    "device": {
        "chip": "auto",
        "flash_mode": "dio",
        "flash_size": "detect",
        "firmware_path": None,
    },
    "ui": {
        "language": "fr",
        "sidebar_width": 240,
        "terminal_height": 200,
        "window_state": "normal",
    },
    "paths": {
        "last_project": None,
        "last_file": None,
    },
}


class ConfigManager:
    """Singleton de gestion de la configuration."""

    _instance: Optional["ConfigManager"] = None

    def __new__(cls) -> "ConfigManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._data = {}
            cls._instance.load()
        return cls._instance

    def load(self) -> None:
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self._data = self._merge(DEFAULT_CONFIG, loaded)
            except Exception:
                self._data = DEFAULT_CONFIG.copy()
        else:
            self._data = DEFAULT_CONFIG.copy()

    def save(self) -> None:
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Impossible de sauvegarder la configuration: {e}")

    def get(self, key_path: str, default: Any = None) -> Any:
        keys = key_path.split(".")
        value = self._data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key_path: str, value: Any) -> None:
        keys = key_path.split(".")
        target = self._data
        for k in keys[:-1]:
            if k not in target or not isinstance(target[k], dict):
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value
        self.save()

    def all(self) -> Dict[str, Any]:
        return self._data.copy()

    @staticmethod
    def _merge(default: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        result = default.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigManager._merge(result[key], value)
            else:
                result[key] = value
        return result


def get_config() -> ConfigManager:
    return ConfigManager()
