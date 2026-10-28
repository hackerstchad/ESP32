"""
Coloration syntaxique Python pour Tkinter Text.
"""

import re
import tkinter as tk
from typing import Dict, List, Tuple

from ..core.config import get_config
from ..core.theme import get_theme


PYTHON_KEYWORDS = [
    "and", "as", "assert", "async", "await", "break", "class", "continue",
    "def", "del", "elif", "else", "except", "False", "finally", "for",
    "from", "global", "if", "import", "in", "is", "lambda", "None",
    "nonlocal", "not", "or", "pass", "raise", "return", "True", "try",
    "while", "with", "yield",
]

PYTHON_BUILTINS = [
    "abs", "all", "any", "bin", "bool", "bytearray", "bytes", "callable",
    "chr", "classmethod", "compile", "complex", "delattr", "dict", "dir",
    "divmod", "enumerate", "eval", "exec", "filter", "float", "format",
    "frozenset", "getattr", "globals", "hasattr", "hash", "help", "hex",
    "id", "input", "int", "isinstance", "issubclass", "iter", "len",
    "list", "locals", "map", "max", "memoryview", "min", "next", "object",
    "oct", "open", "ord", "pow", "print", "property", "range", "repr",
    "reversed", "round", "set", "setattr", "slice", "sorted", "staticmethod",
    "str", "sum", "super", "tuple", "type", "vars", "zip", "__import__",
    "machine", "pin", "i2c", "spi", "uart", "pwm", "adc", "dac", "rtc",
    "network", "socket", "bluetooth", "urequests", "json", "ubinascii",
    "ucollections", "uerrno", "uhashlib", "uheapq", "uio", "ujson", "uos",
    "upoplib", "ure", "uselect", "usocket", "ussl", "ustruct", "usys",
    "utime", "uzlib", "esp", "esp32",
]

PYTHON_DECORATORS = [r"@\w+"]

TOKEN_PATTERNS: List[Tuple[str, str]] = [
    ("comment", r"#[^\n]*"),
    ("string_triple", r"(\"\"\"[\s\S]*?\"\"\"|'''[\s\S]*?''')"),
    ("string_double", r"\"[^\"\\]*(\\.[^\"\\]*)*\""),
    ("string_single", r"'[^'\\]*(\\.[^'\\]*)*'"),
    ("decorator", r"@\w+"),
    ("number", r"\b(?:0[xX][0-9a-fA-F]+|\d+\.?\d*(?:[eE][+-]?\d+)?j?)\b"),
    ("function", r"\b([A-Za-z_][A-Za-z0-9_]*)\s*(?=\()"),
    ("keyword", r"\b(" + "|".join(PYTHON_KEYWORDS) + r")\b"),
    ("builtin", r"\b(" + "|".join(PYTHON_BUILTINS) + r")\b"),
]


class SyntaxHighlighter:
    """Applique la coloration syntaxique sur un widget Text."""

    def __init__(self, text_widget: tk.Text):
        self.text = text_widget
        self._enabled = get_config().get("editor.highlight_syntax", True)
        self._setup_tags()

    def _setup_tags(self) -> None:
        theme = get_theme()
        tag_colors = {
            "keyword": theme.keyword,
            "string": theme.string,
            "string_triple": theme.string,
            "string_double": theme.string,
            "string_single": theme.string,
            "comment": theme.comment,
            "number": theme.number,
            "function": theme.function,
            "builtin": theme.info,
            "decorator": theme.decorator,
        }
        for tag, color in tag_colors.items():
            self.text.tag_configure(tag, foreground=color)

    def enable(self) -> None:
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False
        for tag in ["keyword", "string", "comment", "number", "function", "builtin", "decorator"]:
            self.text.tag_remove(tag, "1.0", "end")

    def apply(self, start: str = "1.0", end: str = "end") -> None:
        if not self._enabled:
            return

        for tag in ["keyword", "string", "string_triple", "string_double", "string_single",
                    "comment", "number", "function", "builtin", "decorator"]:
            self.text.tag_remove(tag, start, end)

        code = self.text.get(start, end)
        base_line = int(float(start))

        combined = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_PATTERNS)

        for match in re.finditer(combined, code):
            for group_name, _ in TOKEN_PATTERNS:
                if match.group(group_name):
                    line_offset = code[: match.start()].count("\n")
                    line = base_line + line_offset
                    col_start = match.start() - code.rfind("\n", 0, match.start()) - 1
                    col_end = col_start + len(match.group(group_name))
                    pos_start = f"{line}.{col_start}"
                    pos_end = f"{line}.{col_end}"
                    tag = "string" if group_name.startswith("string_") else group_name
                    self.text.tag_add(tag, pos_start, pos_end)
                    break
