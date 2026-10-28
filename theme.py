"""
Gestionnaire de thème visuel dynamique.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class Theme:
    name: str
    background: str
    panel: str
    input_bg: str
    border: str
    foreground: str
    muted: str
    accent: str
    accent_hover: str
    success: str
    warning: str
    error: str
    info: str
    highlight: str
    line_number_bg: str
    line_number_fg: str
    selection: str
    caret: str
    keyword: str
    string: str
    comment: str
    number: str
    function: str
    decorator: str
    custom: Dict[str, Any] = field(default_factory=dict)


DARK_THEME = Theme(
    name="dark",
    background="#0d1117",
    panel="#161b22",
    input_bg="#21262d",
    border="#30363d",
    foreground="#c9d1d9",
    muted="#8b949e",
    accent="#58a6ff",
    accent_hover="#79c0ff",
    success="#3fb950",
    warning="#d29922",
    error="#f85149",
    info="#a371f7",
    highlight="#264f78",
    line_number_bg="#0d1117",
    line_number_fg="#6e7681",
    selection="#264f78",
    caret="#58a6ff",
    keyword="#ff7b72",
    string="#a5d6ff",
    comment="#8b949e",
    number="#79c0ff",
    function="#d2a8ff",
    decorator="#f0883e",
)

LIGHT_THEME = Theme(
    name="light",
    background="#ffffff",
    panel="#f6f8fa",
    input_bg="#ffffff",
    border="#d0d7de",
    foreground="#1f2328",
    muted="#6e7781",
    accent="#0969da",
    accent_hover="#0860ca",
    success="#1a7f37",
    warning="#9a6700",
    error="#cf222e",
    info="#8250df",
    highlight="#ddf4ff",
    line_number_bg="#f6f8fa",
    line_number_fg="#6e7781",
    selection="#b6e3ff",
    caret="#0969da",
    keyword="#cf222e",
    string="#0a3069",
    comment="#6e7781",
    number="#0550ae",
    function="#8250df",
    decorator="#953800",
)

THEMES = {"dark": DARK_THEME, "light": LIGHT_THEME}

_current = DARK_THEME


def get_theme() -> Theme:
    return _current


def set_theme(name: str) -> Theme:
    global _current
    if name in THEMES:
        _current = THEMES[name]
    return _current


def toggle_theme() -> Theme:
    global _current
    _current = LIGHT_THEME if _current.name == "dark" else DARK_THEME
    return _current
