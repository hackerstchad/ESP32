#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# hacker_ide_esp32.py — script unique, avancé, stylisé pour ESP32 / MicroPython
# Auteur : Hackers_Tchad
# Date   : 2026
# Licence: MIT

import os
import sys
import re
import io
import json
import time
import queue
import serial
import serial.tools.list_ports
import threading
import subprocess
import tempfile
import shutil
import hashlib
import base64
import webbrowser
import datetime
import traceback
import tkinter as tk
from tkinter import (
    ttk, scrolledtext, messagebox, filedialog, colorchooser, font,
    simpledialog, Menu, BooleanVar, StringVar, IntVar, DoubleVar
)
from tkinter import font as tkfont
from functools import partial
from pathlib import Path

# Importations optionnelles avec fallback
PYGMENTS_OK = False
try:
    from pygments import lex
    from pygments.lexers import PythonLexer
    from pygments.token import Token
    PYGMENTS_OK = True
except ImportError:
    pass

AMPY_OK = False
try:
    import ampy.files as ampy_files
    import ampy.pyboard as ampy_pyboard
    AMPY_OK = True
except ImportError:
    pass

ESPTOOL_OK = False
try:
    import esptool
    ESPTOOL_OK = True
except ImportError:
    pass

PIL_OK = False
try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont
    PIL_OK = True
except ImportError:
    pass

MPREMOTE_OK = False
try:
    import mpremote
    MPREMOTE_OK = True
except ImportError:
    pass


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTES & CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

APP_NAME = "HackerESP32-IDE"
APP_VERSION = "2026.1"
APP_AUTHOR = "Hackers_Tchad"
APP_DATE = "2026"

# Thèmes
THEMES = {
    "hacker": {
        "bg": "#050505",
        "fg": "#00ff41",
        "insert": "#00ff41",
        "select_bg": "#003b00",
        "select_fg": "#00ff41",
        "line_bg": "#0a0a0a",
        "line_fg": "#008f11",
        "button_bg": "#0d0d0d",
        "button_fg": "#00ff41",
        "button_active": "#003b00",
        "border": "#00ff41",
        "accent": "#00ff41",
        "error": "#ff3333",
        "warning": "#ffcc00",
        "info": "#00ccff",
        "keyword": "#00ff41",
        "string": "#00cc66",
        "comment": "#008f11",
        "number": "#66ffcc",
        "function": "#66ff99",
        "class_name": "#ccff66",
    },
    "dark": {
        "bg": "#1e1e1e",
        "fg": "#d4d4d4",
        "insert": "#d4d4d4",
        "select_bg": "#264f78",
        "select_fg": "#ffffff",
        "line_bg": "#1e1e1e",
        "line_fg": "#858585",
        "button_bg": "#2d2d30",
        "button_fg": "#d4d4d4",
        "button_active": "#3e3e42",
        "border": "#3e3e42",
        "accent": "#007acc",
        "error": "#f44747",
        "warning": "#ffcc00",
        "info": "#4fc1ff",
        "keyword": "#569cd6",
        "string": "#ce9178",
        "comment": "#6a9955",
        "number": "#b5cea8",
        "function": "#dcdcaa",
        "class_name": "#4ec9b0",
    },
    "light": {
        "bg": "#ffffff",
        "fg": "#000000",
        "insert": "#000000",
        "select_bg": "#add6ff",
        "select_fg": "#000000",
        "line_bg": "#f5f5f5",
        "line_fg": "#237893",
        "button_bg": "#e5e5e5",
        "button_fg": "#000000",
        "button_active": "#cccccc",
        "border": "#cccccc",
        "accent": "#0078d4",
        "error": "#cd3131",
        "warning": "#ff8c00",
        "info": "#0070c1",
        "keyword": "#0000ff",
        "string": "#a31515",
        "comment": "#008000",
        "number": "#098658",
        "function": "#795e26",
        "class_name": "#267f99",
    },
    "midnight": {
        "bg": "#0f172a",
        "fg": "#e2e8f0",
        "insert": "#e2e8f0",
        "select_bg": "#334155",
        "select_fg": "#ffffff",
        "line_bg": "#0f172a",
        "line_fg": "#64748b",
        "button_bg": "#1e293b",
        "button_fg": "#e2e8f0",
        "button_active": "#334155",
        "border": "#334155",
        "accent": "#38bdf8",
        "error": "#ef4444",
        "warning": "#f59e0b",
        "info": "#38bdf8",
        "keyword": "#c084fc",
        "string": "#f472b6",
        "comment": "#64748b",
        "number": "#2dd4bf",
        "function": "#38bdf8",
        "class_name": "#facc15",
    },
    "cyberpunk": {
        "bg": "#0a001a",
        "fg": "#ff00ff",
        "insert": "#ff00ff",
        "select_bg": "#330066",
        "select_fg": "#ffffff",
        "line_bg": "#120024",
        "line_fg": "#9900cc",
        "button_bg": "#1a0033",
        "button_fg": "#ff00ff",
        "button_active": "#330066",
        "border": "#ff00ff",
        "accent": "#00ffff",
        "error": "#ff3333",
        "warning": "#ffcc00",
        "info": "#00ffff",
        "keyword": "#ff00ff",
        "string": "#00ffcc",
        "comment": "#660099",
        "number": "#ff66ff",
        "function": "#00ccff",
        "class_name": "#ffff00",
    },
}

DEFAULT_THEME = "hacker"

ESP32_SIGNATURES = {
    "VID": [0x10C4, 0x1A86, 0x0403, 0x303A, 0x0483, 0x067B, 0x2341],
    "PID": [0xEA60, 0x7523, 0x6001, 0x0002, 0x5740, 0x2303, 0x0042, 0x0245, 0x024B],
}

DEFAULT_BAUDRATES = ["9600", "115200", "230400", "460800", "921600"]
DEFAULT_CODE = """# ESP32 MicroPython - Hackers_Tchad 2026
from machine import Pin, Timer
import time

led = Pin(2, Pin.OUT)

print("Hello ESP32 from HackerESP32-IDE!")

while True:
    led.value(1)
    time.sleep(0.5)
    led.value(0)
    time.sleep(0.5)
"""

SETTINGS_FILE = Path.home() / ".hacker_ide_esp32.json"
RECENT_FILES_LIMIT = 15
HISTORY_LIMIT = 100


# ═══════════════════════════════════════════════════════════════════════════════
# GESTION DES PARAMÈTRES
# ═══════════════════════════════════════════════════════════════════════════════

class SettingsManager:
    """Gère la persistance des préférences utilisateur."""

    defaults = {
        "theme": DEFAULT_THEME,
        "font_family": "Consolas",
        "font_size": 12,
        "tab_size": 4,
        "word_wrap": False,
        "show_line_numbers": True,
        "auto_save": True,
        "auto_save_interval": 30,
        "highlight_syntax": True,
        "detect_esp32": True,
        "auto_connect": False,
        "last_port": "",
        "last_baud": "115200",
        "recent_files": [],
        "window_geometry": "1400x900+50+30",
        "editor_split": 0.7,
        "terminal_echo": True,
        "flash_firmware_path": "",
        "backup_before_upload": True,
        "backup_before_flash": True,
        "terminal_history": [],
        "toolbar_visible": True,
        "statusbar_visible": True,
        "minimap_visible": False,
        "autocomplete": True,
        "autoindent": True,
        "folding": False,
    }

    def __init__(self, path=SETTINGS_FILE):
        self.path = path
        self.data = dict(self.defaults)
        self.load()

    def load(self):
        try:
            if self.path.exists():
                with open(self.path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self.data.update(loaded)
        except Exception:
            pass

    def save(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def get(self, key, default=None):
        return self.data.get(key, default if default is not None else self.defaults.get(key))

    def set(self, key, value):
        self.data[key] = value

    def add_recent_file(self, filepath):
        recent = self.get("recent_files", [])
        if filepath in recent:
            recent.remove(filepath)
        recent.insert(0, filepath)
        self.set("recent_files", recent[:RECENT_FILES_LIMIT])


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITAIRES
# ═══════════════════════════════════════════════════════════════════════════════

class Logger:
    """Logger centralisé avec niveaux."""

    def __init__(self, app=None):
        self.app = app

    def log(self, msg, level="INFO"):
        ts = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        line = f"[{ts}] [{level}] {msg}"
        if self.app and hasattr(self.app, "write_log"):
            self.app.write_log(line)
        else:
            print(line)

    def info(self, msg):
        self.log(msg, "INFO")

    def warn(self, msg):
        self.log(msg, "WARN")

    def error(self, msg):
        self.log(msg, "ERROR")

    def success(self, msg):
        self.log(msg, "OK")


def get_monospace_fonts():
    """Retourne une liste de polices monospaces communes."""
    candidates = [
        "Consolas", "Courier New", "Lucida Console", "DejaVu Sans Mono",
        "Fira Code", "JetBrains Mono", "Source Code Pro", "Ubuntu Mono",
        "Cascadia Code", "Monaco", "Inconsolata", "Hack", "IBM Plex Mono",
    ]
    available = []
    try:
        families = tkfont.families()
        for name in candidates:
            if name in families:
                available.append(name)
    except Exception:
        pass
    if not available:
        available.append("Courier")
    return available


def format_size(num):
    for unit in ["B", "KB", "MB", "GB"]:
        if abs(num) < 1024.0:
            return f"{num:.1f} {unit}"
        num /= 1024.0
    return f"{num:.1f} TB"


def hexdump(data, width=16):
    result = []
    for i in range(0, len(data), width):
        chunk = data[i:i+width]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        result.append(f"{i:08x}  {hex_part:<{width*3}}  {ascii_part}")
    return "\n".join(result)


def is_esp32_port(port):
    """Détecte si un port COM est probablement un ESP32/CP210x/CH340/etc."""
    try:
        vid = getattr(port, "vid", None)
        pid = getattr(port, "pid", None)
        desc = (getattr(port, "description", "") or "").lower()
        hwid = (getattr(port, "hwid", "") or "").lower()
        if vid in ESP32_SIGNATURES["VID"] or pid in ESP32_SIGNATURES["PID"]:
            return True
        keywords = ["cp210", "ch340", "ch910", "ftdi", "usb-serial", "uart", "esp32", "esp8266", "silicon labs", "bluetooth"]
        for kw in keywords:
            if kw in desc or kw in hwid:
                return True
    except Exception:
        pass
    return False


# ═══════════════════════════════════════════════════════════════════════════════
# COMPOSANTS DE L'INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

class LineNumberCanvas(tk.Canvas):
    """Canvas affichant les numéros de ligne synchronisés avec un Text."""

    def __init__(self, parent, text_widget, theme, **kwargs):
        super().__init__(parent, **kwargs)
        self.text_widget = text_widget
        self.theme = theme
        self.config(width=55, bg=theme["line_bg"], highlightthickness=0)
        self.bind("<ButtonPress-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<B1-Motion>", self.on_drag)
        self._drag_start = None

    def set_theme(self, theme):
        self.theme = theme
        self.config(bg=theme["line_bg"])
        self.redraw()

    def redraw(self):
        self.delete("all")
        try:
            first = self.text_widget.index("@0,0")
            last = self.text_widget.index("@0,%d" % self.text_widget.winfo_height())
            line_num = int(float(first))
            last_line = int(float(last)) + 1
            while line_num <= last_line:
                dline = self.text_widget.dlineinfo(f"{line_num}.0")
                if dline:
                    y = dline[1]
                    self.create_text(
                        45, y, text=str(line_num), anchor="ne",
                        fill=self.theme["line_fg"], font=self.text_widget.cget("font")
                    )
                line_num += 1
        except Exception:
            pass

    def on_click(self, event):
        line = int(self.text_widget.index(f"@0,{event.y}").split(".")[0])
        self._drag_start = line
        self.text_widget.mark_set("insert", f"{line}.0")
        self.text_widget.tag_remove("sel", "1.0", "end")
        self.text_widget.tag_add("sel", f"{line}.0", f"{line+1}.0")
        self.text_widget.focus_set()

    def on_drag(self, event):
        if self._drag_start is None:
            return
        line = int(self.text_widget.index(f"@0,{event.y}").split(".")[0])
        start = min(self._drag_start, line)
        end = max(self._drag_start, line)
        self.text_widget.tag_remove("sel", "1.0", "end")
        self.text_widget.tag_add("sel", f"{start}.0", f"{end+1}.0")

    def on_release(self, event):
        self._drag_start = None


class CodeEditor(tk.Text):
    """Éditeur de code enrichi avec coloration syntaxique, indentation auto, etc."""

    def __init__(self, parent, app, **kwargs):
        self.app = app
        self.theme = app.theme
        self.font_family = app.settings.get("font_family", "Consolas")
        self.font_size = app.settings.get("font_size", 12)
        font_obj = tkfont.Font(family=self.font_family, size=self.font_size)
        super().__init__(
            parent,
            wrap="none" if not app.settings.get("word_wrap", False) else "word",
            undo=True,
            maxundo=100,
            autoseparators=True,
            font=font_obj,
            bg=self.theme["bg"],
            fg=self.theme["fg"],
            insertbackground=self.theme["insert"],
            selectbackground=self.theme["select_bg"],
            selectforeground=self.theme["select_fg"],
            relief="flat",
            padx=8,
            pady=8,
            spacing1=2,
            spacing3=2,
            highlightthickness=0,
            **kwargs,
        )
        self._setup_tags()
        self._setup_bindings()
        self._highlight_job = None
        self._pending_changes = False
        self._modified = False
        self._last_count = 0
        self._bracket_stack = []

    def _setup_tags(self):
        self.tag_configure("keyword", foreground=self.theme["keyword"], font=self.cget("font"))
        self.tag_configure("string", foreground=self.theme["string"], font=self.cget("font"))
        self.tag_configure("comment", foreground=self.theme["comment"], font=self.cget("font"))
        self.tag_configure("number", foreground=self.theme["number"], font=self.cget("font"))
        self.tag_configure("function", foreground=self.theme["function"], font=self.cget("font"))
        self.tag_configure("class_name", foreground=self.theme["class_name"], font=self.cget("font"))
        self.tag_configure("operator", foreground=self.theme["accent"], font=self.cget("font"))
        self.tag_configure("error_line", background="#3a0000")
        self.tag_configure("warning_line", background="#3a3a00")
        self.tag_configure("current_line", background=self._blend_color(self.theme["bg"], self.theme["select_bg"], 0.15))
        self.tag_configure("matching_bracket", background=self.theme["select_bg"])
        self.tag_configure("search", background="#444466")
        self.tag_raise("sel")

    def _blend_color(self, c1, c2, ratio):
        try:
            r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
            r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return c1

    def _setup_bindings(self):
        self.bind("<KeyRelease>", self._on_key_release)
        self.bind("<Return>", self._on_return)
        self.bind("<Tab>", self._on_tab)
        self.bind("<BackSpace>", self._on_backspace)
        self.bind("<Control-a>", self._select_all)
        self.bind("<Control-A>", self._select_all)
        self.bind("<Control-d>", self._duplicate_line)
        self.bind("<Control-slash>", self._toggle_comment)
        self.bind("<Control-question>", self._toggle_comment)
        self.bind("<Control-f>", lambda e: self.app.show_find_bar())
        self.bind("<Control-F>", lambda e: self.app.show_find_bar())
        self.bind("<Control-g>", lambda e: self.app.show_goto_line())
        self.bind("<Control-G>", lambda e: self.app.show_goto_line())
        self.bind("<Control-Home>", lambda e: self.mark_set("insert", "1.0"))
        self.bind("<Control-End>", lambda e: self.mark_set("insert", "end-1c"))
        self.bind("<parenleft>", partial(self._insert_bracket_pair, "()"))
        self.bind("<bracketleft>", partial(self._insert_bracket_pair, "[]"))
        self.bind("<braceleft>", partial(self._insert_bracket_pair, "{}"))
        self.bind("<quotedbl>", partial(self._insert_bracket_pair, '""'))
        self.bind("<apostrophe>", partial(self._insert_bracket_pair, "''"))
        self.bind("<KeyRelease>", self._highlight_matching_bracket, add="+")
        self.bind("<Button-1>", self._on_click, add="+")
        self.bind("<B1-Motion>", self._on_drag, add="+")
        self.bind("<MouseWheel>", self._on_scroll)
        self.bind("<Button-4>", self._on_scroll)
        self.bind("<Button-5>", self._on_scroll)
        self.bind("<<Modified>>", self._on_modified)

    def set_theme(self, theme):
        self.theme = theme
        self.config(
            bg=theme["bg"], fg=theme["fg"],
            insertbackground=theme["insert"],
            selectbackground=theme["select_bg"],
            selectforeground=theme["select_fg"],
        )
        self._setup_tags()
        self.highlight_all()

    def set_font(self, family, size):
        font_obj = tkfont.Font(family=family, size=size)
        self.config(font=font_obj)
        self._setup_tags()

    def set_word_wrap(self, wrap):
        self.config(wrap="word" if wrap else "none")

    def _on_key_release(self, event):
        if event.keysym in ("Up", "Down", "Left", "Right", "Prior", "Next", "Home", "End"):
            return
        self._pending_changes = True
        self._schedule_highlight()

    def _schedule_highlight(self):
        if self._highlight_job:
            self.after_cancel(self._highlight_job)
        self._highlight_job = self.after(250, self.highlight_visible)

    def highlight_visible(self):
        if not self.app.settings.get("highlight_syntax", True):
            return
        if not PYGMENTS_OK:
            return
        try:
            first = int(float(self.index("@0,0")))
            last = int(float(self.index("@0,%d" % self.winfo_height()))) + 2
            for tag in ("keyword", "string", "comment", "number", "function", "class_name", "operator"):
                self.tag_remove(tag, f"{first}.0", f"{last}.0")
            start_idx = f"{first}.0"
            end_idx = f"{last}.0"
            text = self.get(start_idx, end_idx)
            offset = len(self.get("1.0", start_idx))
            lexer = PythonLexer()
            for token_type, value in lex(text, lexer):
                tag = self._get_tag_for_token(token_type)
                if tag:
                    s = self.index(f"{start_idx} + {offset - len(self.get('1.0', start_idx))} chars")
                    e = self.index(f"{s} + {len(value)} chars")
                    self.tag_add(tag, s, e)
                offset += len(value)
        except Exception:
            pass

    def highlight_all(self):
        if not self.app.settings.get("highlight_syntax", True):
            return
        if not PYGMENTS_OK:
            return
        try:
            for tag in ("keyword", "string", "comment", "number", "function", "class_name", "operator"):
                self.tag_remove(tag, "1.0", "end")
            text = self.get("1.0", "end-1c")
            offset = 0
            lexer = PythonLexer()
            for token_type, value in lex(text, lexer):
                tag = self._get_tag_for_token(token_type)
                if tag:
                    s = self.index(f"1.0 + {offset} chars")
                    e = self.index(f"{s} + {len(value)} chars")
                    self.tag_add(tag, s, e)
                offset += len(value)
        except Exception:
            pass

    def _get_tag_for_token(self, token_type):
        if token_type in Token.Keyword:
            return "keyword"
        if token_type in Token.Literal.String:
            return "string"
        if token_type in Token.Comment:
            return "comment"
        if token_type in Token.Literal.Number:
            return "number"
        if token_type in Token.Name.Function:
            return "function"
        if token_type in Token.Name.Class:
            return "class_name"
        if token_type in Token.Operator:
            return "operator"
        return None

    def _on_return(self, event):
        try:
            if not self.app.settings.get("autoindent", True):
                return
            idx = self.index("insert")
            line, col = map(int, idx.split("."))
            current = self.get(f"{line}.0", idx)
            indent = len(current) - len(current.lstrip())
            extra = ""
            stripped = current.rstrip()
            if stripped.endswith(":"):
                extra = " " * self.app.settings.get("tab_size", 4)
            elif stripped.endswith("(") or stripped.endswith("[") or stripped.endswith("{"):
                extra = " " * self.app.settings.get("tab_size", 4)
            self.insert(idx, "\n" + " " * indent + extra)
            self.see("insert")
            return "break"
        except Exception:
            return

    def _on_tab(self, event):
        try:
            sel = self.tag_ranges("sel")
            if sel:
                start = int(float(sel[0]))
                end = int(float(sel[1]))
                for ln in range(start, end + 1):
                    self.insert(f"{ln}.0", " " * self.app.settings.get("tab_size", 4))
            else:
                self.insert("insert", " " * self.app.settings.get("tab_size", 4))
            return "break"
        except Exception:
            return

    def _on_backspace(self, event):
        try:
            idx = self.index("insert")
            line, col = map(int, idx.split("."))
            if col == 0:
                return
            current = self.get(f"{line}.0", idx)
            tab = " " * self.app.settings.get("tab_size", 4)
            if current.endswith(tab):
                self.delete(f"{idx} - {self.app.settings.get('tab_size', 4)} chars", idx)
                return "break"
        except Exception:
            return

    def _select_all(self, event):
        self.tag_add("sel", "1.0", "end-1c")
        return "break"

    def _duplicate_line(self, event):
        try:
            idx = self.index("insert")
            line = int(float(idx))
            text = self.get(f"{line}.0", f"{line+1}.0")
            self.insert(f"{line+1}.0", text)
            return "break"
        except Exception:
            return

    def _toggle_comment(self, event):
        try:
            sel = self.tag_ranges("sel")
            if sel:
                start = int(float(sel[0]))
                end = int(float(sel[1]))
            else:
                start = end = int(float(self.index("insert")))
            for ln in range(start, end + 1):
                line = self.get(f"{ln}.0", f"{ln}.end")
                if line.strip().startswith("#"):
                    pos = line.find("#")
                    self.delete(f"{ln}.{pos}", f"{ln}.{pos+1}")
                else:
                    self.insert(f"{ln}.0", "#")
            return "break"
        except Exception:
            return

    def _insert_bracket_pair(self, pair, event):
        try:
            sel = self.tag_ranges("sel")
            if sel:
                text = self.get(sel[0], sel[1])
                self.delete(sel[0], sel[1])
                self.insert(sel[0], pair[0] + text + pair[1])
                self.mark_set("insert", f"{sel[0]} + {len(pair[0]) + len(text)} chars")
            else:
                self.insert("insert", pair[0] + pair[1])
                self.mark_set("insert", "insert - 1 chars")
            return "break"
        except Exception:
            return

    def _highlight_matching_bracket(self, event=None):
        self.tag_remove("matching_bracket", "1.0", "end")
        try:
            idx = self.index("insert")
            char = self.get(idx)
            pairs = {"(": ")", ")": "(", "[": "]", "]": "[", "{": "}", "}": "{"}
            if char in pairs:
                target = pairs[char]
                direction = 1 if char in "([{" else -1
                depth = 1
                cur = idx
                while True:
                    cur = self.index(f"{cur} + {direction} chars")
                    if self.compare(cur, ">=", "end") or self.compare(cur, "<=", "1.0"):
                        break
                    c = self.get(cur)
                    if c == char:
                        depth += 1
                    elif c == target:
                        depth -= 1
                        if depth == 0:
                            self.tag_add("matching_bracket", cur)
                            self.tag_add("matching_bracket", idx)
                            break
                    elif c in ('"', "'"):
                        # Skip strings naively
                        end = self.search(c, f"{cur} + 1 chars", stopindex="end", regexp=False)
                        if end:
                            cur = end
        except Exception:
            pass

    def _on_click(self, event):
        self.after_idle(self._highlight_current_line)

    def _on_drag(self, event):
        self.after_idle(self._highlight_current_line)

    def _on_scroll(self, event):
        self.after_idle(self._highlight_current_line)

    def _highlight_current_line(self):
        self.tag_remove("current_line", "1.0", "end")
        try:
            line = int(float(self.index("insert")))
            self.tag_add("current_line", f"{line}.0", f"{line+1}.0")
        except Exception:
            pass

    def _on_modified(self, event=None):
        flag = self.tk.call(self._w, "edit", "modified")
        if flag:
            self._modified = True
            self.tk.call(self._w, "edit", "modified", False)
            self.app.update_title()
            self.app.status_bar.set_status("Modifié")

    def is_modified(self):
        return self._modified

    def clear_modified(self):
        self._modified = False
        self.tk.call(self._w, "edit", "modified", False)


class TerminalFrame(ttk.Frame):
    """Terminal série intégré avec historique et envoi de commandes."""

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.theme = app.theme
        self.queue = queue.Queue()
        self.running = False
        self.serial_port = None
        self.reader_thread = None
        self.font = tkfont.Font(family=app.settings.get("font_family", "Consolas"), size=10)
        self._build_ui()
        self._history = app.settings.get("terminal_history", [])
        self._history_index = -1
        self._local_echo = BooleanVar(value=app.settings.get("terminal_echo", True))
        self.after(100, self._process_queue)

    def _build_ui(self):
        # Barre d'outils du terminal
        toolbar = tk.Frame(self, bg=self.theme["bg"], height=32)
        toolbar.pack(fill="x", side="top")
        tk.Label(toolbar, text="PORT:", bg=self.theme["bg"], fg=self.theme["fg"], font=self.font).pack(side="left", padx=4)
        self.port_combo = ttk.Combobox(toolbar, values=[], width=18, state="readonly")
        self.port_combo.pack(side="left", padx=4)
        self.port_combo.bind("<<ComboboxSelected>>", self._on_port_selected)
        tk.Label(toolbar, text="BAUD:", bg=self.theme["bg"], fg=self.theme["fg"], font=self.font).pack(side="left", padx=4)
        self.baud_combo = ttk.Combobox(toolbar, values=DEFAULT_BAUDRATES, width=10, state="readonly")
        self.baud_combo.set(self.app.settings.get("last_baud", "115200"))
        self.baud_combo.pack(side="left", padx=4)
        self.btn_connect = tk.Button(toolbar, text="Connecter", command=self._toggle_connection,
                                     bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                                     activebackground=self.theme["button_active"],
                                     relief="flat", font=self.font, cursor="hand2")
        self.btn_connect.pack(side="left", padx=4)
        tk.Button(toolbar, text="Rafraîchir", command=self.refresh_ports,
                  bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                  activebackground=self.theme["button_active"],
                  relief="flat", font=self.font, cursor="hand2").pack(side="left", padx=4)
        tk.Button(toolbar, text="RESET", command=self._reset_board,
                  bg=self.theme["button_bg"], fg=self.theme["warning"],
                  activebackground=self.theme["button_active"],
                  relief="flat", font=self.font, cursor="hand2").pack(side="left", padx=4)
        tk.Button(toolbar, text="CLEAR", command=self.clear,
                  bg=self.theme["button_bg"], fg=self.theme["info"],
                  activebackground=self.theme["button_active"],
                  relief="flat", font=self.font, cursor="hand2").pack(side="left", padx=4)
        tk.Checkbutton(toolbar, text="Echo", variable=self._local_echo,
                       bg=self.theme["bg"], fg=self.theme["fg"],
                       selectcolor=self.theme["bg"], activebackground=self.theme["bg"],
                       activeforeground=self.theme["fg"], font=self.font).pack(side="left", padx=4)
        # Zone de texte
        self.text = tk.Text(self, wrap="word", state="normal", font=self.font,
                            bg=self.theme["bg"], fg=self.theme["fg"],
                            insertbackground=self.theme["insert"],
                            selectbackground=self.theme["select_bg"],
                            selectforeground=self.theme["select_fg"],
                            relief="flat", padx=6, pady=6)
        self.text.pack(fill="both", expand=True, side="top")
        self.text.tag_configure("sent", foreground=self.theme["info"])
        self.text.tag_configure("error", foreground=self.theme["error"])
        self.text.tag_configure("info", foreground=self.theme["warning"])
        # Entrée commande
        input_frame = tk.Frame(self, bg=self.theme["bg"], height=28)
        input_frame.pack(fill="x", side="bottom")
        tk.Label(input_frame, text=">>", bg=self.theme["bg"], fg=self.theme["accent"], font=self.font).pack(side="left", padx=4)
        self.entry = tk.Entry(input_frame, bg=self.theme["bg"], fg=self.theme["fg"],
                              insertbackground=self.theme["insert"], relief="flat",
                              font=self.font, highlightbackground=self.theme["border"],
                              highlightthickness=1)
        self.entry.pack(fill="x", side="left", expand=True, padx=4, pady=2)
        self.entry.bind("<Return>", self._send_command)
        self.entry.bind("<Up>", self._history_prev)
        self.entry.bind("<Down>", self._history_next)
        self.entry.bind("<Control-c>", lambda e: self._send_ctrl_c())
        self.entry.bind("<Control-C>", lambda e: self._send_ctrl_c())
        self.entry.bind("<Control-d>", lambda e: self._send_ctrl_d())
        self.entry.bind("<Control-D>", lambda e: self._send_ctrl_d())

    def set_theme(self, theme):
        self.theme = theme
        for child in self.winfo_children():
            if isinstance(child, tk.Frame):
                child.config(bg=theme["bg"])
                for c in child.winfo_children():
                    if isinstance(c, (tk.Label, tk.Checkbutton)):
                        c.config(bg=theme["bg"], fg=theme["fg"], selectcolor=theme["bg"],
                                 activebackground=theme["bg"], activeforeground=theme["fg"])
                    elif isinstance(c, tk.Button):
                        c.config(bg=theme["button_bg"], fg=theme["button_fg"],
                                 activebackground=theme["button_active"])
                    elif isinstance(c, tk.Entry):
                        c.config(bg=theme["bg"], fg=theme["fg"], insertbackground=theme["insert"],
                                 highlightbackground=theme["border"])
        self.text.config(bg=theme["bg"], fg=theme["fg"], insertbackground=theme["insert"],
                         selectbackground=theme["select_bg"], selectforeground=theme["select_fg"])
        self.text.tag_configure("sent", foreground=theme["info"])
        self.text.tag_configure("error", foreground=theme["error"])
        self.text.tag_configure("info", foreground=theme["warning"])

    def refresh_ports(self):
        ports = list(serial.tools.list_ports.comports())
        esp_ports = [p for p in ports if is_esp32_port(p)]
        other_ports = [p for p in ports if not is_esp32_port(p)]
        values = []
        for p in esp_ports:
            values.append(f"{p.device} | {p.description} (ESP32?)")
        for p in other_ports:
            values.append(f"{p.device} | {p.description}")
        self.port_combo["values"] = values
        if values:
            saved = self.app.settings.get("last_port", "")
            for i, v in enumerate(values):
                if saved and v.startswith(saved):
                    self.port_combo.current(i)
                    break
            else:
                self.port_combo.current(0)
        return ports

    def _on_port_selected(self, event=None):
        text = self.port_combo.get()
        if " | " in text:
            port = text.split(" | ")[0]
            self.app.settings.set("last_port", port)

    def _toggle_connection(self):
        if self.serial_port and self.serial_port.is_open:
            self.disconnect()
        else:
            self.connect()

    def connect(self):
        text = self.port_combo.get()
        if not text:
            self.app.logger.warn("Aucun port sélectionné.")
            return
        port = text.split(" | ")[0]
        baud = int(self.baud_combo.get())
        try:
            self.serial_port = serial.Serial(port, baud, timeout=0.05)
            self.running = True
            self.reader_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.reader_thread.start()
            self.btn_connect.config(text="Déconnecter", fg=self.theme["error"])
            self.app.status_bar.set_status(f"Connecté à {port} @ {baud} bauds")
            self.app.logger.success(f"Connecté à {port} @ {baud} bauds")
        except Exception as e:
            self.app.logger.error(f"Échec connexion {port}: {e}")
            messagebox.showerror("Erreur connexion", str(e))

    def disconnect(self):
        self.running = False
        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
        except Exception:
            pass
        self.serial_port = None
        self.btn_connect.config(text="Connecter", fg=self.theme["button_fg"])
        self.app.status_bar.set_status("Déconnecté")
        self.app.logger.info("Port série déconnecté")

    def _read_loop(self):
        while self.running and self.serial_port and self.serial_port.is_open:
            try:
                data = self.serial_port.read(self.serial_port.in_waiting or 1)
                if data:
                    self.queue.put(("data", data))
            except Exception as e:
                self.queue.put(("error", str(e)))
                break

    def _process_queue(self):
        while not self.queue.empty():
            kind, value = self.queue.get()
            if kind == "data":
                self.append(value.decode("utf-8", errors="replace"))
            elif kind == "error":
                self.append(f"[ERREUR SÉRIE] {value}\n", "error")
                self.disconnect()
        self.after(50, self._process_queue)

    def append(self, text, tag=None):
        self.text.config(state="normal")
        self.text.insert("end", text, tag)
        self.text.see("end")
        self.text.config(state="disabled")

    def clear(self):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.config(state="disabled")

    def _send_command(self, event=None):
        cmd = self.entry.get()
        if not cmd:
            return
        self.entry.delete(0, "end")
        self.append(f">> {cmd}\n", "sent")
        self._add_history(cmd)
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.write((cmd + "\r\n").encode("utf-8"))
            except Exception as e:
                self.append(f"[ERREUR ENVOI] {e}\n", "error")
        else:
            self.append("[Non connecté]\n", "error")

    def _add_history(self, cmd):
        if cmd in self._history:
            self._history.remove(cmd)
        self._history.insert(0, cmd)
        self._history = self._history[:HISTORY_LIMIT]
        self._history_index = -1
        self.app.settings.set("terminal_history", self._history)

    def _history_prev(self, event):
        if self._history:
            self._history_index = min(self._history_index + 1, len(self._history) - 1)
            self.entry.delete(0, "end")
            self.entry.insert(0, self._history[self._history_index])
        return "break"

    def _history_next(self, event):
        if self._history_index > 0:
            self._history_index -= 1
            self.entry.delete(0, "end")
            self.entry.insert(0, self._history[self._history_index])
        elif self._history_index == 0:
            self._history_index = -1
            self.entry.delete(0, "end")
        return "break"

    def _send_ctrl_c(self):
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.write(b"\x03")
                self.append("[CTRL+C envoyé]\n", "info")
            except Exception as e:
                self.append(f"[ERREUR] {e}\n", "error")
        return "break"

    def _send_ctrl_d(self):
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.write(b"\x04")
                self.append("[CTRL+D envoyé]\n", "info")
            except Exception as e:
                self.append(f"[ERREUR] {e}\n", "error")
        return "break"

    def _reset_board(self):
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.setDTR(False)
                self.serial_port.setRTS(True)
                time.sleep(0.1)
                self.serial_port.setRTS(False)
                self.append("[RESET matériel envoyé]\n", "info")
            except Exception as e:
                self.append(f"[ERREUR RESET] {e}\n", "error")
        else:
            self.append("[Non connecté]\n", "error")

    def send_raw(self, data):
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.write(data)
            except Exception as e:
                self.append(f"[ERREUR] {e}\n", "error")

    def send_line(self, line):
        self.send_raw((line + "\r\n").encode("utf-8"))

    def is_connected(self):
        return self.serial_port is not None and self.serial_port.is_open


class StatusBar(tk.Frame):
    """Barre de statut affichant les informations contextuelles."""

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.theme = app.theme
        self.config(bg=self.theme["bg"], height=24)
        self._build_ui()

    def _build_ui(self):
        self.lbl_status = tk.Label(self, text="Prêt", bg=self.theme["bg"], fg=self.theme["fg"],
                                   font=(self.app.settings.get("font_family", "Consolas"), 10))
        self.lbl_status.pack(side="left", padx=6)
        self.lbl_position = tk.Label(self, text="Ln 1, Col 1", bg=self.theme["bg"], fg=self.theme["fg"],
                                     font=(self.app.settings.get("font_family", "Consolas"), 10))
        self.lbl_position.pack(side="right", padx=6)
        self.lbl_encoding = tk.Label(self, text="UTF-8", bg=self.theme["bg"], fg=self.theme["fg"],
                                     font=(self.app.settings.get("font_family", "Consolas"), 10))
        self.lbl_encoding.pack(side="right", padx=6)
        self.lbl_port = tk.Label(self, text="Aucun port", bg=self.theme["bg"], fg=self.theme["line_fg"],
                                 font=(self.app.settings.get("font_family", "Consolas"), 10))
        self.lbl_port.pack(side="right", padx=6)

    def set_theme(self, theme):
        self.theme = theme
        self.config(bg=theme["bg"])
        for w in self.winfo_children():
            w.config(bg=theme["bg"], fg=theme["fg"])

    def set_status(self, text):
        self.lbl_status.config(text=text)

    def set_position(self, text):
        self.lbl_position.config(text=text)

    def set_port(self, text):
        self.lbl_port.config(text=text)


class FileBrowser(ttk.Frame):
    """Explorateur de fichiers local simple."""

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.theme = app.theme
        self.current_path = Path.home()
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        self.tree = ttk.Treeview(self, columns=("size", "modified"), show="tree headings")
        self.tree.heading("#0", text="Fichier")
        self.tree.heading("size", text="Taille")
        self.tree.heading("modified", text="Modifié")
        self.tree.column("#0", width=200)
        self.tree.column("size", width=80)
        self.tree.column("modified", width=120)
        self.tree.pack(fill="both", expand=True, side="top")
        self.tree.bind("<Double-1>", self._on_double)
        toolbar = tk.Frame(self, bg=self.theme["bg"], height=28)
        toolbar.pack(fill="x", side="bottom")
        tk.Button(toolbar, text="↑", command=self._go_up,
                  bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                  activebackground=self.theme["button_active"],
                  relief="flat", cursor="hand2").pack(side="left", padx=2)
        tk.Button(toolbar, text="🗀", command=self._choose_dir,
                  bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                  activebackground=self.theme["button_active"],
                  relief="flat", cursor="hand2").pack(side="left", padx=2)
        tk.Button(toolbar, text="↻", command=self.refresh,
                  bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                  activebackground=self.theme["button_active"],
                  relief="flat", cursor="hand2").pack(side="left", padx=2)

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            self.tree.insert("", "end", text="..", values=("", "", "DIR"), open=False)
            for entry in sorted(self.current_path.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower())):
                try:
                    stat = entry.stat()
                    size = format_size(stat.st_size) if entry.is_file() else ""
                    mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                    kind = "DIR" if entry.is_dir() else "FILE"
                    self.tree.insert("", "end", text=entry.name, values=(size, mtime, kind))
                except Exception:
                    pass
        except Exception:
            pass

    def _on_double(self, event):
        item = self.tree.selection()[0]
        vals = self.tree.item(item, "values")
        text = self.tree.item(item, "text")
        if text == "..":
            self.current_path = self.current_path.parent
            self.refresh()
        elif vals and vals[2] == "DIR":
            self.current_path = self.current_path / text
            self.refresh()
        elif vals and vals[2] == "FILE":
            self.app.open_file(self.current_path / text)

    def _go_up(self):
        self.current_path = self.current_path.parent
        self.refresh()

    def _choose_dir(self):
        d = filedialog.askdirectory()
        if d:
            self.current_path = Path(d)
            self.refresh()


# ═══════════════════════════════════════════════════════════════════════════════
# GESTION ESP32
# ═══════════════════════════════════════════════════════════════════════════════

class ESP32Manager:
    """Fournit les opérations de flash, upload, download, filesystem, etc."""

    def __init__(self, app):
        self.app = app
        self.logger = app.logger

    def get_port(self):
        return self.app.terminal.port_combo.get().split(" | ")[0] if self.app.terminal.port_combo.get() else None

    def run_esptool(self, args, callback=None):
        port = self.get_port()
        if not port:
            self.logger.error("Aucun port ESP32 sélectionné.")
            return False
        full_args = ["--port", port] + args
        def worker():
            try:
                if ESPTOOL_OK:
                    old_argv = sys.argv
                    sys.argv = ["esptool"] + full_args
                    esptool.main()
                    sys.argv = old_argv
                else:
                    cmd = ["esptool.py"] + full_args
                    subprocess.run(cmd, check=True)
                if callback:
                    self.app.after(0, callback, True, "")
            except Exception as e:
                if callback:
                    self.app.after(0, callback, False, str(e))
        threading.Thread(target=worker, daemon=True).start()
        return True

    def flash_firmware(self, firmware_path, callback=None):
        if not firmware_path or not os.path.exists(firmware_path):
            self.logger.error("Chemin de firmware invalide.")
            return False
        args = ["--baud", "921600", "write_flash", "-z", "0x1000", firmware_path]
        return self.run_esptool(args, callback)

    def erase_flash(self, callback=None):
        args = ["erase_flash"]
        return self.run_esptool(args, callback)

    def chip_id(self, callback=None):
        args = ["chip_id"]
        return self.run_esptool(args, callback)

    def upload_with_ampy(self, local_path, remote_path=None, callback=None):
        port = self.get_port()
        if not port:
            self.logger.error("Aucun port sélectionné.")
            return False
        if remote_path is None:
            remote_path = os.path.basename(local_path)
        def worker():
            try:
                if not AMPY_OK:
                    subprocess.run(["ampy", "--port", port, "put", local_path, remote_path], check=True)
                else:
                    board = ampy_pyboard.Pyboard(port)
                    fs = ampy_files.Files(board)
                    with open(local_path, "rb") as f:
                        data = f.read()
                    fs.put(remote_path, data)
                if callback:
                    self.app.after(0, callback, True, "")
            except Exception as e:
                if callback:
                    self.app.after(0, callback, False, str(e))
        threading.Thread(target=worker, daemon=True).start()
        return True

    def run_with_mpremote(self, args, callback=None):
        port = self.get_port()
        if not port:
            self.logger.error("Aucun port sélectionné.")
            return False
        def worker():
            try:
                if MPREMOTE_OK:
                    import mpremote.main as mp_main
                    old_argv = sys.argv
                    sys.argv = ["mpremote"] + ["connect", port] + args
                    mp_main.main()
                    sys.argv = old_argv
                else:
                    subprocess.run(["mpremote", "connect", port] + args, check=True)
                if callback:
                    self.app.after(0, callback, True, "")
            except Exception as e:
                if callback:
                    self.app.after(0, callback, False, str(e))
        threading.Thread(target=worker, daemon=True).start()
        return True

    def run_code_on_board(self, code, callback=None):
        port = self.get_port()
        if not port:
            self.logger.error("Aucun port sélectionné.")
            return False
        tmp_path = None
        try:
            fd, tmp_path = tempfile.mkstemp(suffix=".py")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(code)
            def worker():
                try:
                    if MPREMOTE_OK:
                        import mpremote.main as mp_main
                        old_argv = sys.argv
                        sys.argv = ["mpremote", "connect", port, "run", tmp_path]
                        mp_main.main()
                        sys.argv = old_argv
                    else:
                        subprocess.run(["mpremote", "connect", port, "run", tmp_path], check=True)
                    if callback:
                        self.app.after(0, callback, True, "")
                except Exception as e:
                    if callback:
                        self.app.after(0, callback, False, str(e))
                finally:
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass
            threading.Thread(target=worker, daemon=True).start()
            return True
        except Exception as e:
            self.logger.error(f"Erreur préparation exécution: {e}")
            return False

    def list_files(self, callback=None):
        return self.run_with_mpremote(["fs", "ls"], callback)

    def get_file(self, remote_path, local_path, callback=None):
        return self.run_with_mpremote(["fs", "cp", f":{remote_path}", local_path], callback)

    def put_file(self, local_path, remote_path=None, callback=None):
        if remote_path is None:
            remote_path = os.path.basename(local_path)
        return self.run_with_mpremote(["fs", "cp", local_path, f":{remote_path}"], callback)

    def remove_file(self, remote_path, callback=None):
        return self.run_with_mpremote(["fs", "rm", remote_path], callback)

    def mkdir(self, remote_path, callback=None):
        return self.run_with_mpremote(["fs", "mkdir", remote_path], callback)

    def rmdir(self, remote_path, callback=None):
        return self.run_with_mpremote(["fs", "rmdir", remote_path], callback)

    def repl(self):
        port = self.get_port()
        if not port:
            self.logger.error("Aucun port sélectionné.")
            return
        if self.app.terminal.is_connected():
            self.logger.info("REPL déjà accessible via le terminal intégré.")
            return
        try:
            subprocess.Popen(["mpremote", "connect", port, "repl"],
                             creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0))
        except Exception as e:
            self.logger.error(f"Impossible d'ouvrir le REPL externe: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# APPLICATION PRINCIPALE
# ═══════════════════════════════════════════════════════════════════════════════

class SerialTerminal:
    """Gestion du port série, lecture en thread séparé et envoi de commandes."""

    def __init__(self, app):
        self.app = app
        self.settings = app.settings
        self.logger = app.logger
        self.serial_port = None
        self.read_thread = None
        self.running = False
        self.port_combo = None
        self.baud_combo = None
        self.connect_btn = None
        self.input_var = StringVar()
        self._history = []
        self._history_index = 0
        self._rx_queue = queue.Queue()

    def build_ui(self, parent):
        frame = tk.LabelFrame(parent, text="Terminal / Logs", bg=self.app.theme["bg"],
                              fg=self.app.theme["fg"], relief="flat", bd=1)
        frame.pack(fill="both", expand=True)
        top = tk.Frame(frame, bg=self.app.theme["bg"])
        top.pack(fill="x", padx=4, pady=2)
        self.port_combo = ttk.Combobox(top, state="readonly", width=28)
        self.port_combo.pack(side="left", padx=2)
        self.baud_combo = ttk.Combobox(top, values=DEFAULT_BAUDRATES, state="readonly", width=10)
        self.baud_combo.set(self.settings.get("last_baud", "115200"))
        self.baud_combo.pack(side="left", padx=2)
        self.connect_btn = tk.Button(top, text="Connecter", command=self._toggle_connection,
                                     bg=self.app.theme["button_bg"], fg=self.app.theme["button_fg"],
                                     activebackground=self.app.theme["button_active"], relief="flat")
        self.connect_btn.pack(side="left", padx=2)
        tk.Button(top, text="Rafraîchir", command=lambda: self.refresh_ports(),
                  bg=self.app.theme["button_bg"], fg=self.app.theme["button_fg"],
                  activebackground=self.app.theme["button_active"], relief="flat").pack(side="left", padx=2)
        tk.Button(top, text="STOP (Ctrl+C)", command=self._send_ctrl_c,
                  bg=self.app.theme["button_bg"], fg=self.app.theme["error"],
                  activebackground=self.app.theme["button_active"], relief="flat").pack(side="left", padx=2)
        self.output = tk.Text(frame, wrap="word", state="disabled", height=10,
                              bg=self.app.theme["bg"], fg=self.app.theme["fg"],
                              insertbackground=self.app.theme["insert"],
                              font=(self.settings.get("font_family", "Consolas"), 10),
                              relief="flat")
        self.output.pack(fill="both", expand=True, padx=4, pady=2)
        scroll = tk.Scrollbar(self.output, command=self.output.yview, orient="vertical",
                              bg=self.app.theme["bg"], troughcolor=self.app.theme["bg"])
        self.output.config(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        input_frame = tk.Frame(frame, bg=self.app.theme["bg"])
        input_frame.pack(fill="x", padx=4, pady=2)
        self.input_entry = tk.Entry(input_frame, textvariable=self.input_var,
                                    bg=self.app.theme["bg"], fg=self.app.theme["fg"],
                                    insertbackground=self.app.theme["insert"], relief="flat",
                                    highlightbackground=self.app.theme["border"], highlightthickness=1)
        self.input_entry.pack(side="left", fill="x", expand=True, padx=2)
        self.input_entry.bind("<Return>", self._send_input)
        self.input_entry.bind("<Up>", self._history_up)
        self.input_entry.bind("<Down>", self._history_down)
        tk.Button(input_frame, text="Envoyer", command=self._send_input,
                  bg=self.app.theme["button_bg"], fg=self.app.theme["button_fg"],
                  activebackground=self.app.theme["button_active"], relief="flat").pack(side="left", padx=2)
        self.refresh_ports()
        self._poll_rx()

    def set_theme(self, theme):
        self.output.config(bg=theme["bg"], fg=theme["fg"], insertbackground=theme["insert"])
        self.input_entry.config(bg=theme["bg"], fg=theme["fg"], insertbackground=theme["insert"],
                                highlightbackground=theme["border"])

    def refresh_ports(self):
        ports = list(serial.tools.list_ports.comports())
        items = []
        selected = None
        for p in ports:
            label = f"{p.device} | {p.description or 'Unknown'}"
            items.append(label)
            if is_esp32_port(p):
                selected = label
        self.port_combo.config(values=items)
        if selected:
            self.port_combo.set(selected)
        elif items:
            self.port_combo.current(0)
        else:
            self.port_combo.set("")
        return ports

    def get_current_port(self):
        val = self.port_combo.get()
        return val.split(" | ")[0] if val else ""

    def _toggle_connection(self):
        if self.serial_port and self.serial_port.is_open:
            self.disconnect()
        else:
            self.connect()

    def connect(self):
        port = self.get_current_port()
        if not port:
            self.logger.warn("Aucun port sélectionné.")
            return
        baud = self.baud_combo.get()
        try:
            self.serial_port = serial.Serial(port, int(baud), timeout=0.1)
            self.running = True
            self.read_thread = threading.Thread(target=self._reader_loop, daemon=True)
            self.read_thread.start()
            if self.connect_btn:
                self.connect_btn.config(text="Déconnecter")
            self.app.status_bar.set_connection("Connecté")
            self.logger.success(f"Connecté à {port} @ {baud}")
        except Exception as e:
            self.logger.error(f"Connexion échouée: {e}")

    def disconnect(self):
        self.running = False
        try:
            if self.serial_port:
                self.serial_port.close()
        except Exception:
            pass
        self.serial_port = None
        if self.connect_btn:
            self.connect_btn.config(text="Connecter")
        self.app.status_bar.set_connection("Déconnecté")
        self.logger.info("Déconnecté.")

    def _reader_loop(self):
        while self.running and self.serial_port and self.serial_port.is_open:
            try:
                data = self.serial_port.read(self.serial_port.in_waiting or 1)
                if data:
                    self._rx_queue.put(data)
            except Exception:
                break

    def _poll_rx(self):
        try:
            while True:
                data = self._rx_queue.get_nowait()
                text = data.decode("utf-8", errors="replace")
                self._append_output(text)
        except queue.Empty:
            pass
        self.app.after(50, self._poll_rx)

    def _append_output(self, text):
        self.output.config(state="normal")
        self.output.insert("end", text)
        self.output.see("end")
        self.output.config(state="disabled")

    def send_raw(self, data):
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.write(data)
                return True
            except Exception as e:
                self.logger.error(f"Erreur envoi série: {e}")
        return False

    def _send_input(self, event=None):
        cmd = self.input_var.get()
        if not cmd:
            return
        self._history.append(cmd)
        self._history = self._history[-HISTORY_LIMIT:]
        self._history_index = len(self._history)
        self.input_var.set("")
        self._append_output(f">>> {cmd}\n")
        self.send_raw((cmd + "\r\n").encode("utf-8"))

    def _history_up(self, event):
        if self._history and self._history_index > 0:
            self._history_index -= 1
            self.input_var.set(self._history[self._history_index])
        return "break"

    def _history_down(self, event):
        if self._history and self._history_index < len(self._history) - 1:
            self._history_index += 1
            self.input_var.set(self._history[self._history_index])
        else:
            self._history_index = len(self._history)
            self.input_var.set("")
        return "break"

    def _send_ctrl_c(self):
        if self.send_raw(b"\x03"):
            self.logger.info("Signal d'arrêt envoyé (Ctrl+C).")


class ESP32Manager:
    """Opérations avancées sur l'ESP32 : exécution, fichiers, firmware."""

    def __init__(self, terminal, logger):
        self.terminal = terminal
        self.logger = logger
        self._op_thread = None

    def _ensure_port(self):
        if not self.terminal.serial_port or not self.terminal.serial_port.is_open:
            self.terminal.connect()
        return bool(self.terminal.serial_port and self.terminal.serial_port.is_open)

    def _exec(self, func, callback):
        def wrapper():
            try:
                ok, err = func(), None
                callback(True, None)
            except Exception as e:
                callback(False, str(e))
        self._op_thread = threading.Thread(target=wrapper, daemon=True)
        self._op_thread.start()

    def run_code_on_board(self, code, callback):
        def op():
            if not self._ensure_port():
                raise RuntimeError("Pas de connexion série.")
            payload = code + "\r\n"
            self.terminal.send_raw(payload.encode("utf-8"))
            return True
        self._exec(op, callback)

    def put_file(self, local_path, remote_path, callback):
        def op():
            if MPREMOTE_OK:
                cmd = ["mpremote", "connect", self.terminal.get_current_port(), "fs", "cp", local_path, ":" + remote_path]
                subprocess.run(cmd, check=True)
                return True
            elif AMPY_OK:
                board = ampy_pyboard.Pyboard(self.terminal.get_current_port())
                fs = ampy_files.Files(board)
                fs.put(local_path, remote_path)
                return True
            raise RuntimeError("ampy ou mpremote requis pour l'upload.")
        self._exec(op, callback)

    def get_file(self, remote_path, local_path, callback):
        def op():
            if MPREMOTE_OK:
                cmd = ["mpremote", "connect", self.terminal.get_current_port(), "fs", "cp", ":" + remote_path, local_path]
                subprocess.run(cmd, check=True)
                return True
            elif AMPY_OK:
                board = ampy_pyboard.Pyboard(self.terminal.get_current_port())
                fs = ampy_files.Files(board)
                fs.get(remote_path, local_path)
                return True
            raise RuntimeError("ampy ou mpremote requis pour le download.")
        self._exec(op, callback)

    def list_files(self, callback):
        def op():
            if MPREMOTE_OK:
                cmd = ["mpremote", "connect", self.terminal.get_current_port(), "fs", "ls"]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                self.logger.info("Fichiers sur l'ESP32:\n" + result.stdout)
                return True
            elif AMPY_OK:
                board = ampy_pyboard.Pyboard(self.terminal.get_current_port())
                fs = ampy_files.Files(board)
                files = fs.ls()
                self.logger.info("Fichiers sur l'ESP32:\n" + "\n".join(files))
                return True
            raise RuntimeError("ampy ou mpremote requis pour lister les fichiers.")
        self._exec(op, callback)

    def erase_flash(self, callback):
        def op():
            port = self.terminal.get_current_port()
            if ESPTOOL_OK:
                cmd = ["esptool.py", "--port", port, "erase_flash"]
                subprocess.run(cmd, check=True)
                return True
            raise RuntimeError("esptool requis pour effacer la flash.")
        self._exec(op, callback)

    def flash_firmware(self, firmware_path, callback):
        def op():
            port = self.terminal.get_current_port()
            if ESPTOOL_OK:
                cmd = ["esptool.py", "--port", port, "--baud", self.terminal.baud_combo.get(),
                       "write_flash", "0x1000", firmware_path]
                subprocess.run(cmd, check=True)
                return True
            raise RuntimeError("esptool requis pour flasher.")
        self._exec(op, callback)


class StatusBar(tk.Frame):
    """Barre d'état affichant port, position, connexion et messages."""

    def __init__(self, parent, theme):
        super().__init__(parent, bg=theme["bg"], relief="flat", bd=1)
        self.theme = theme
        self.port_lbl = tk.Label(self, text="Port: --", bg=theme["bg"], fg=theme["fg"],
                                 font=("Consolas", 9))
        self.port_lbl.pack(side="left", padx=6)
        self.pos_lbl = tk.Label(self, text="Ln 1, Col 0", bg=theme["bg"], fg=theme["fg"],
                                font=("Consolas", 9))
        self.pos_lbl.pack(side="left", padx=6)
        self.conn_lbl = tk.Label(self, text="Déconnecté", bg=theme["bg"], fg=theme["error"],
                                 font=("Consolas", 9))
        self.conn_lbl.pack(side="right", padx=6)
        self.msg_lbl = tk.Label(self, text="Prêt", bg=theme["bg"], fg=theme["info"],
                                font=("Consolas", 9))
        self.msg_lbl.pack(side="right", padx=6)

    def set_theme(self, theme):
        self.theme = theme
        self.config(bg=theme["bg"])
        for w in (self.port_lbl, self.pos_lbl, self.conn_lbl, self.msg_lbl):
            w.config(bg=theme["bg"], fg=theme["fg"])
        self.conn_lbl.config(fg=theme["error"])
        self.msg_lbl.config(fg=theme["info"])

    def set_port(self, text):
        self.port_lbl.config(text=f"Port: {text}")

    def set_position(self, text):
        self.pos_lbl.config(text=text)

    def set_connection(self, text):
        self.conn_lbl.config(text=text)
        self.conn_lbl.config(fg=self.theme["accent"] if text == "Connecté" else self.theme["error"])

    def set_message(self, text):
        self.msg_lbl.config(text=text)


class HackerESP32IDE(tk.Tk):
    """Application IDE complète pour ESP32 / MicroPython."""

    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} v{APP_VERSION} — {APP_AUTHOR} {APP_DATE}")
        self.settings = SettingsManager()
        self.theme = THEMES[self.settings.get("theme", DEFAULT_THEME)]
        self.logger = Logger(self)
        self.esp32 = ESP32Manager(self)
        self.current_file = None
        self.file_browser = None
        self.find_bar = None
        self._auto_save_job = None
        self._port_watcher_job = None
        self._last_ports_hash = ""
        self._log_lines = []
        self._clipboard = []
        self._build_ui()
        self._apply_theme()
        self._bind_global_shortcuts()
        self._start_auto_save()
        self._start_port_watcher()
        self._load_startup()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ─────────────────────────── Construction UI ────────────────────────────

    def _build_ui(self):
        self.geometry(self.settings.get("window_geometry", "1400x900+50+30"))
        self.minsize(900, 600)
        self.configure(bg=self.theme["bg"])
        # Icône
        try:
            self.iconbitmap(default="")
        except Exception:
            pass
        # Menu
        self._build_menu()
        # Toolbar
        self.toolbar = self._build_toolbar()
        # Paned principal
        self.paned = tk.PanedWindow(self, orient="horizontal", sashrelief="flat", sashwidth=4, bg=self.theme["border"])
        self.paned.pack(fill="both", expand=True, padx=2, pady=2)
        # Sidebar
        self.sidebar = tk.Frame(self.paned, bg=self.theme["bg"], width=220)
        self.paned.add(self.sidebar, minsize=180)
        self._build_sidebar()
        # Zone éditeur + terminal
        self.right_pane = tk.PanedWindow(self.paned, orient="vertical", sashrelief="flat", sashwidth=4, bg=self.theme["border"])
        self.paned.add(self.right_pane, minsize=400)
        # Éditeur
        self.editor_frame = tk.Frame(self.right_pane, bg=self.theme["bg"])
        self.right_pane.add(self.editor_frame, minsize=300)
        self._build_editor()
        # Terminal
        self.terminal = TerminalFrame(self.right_pane, self, relief="flat", borderwidth=0)
        self.right_pane.add(self.terminal, minsize=200)
        # Log panel
        self.log_frame = tk.Frame(self, bg=self.theme["bg"], height=120)
        self.log_text = tk.Text(self.log_frame, wrap="word", state="disabled", height=6,
                                bg=self.theme["bg"], fg=self.theme["fg"],
                                insertbackground=self.theme["insert"],
                                font=(self.settings.get("font_family", "Consolas"), 9),
                                relief="flat")
        self.log_text.pack(fill="both", expand=True)
        self.log_frame.pack(fill="x", side="bottom")
        # Status bar
        self.status_bar = StatusBar(self, self)
        self.status_bar.pack(fill="x", side="bottom")
        # Position updater
        self.editor.bind("<KeyRelease>", self._update_position, add="+")
        self.editor.bind("<Button-1>", self._update_position, add="+")
        self.after(100, self._update_position)

    def _build_menu(self):
        menubar = Menu(self, bg=self.theme["bg"], fg=self.theme["fg"],
                       activebackground=self.theme["select_bg"],
                       activeforeground=self.theme["select_fg"])
        # Fichier
        file_menu = Menu(menubar, tearoff=0, bg=self.theme["bg"], fg=self.theme["fg"],
                         activebackground=self.theme["select_bg"])
        file_menu.add_command(label="Nouveau (Ctrl+N)", command=self.new_file)
        file_menu.add_command(label="Ouvrir... (Ctrl+O)", command=self.open_file_dialog)
        file_menu.add_command(label="Enregistrer (Ctrl+S)", command=self.save_file)
        file_menu.add_command(label="Enregistrer sous... (Ctrl+Maj+S)", command=self.save_file_as)
        file_menu.add_separator()
        self.recent_menu = Menu(file_menu, tearoff=0, bg=self.theme["bg"], fg=self.theme["fg"])
        file_menu.add_cascade(label="Fichiers récents", menu=self.recent_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter (Alt+F4)", command=self._on_close)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        # Édition
        edit_menu = Menu(menubar, tearoff=0, bg=self.theme["bg"], fg=self.theme["fg"])
        edit_menu.add_command(label="Annuler (Ctrl+Z)", command=self._undo)
        edit_menu.add_command(label="Rétablir (Ctrl+Y)", command=self._redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Couper (Ctrl+X)", command=self._cut)
        edit_menu.add_command(label="Copier (Ctrl+C)", command=self._copy)
        edit_menu.add_command(label="Coller (Ctrl+V)", command=self._paste)
        edit_menu.add_separator()
        edit_menu.add_command(label="Rechercher (Ctrl+F)", command=self.show_find_bar)
        edit_menu.add_command(label="Aller à la ligne (Ctrl+G)", command=self.show_goto_line)
        menubar.add_cascade(label="Édition", menu=edit_menu)
        # Affichage
        view_menu = Menu(menubar, tearoff=0, bg=self.theme["bg"], fg=self.theme["fg"])
        self.var_show_line_numbers = BooleanVar(value=self.settings.get("show_line_numbers", True))
        view_menu.add_checkbutton(label="Numéros de ligne", variable=self.var_show_line_numbers,
                                  command=self._toggle_line_numbers)
        self.var_word_wrap = BooleanVar(value=self.settings.get("word_wrap", False))
        view_menu.add_checkbutton(label="Retour à la ligne", variable=self.var_word_wrap,
                                  command=self._toggle_word_wrap)
        view_menu.add_separator()
        self.var_toolbar = BooleanVar(value=self.settings.get("toolbar_visible", True))
        view_menu.add_checkbutton(label="Barre d'outils", variable=self.var_toolbar,
                                  command=self._toggle_toolbar)
        self.var_statusbar = BooleanVar(value=self.settings.get("statusbar_visible", True))
        view_menu.add_checkbutton(label="Barre de statut", variable=self.var_statusbar,
                                  command=self._toggle_statusbar)
        view_menu.add_separator()
        theme_menu = Menu(view_menu, tearoff=0, bg=self.theme["bg"], fg=self.theme["fg"])
        for theme_name in THEMES:
            theme_menu.add_command(label=theme_name.capitalize(),
                                   command=lambda t=theme_name: self.set_theme(t))
        view_menu.add_cascade(label="Thème", menu=theme_menu)
        menubar.add_cascade(label="Affichage", menu=view_menu)
        # ESP32
        esp_menu = Menu(menubar, tearoff=0, bg=self.theme["bg"], fg=self.theme["fg"])
        esp_menu.add_command(label="Détecter les ports", command=self._detect_ports)
        esp_menu.add_command(label="Connecter/Déconnecter", command=self.terminal._toggle_connection)
        esp_menu.add_separator()
        esp_menu.add_command(label="Exécuter sur ESP32 (F5)", command=self.run_on_esp32)
        esp_menu.add_command(label="Exécuter sélection (F6)", command=self.run_selection_on_esp32)
        esp_menu.add_command(label="Téléverser fichier (F7)", command=self.upload_current_file)
        esp_menu.add_command(label="Télécharger fichier", command=self.download_file_from_esp32)
        esp_menu.add_separator()
        esp_menu.add_command(label="Lister fichiers sur ESP32", command=self.list_esp32_files)
        esp_menu.add_command(label="Effacer flash", command=self.erase_flash_dialog)
        esp_menu.add_command(label="Flasher firmware", command=self.flash_firmware_dialog)
        esp_menu.add_command(label="REPL externe", command=self.esp32.repl)
        menubar.add_cascade(label="ESP32", menu=esp_menu)
        # Outils
        tools_menu = Menu(menubar, tearoff=0, bg=self.theme["bg"], fg=self.theme["fg"])
        tools_menu.add_command(label="Nouveau projet template", command=self._new_project_template)
        tools_menu.add_command(label="Analyser code", command=self._analyze_code)
        tools_menu.add_command(label="Formater code", command=self._format_code)
        tools_menu.add_command(label="Minifier code", command=self._minify_code)
        tools_menu.add_separator()
        tools_menu.add_command(label="Préférences", command=self._show_preferences)
        tools_menu.add_command(label="Raccourcis clavier", command=self._show_shortcuts)
        menubar.add_cascade(label="Outils", menu=tools_menu)
        # Aide
        help_menu = Menu(menubar, tearoff=0, bg=self.theme["bg"], fg=self.theme["fg"])
        help_menu.add_command(label="Documentation MicroPython", command=lambda: webbrowser.open("https://docs.micropython.org"))
        help_menu.add_command(label="Documentation ESP32", command=lambda: webbrowser.open("https://docs.espressif.com"))
        help_menu.add_command(label="GitHub esptool", command=lambda: webbrowser.open("https://github.com/espressif/esptool"))
        help_menu.add_command(label="À propos", command=self._show_about)
        menubar.add_cascade(label="Aide", menu=help_menu)
        self.config(menu=menubar)
        self.menubar = menubar

    def _build_toolbar(self):
        toolbar = tk.Frame(self, bg=self.theme["bg"], height=42)
        toolbar.pack(fill="x", side="top")
        buttons = [
            ("Nouveau", self.new_file),
            ("Ouvrir", self.open_file_dialog),
            ("Sauver", self.save_file),
            ("▶ Run", self.run_on_esp32),
            ("⏹ Stop", self._send_stop),
            ("⬆ Upload", self.upload_current_file),
            ("⬇ Download", self.download_file_from_esp32),
            ("🔄 Ports", self._detect_ports),
            ("⚙ Préf.", self._show_preferences),
        ]
        for label, cmd in buttons:
            btn = tk.Button(toolbar, text=label, command=cmd,
                            bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                            activebackground=self.theme["button_active"],
                            activeforeground=self.theme["button_fg"],
                            relief="flat", font=(self.settings.get("font_family", "Consolas"), 10),
                            cursor="hand2")
            btn.pack(side="left", padx=2, pady=4)
        return toolbar

    def _build_sidebar(self):
        # Onglets: Fichiers / Projets / Snippets
        self.notebook = ttk.Notebook(self.sidebar)
        self.notebook.pack(fill="both", expand=True)
        self.file_browser = FileBrowser(self.notebook, self)
        self.notebook.add(self.file_browser, text="Fichiers")
        self.snippets_frame = tk.Frame(self.notebook, bg=self.theme["bg"])
        self.notebook.add(self.snippets_frame, text="Snippets")
        self._build_snippets()
        self.info_frame = tk.Frame(self.notebook, bg=self.theme["bg"])
        self.notebook.add(self.info_frame, text="Infos")
        self._build_info_panel()

    def _build_snippets(self):
        snippets = {
            "Blink LED": "from machine import Pin\nimport time\nled = Pin(2, Pin.OUT)\nwhile True:\n    led.toggle()\n    time.sleep(0.5)",
            "WiFi connect": "import network\nwlan = network.WLAN(network.STA_IF)\nwlan.active(True)\nwlan.connect('SSID', 'PASSWORD')\nwhile not wlan.isconnected():\n    pass\nprint(wlan.ifconfig())",
            "ADC read": "from machine import ADC\nadc = ADC(34)\nadc.atten(ADC.ATTN_11DB)\nprint(adc.read())",
            "PWM fade": "from machine import Pin, PWM\nimport time\np = PWM(Pin(2))\np.freq(1000)\nfor d in range(0, 1024, 10):\n    p.duty(d)\n    time.sleep_ms(20)",
            "HTTP GET": "import urequests\nr = urequests.get('http://example.com')\nprint(r.text)\nr.close()",
            "Deep sleep": "import machine\nmachine.deepsleep(10000)",
        }
        listbox = tk.Listbox(self.snippets_frame, bg=self.theme["bg"], fg=self.theme["fg"],
                             selectbackground=self.theme["select_bg"],
                             selectforeground=self.theme["select_fg"],
                             relief="flat", font=(self.settings.get("font_family", "Consolas"), 10))
        listbox.pack(fill="both", expand=True)
        for name in snippets:
            listbox.insert("end", name)
        def insert_snippet(event):
            sel = listbox.curselection()
            if sel:
                name = listbox.get(sel[0])
                self.editor.insert("insert", snippets[name])
        listbox.bind("<Double-1>", insert_snippet)
        tk.Button(self.snippets_frame, text="Insérer", command=lambda: insert_snippet(None),
                  bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                  activebackground=self.theme["button_active"], relief="flat").pack(fill="x", pady=2)

    def _build_info_panel(self):
        self.info_text = tk.Text(self.info_frame, wrap="word", state="disabled",
                                 bg=self.theme["bg"], fg=self.theme["fg"],
                                 font=(self.settings.get("font_family", "Consolas"), 9),
                                 relief="flat")
        self.info_text.pack(fill="both", expand=True)
        self._update_info_panel()

    def _update_info_panel(self):
        try:
            info = f"""{APP_NAME} v{APP_VERSION}
Auteur: {APP_AUTHOR}
Date: {APP_DATE}

Python: {sys.version.split()[0]}
Pygments: {'OK' if PYGMENTS_OK else 'Non installé'}
esptool: {'OK' if ESPTOOL_OK else 'Non installé'}
ampy: {'OK' if AMPY_OK else 'Non installé'}
mpremote: {'OK' if MPREMOTE_OK else 'Non installé'}
Pillow: {'OK' if PIL_OK else 'Non installé'}
"""
            self.info_text.config(state="normal")
            self.info_text.delete("1.0", "end")
            self.info_text.insert("end", info)
            self.info_text.config(state="disabled")
        except Exception:
            pass

    def _build_editor(self):
        self.line_canvas = LineNumberCanvas(self.editor_frame, None, self.theme,
                                            bg=self.theme["line_bg"], highlightthickness=0)
        self.editor = CodeEditor(self.editor_frame, self)
        self.line_canvas.text_widget = self.editor
        self.line_canvas.pack(side="left", fill="y")
        self.editor.pack(side="left", fill="both", expand=True)
        self.vscroll = tk.Scrollbar(self.editor_frame, command=self._on_scroll, orient="vertical",
                                    bg=self.theme["bg"], troughcolor=self.theme["bg"],
                                    highlightbackground=self.theme["border"])
        self.vscroll.pack(side="right", fill="y")
        self.editor.config(yscrollcommand=self._on_editor_scroll)
        self.hscroll = tk.Scrollbar(self.editor_frame, command=self.editor.xview, orient="horizontal",
                                    bg=self.theme["bg"], troughcolor=self.theme["bg"])
        self.hscroll.pack(side="bottom", fill="x")
        self.editor.config(xscrollcommand=self.hscroll.set)
        self.editor.insert("1.0", DEFAULT_CODE)
        self.editor.highlight_all()

    def _on_scroll(self, *args):
        self.editor.yview(*args)
        self.line_canvas.redraw()

    def _on_editor_scroll(self, first, last):
        self.vscroll.set(first, last)
        self.line_canvas.redraw()

    # ─────────────────────────── Thèmes & styles ────────────────────────────

    def _apply_theme(self):
        self.configure(bg=self.theme["bg"])
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background=self.theme["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", background=self.theme["button_bg"],
                        foreground=self.theme["button_fg"], padding=[10, 4])
        style.map("TNotebook.Tab", background=[("selected", self.theme["select_bg"])],
                  foreground=[("selected", self.theme["select_fg"])])
        style.configure("TCombobox", fieldbackground=self.theme["bg"],
                        background=self.theme["button_bg"], foreground=self.theme["fg"],
                        selectbackground=self.theme["select_bg"])
        style.configure("Treeview", background=self.theme["bg"], foreground=self.theme["fg"],
                        fieldbackground=self.theme["bg"])
        style.configure("Treeview.Heading", background=self.theme["button_bg"],
                        foreground=self.theme["button_fg"])

    def set_theme(self, name):
        if name not in THEMES:
            return
        self.theme = THEMES[name]
        self.settings.set("theme", name)
        self._apply_theme()
        self.editor.set_theme(self.theme)
        self.line_canvas.set_theme(self.theme)
        self.terminal.set_theme(self.theme)
        self.status_bar.set_theme(self.theme)
        self.log_text.config(bg=self.theme["bg"], fg=self.theme["fg"],
                             insertbackground=self.theme["insert"])
        for child in self.toolbar.winfo_children():
            if isinstance(child, tk.Button):
                child.config(bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                             activebackground=self.theme["button_active"])

    def _toggle_line_numbers(self):
        show = self.var_show_line_numbers.get()
        self.settings.set("show_line_numbers", show)
        if show:
            self.line_canvas.pack(side="left", fill="y", before=self.editor)
        else:
            self.line_canvas.pack_forget()

    def _toggle_word_wrap(self):
        wrap = self.var_word_wrap.get()
        self.settings.set("word_wrap", wrap)
        self.editor.set_word_wrap(wrap)

    def _toggle_toolbar(self):
        show = self.var_toolbar.get()
        self.settings.set("toolbar_visible", show)
        if show:
            self.toolbar.pack(fill="x", side="top", before=self.paned)
        else:
            self.toolbar.pack_forget()

    def _toggle_statusbar(self):
        show = self.var_statusbar.get()
        self.settings.set("statusbar_visible", show)
        if show:
            self.status_bar.pack(fill="x", side="bottom")
        else:
            self.status_bar.pack_forget()

    # ─────────────────────────── Gestion des fichiers ───────────────────────

    def new_file(self):
        if not self._check_save():
            return
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", DEFAULT_CODE)
        self.current_file = None
        self.editor.clear_modified()
        self.update_title()
        self.editor.highlight_all()

    def open_file_dialog(self):
        if not self._check_save():
            return
        path = filedialog.askopenfilename(
            defaultextension=".py",
            filetypes=[("Python", "*.py"), ("MicroPython", "*.mpy"), ("Tous", "*.*")]
        )
        if path:
            self.open_file(path)

    def open_file(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", content)
            self.current_file = Path(path)
            self.editor.clear_modified()
            self.settings.add_recent_file(str(self.current_file))
            self.update_title()
            self.editor.highlight_all()
            self._update_recent_menu()
            self.logger.success(f"Ouvert: {path}")
        except Exception as e:
            self.logger.error(f"Impossible d'ouvrir {path}: {e}")

    def save_file(self):
        if self.current_file:
            self._write_file(self.current_file)
        else:
            self.save_file_as()

    def save_file_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python", "*.py"), ("Tous", "*.*")]
        )
        if path:
            self.current_file = Path(path)
            self._write_file(self.current_file)
            self.settings.add_recent_file(str(self.current_file))
            self._update_recent_menu()

    def _write_file(self, path):
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.editor.get("1.0", "end-1c"))
            self.editor.clear_modified()
            self.update_title()
            self.logger.success(f"Enregistré: {path}")
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde {path}: {e}")

    def _check_save(self):
        if self.editor.is_modified():
            answer = messagebox.askyesnocancel("Enregistrer ?",
                "Le fichier actuel a été modifié. Voulez-vous l'enregistrer ?")
            if answer is True:
                self.save_file()
            elif answer is False:
                return True
            else:
                return False
        return True

    def _load_startup(self):
        recent = self.settings.get("recent_files", [])
        if recent and Path(recent[0]).exists():
            self.open_file(recent[0])
        self._update_recent_menu()
        self._detect_ports()

    def _update_recent_menu(self):
        self.recent_menu.delete(0, "end")
        for p in self.settings.get("recent_files", []):
            self.recent_menu.add_command(label=p, command=lambda path=p: self.open_file(path))
        if not self.settings.get("recent_files"):
            self.recent_menu.add_command(label="(aucun)", state="disabled")

    def update_title(self):
        name = self.current_file.name if self.current_file else "sans_titre.py"
        mod = " *" if self.editor.is_modified() else ""
        self.title(f"{name}{mod} — {APP_NAME} v{APP_VERSION}")

    # ─────────────────────────── Raccourcis globaux ─────────────────────────

    def _bind_global_shortcuts(self):
        self.bind("<Control-n>", lambda e: self.new_file())
        self.bind("<Control-N>", lambda e: self.new_file())
        self.bind("<Control-o>", lambda e: self.open_file_dialog())
        self.bind("<Control-O>", lambda e: self.open_file_dialog())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-S>", lambda e: self.save_file())
        self.bind("<Control-Shift-s>", lambda e: self.save_file_as())
        self.bind("<Control-Shift-S>", lambda e: self.save_file_as())
        self.bind("<F5>", lambda e: self.run_on_esp32())
        self.bind("<F6>", lambda e: self.run_selection_on_esp32())
        self.bind("<F7>", lambda e: self.upload_current_file())
        self.bind("<F9>", lambda e: self.terminal._toggle_connection())
        self.bind("<Control-Shift-p>", lambda e: self._show_preferences())

    # ─────────────────────────── Actions éditeur ────────────────────────────

    def _undo(self):
        try:
            self.editor.edit_undo()
        except Exception:
            pass

    def _redo(self):
        try:
            self.editor.edit_redo()
        except Exception:
            pass

    def _cut(self):
        try:
            self.editor.event_generate("<<Cut>>")
        except Exception:
            pass

    def _copy(self):
        try:
            self.editor.event_generate("<<Copy>>")
        except Exception:
            pass

    def _paste(self):
        try:
            self.editor.event_generate("<<Paste>>")
        except Exception:
            pass

    def show_find_bar(self):
        if self.find_bar is not None:
            self.find_bar.focus()
            return
        frame = tk.Frame(self.editor_frame, bg=self.theme["bg"], height=28)
        frame.pack(fill="x", side="bottom")
        tk.Label(frame, text="Rechercher:", bg=self.theme["bg"], fg=self.theme["fg"]).pack(side="left", padx=4)
        entry = tk.Entry(frame, bg=self.theme["bg"], fg=self.theme["fg"],
                         insertbackground=self.theme["insert"], relief="flat",
                         highlightbackground=self.theme["border"], highlightthickness=1)
        entry.pack(side="left", fill="x", expand=True, padx=4)
        def do_find():
            query = entry.get()
            self.editor.tag_remove("search", "1.0", "end")
            if not query:
                return
            pos = "1.0"
            while True:
                found = self.editor.search(query, pos, stopindex="end", nocase=True)
                if not found:
                    break
                end = f"{found} + {len(query)} chars"
                self.editor.tag_add("search", found, end)
                pos = end
        def close_find():
            frame.destroy()
            self.find_bar = None
            self.editor.tag_remove("search", "1.0", "end")
        entry.bind("<Return>", lambda e: do_find())
        entry.bind("<Escape>", lambda e: close_find())
        tk.Button(frame, text="Suivant", command=do_find,
                  bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                  activebackground=self.theme["button_active"], relief="flat").pack(side="left", padx=2)
        tk.Button(frame, text="Fermer", command=close_find,
                  bg=self.theme["button_bg"], fg=self.theme["error"],
                  activebackground=self.theme["button_active"], relief="flat").pack(side="left", padx=2)
        self.find_bar = entry
        entry.focus_set()

    def show_goto_line(self):
        answer = simpledialog.askinteger("Aller à la ligne", "Numéro de ligne:", minvalue=1)
        if answer:
            self.editor.mark_set("insert", f"{answer}.0")
            self.editor.see(f"{answer}.0")

    # ─────────────────────────── ESP32 actions ──────────────────────────────

    def _detect_ports(self):
        ports = self.terminal.refresh_ports()
        esp_ports = [p for p in ports if is_esp32_port(p)]
        if esp_ports:
            p = esp_ports[0]
            self.status_bar.set_port(f"{p.device} @ {self.terminal.baud_combo.get()}")
            self.logger.success(f"ESP32 détecté sur {p.device}")
            if self.settings.get("auto_connect", False):
                self.terminal.connect()
        else:
            self.status_bar.set_port("Aucun ESP32 détecté")
            if ports:
                self.logger.info(f"Ports disponibles: {', '.join(p.device for p in ports)}")
            else:
                self.logger.warn("Aucun port COM détecté.")
        return ports

    def _start_port_watcher(self):
        if not self.settings.get("detect_esp32", True):
            return
        ports = list(serial.tools.list_ports.comports())
        h = hashlib.md5(
            "".join(f"{p.device}{p.vid}{p.pid}" for p in ports).encode()
        ).hexdigest()
        if h != self._last_ports_hash:
            self._last_ports_hash = h
            self.terminal.refresh_ports()
            esp_ports = [p for p in ports if is_esp32_port(p)]
            if esp_ports:
                self.status_bar.set_port(f"{esp_ports[0].device} détecté")
        self._port_watcher_job = self.after(1500, self._start_port_watcher)

    def run_on_esp32(self):
        code = self.editor.get("1.0", "end-1c")
        if not code.strip():
            self.logger.warn("Aucun code à exécuter.")
            return
        self.logger.info("Envoi du code vers l'ESP32...")
        def cb(ok, err):
            if ok:
                self.logger.success("Exécution terminée avec succès.")
            else:
                self.logger.error(f"Échec exécution: {err}")
        self.esp32.run_code_on_board(code, cb)

    def run_selection_on_esp32(self):
        try:
            code = self.editor.get("sel.first", "sel.last")
        except Exception:
            self.logger.warn("Aucune sélection.")
            return
        def cb(ok, err):
            if ok:
                self.logger.success("Sélection exécutée.")
            else:
                self.logger.error(f"Échec: {err}")
        self.esp32.run_code_on_board(code, cb)

    def upload_current_file(self):
        if not self.current_file:
            self.save_file_as()
        if not self.current_file:
            return
        remote = self.current_file.name
        self.logger.info(f"Upload de {self.current_file} vers {remote}...")
        def cb(ok, err):
            if ok:
                self.logger.success(f"Upload terminé: {remote}")
            else:
                self.logger.error(f"Échec upload: {err}")
        if self.settings.get("backup_before_upload", True):
            self._backup_file(self.current_file)
        self.esp32.put_file(str(self.current_file), remote, cb)

    def download_file_from_esp32(self):
        remote = simpledialog.askstring("Télécharger depuis ESP32", "Chemin distant:")
        if not remote:
            return
        local = filedialog.asksaveasfilename(initialfile=remote)
        if not local:
            return
        def cb(ok, err):
            if ok:
                self.logger.success(f"Téléchargé: {remote} -> {local}")
            else:
                self.logger.error(f"Échec téléchargement: {err}")
        self.esp32.get_file(remote, local, cb)

    def list_esp32_files(self):
        self.logger.info("Liste des fichiers sur l'ESP32...")
        def cb(ok, err):
            if not ok:
                self.logger.error(f"Échec liste: {err}")
        self.esp32.list_files(cb)

    def erase_flash_dialog(self):
        if messagebox.askyesno("Confirmation",
            "Effacer complètement la flash de l'ESP32 ? Cette action est irréversible."):
            def cb(ok, err):
                if ok:
                    self.logger.success("Flash effacée.")
                else:
                    self.logger.error(f"Échec effacement: {err}")
            self.esp32.erase_flash(cb)

    def flash_firmware_dialog(self):
        path = filedialog.askopenfilename(
            title="Choisir un firmware .bin",
            filetypes=[("Firmware binaire", "*.bin"), ("Tous", "*.*")]
        )
        if path:
            self.settings.set("flash_firmware_path", path)
            if messagebox.askyesno("Flasher", f"Flasher {path} sur l'ESP32 ?"):
                def cb(ok, err):
                    if ok:
                        self.logger.success("Firmware flashé avec succès.")
                    else:
                        self.logger.error(f"Échec flash: {err}")
                self.esp32.flash_firmware(path, cb)

    def _send_stop(self):
        self.terminal._send_ctrl_c()

    def _backup_file(self, path):
        try:
            backup_dir = Path.home() / ".hacker_ide_backups"
            backup_dir.mkdir(exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            dest = backup_dir / f"{path.name}.{timestamp}.bak"
            shutil.copy2(path, dest)
            self.logger.info(f"Backup créé: {dest}")
        except Exception:
            pass

    # ─────────────────────────── Outils ─────────────────────────────────────

    def _new_project_template(self):
        d = filedialog.askdirectory(title="Dossier du nouveau projet")
        if not d:
            return
        base = Path(d)
        (base / "src").mkdir(exist_ok=True)
        (base / "lib").mkdir(exist_ok=True)
        (base / "tests").mkdir(exist_ok=True)
        main_file = base / "src" / "main.py"
        with open(main_file, "w", encoding="utf-8") as f:
            f.write(DEFAULT_CODE)
        readme = base / "README.txt"
        with open(readme, "w", encoding="utf-8") as f:
            f.write(f"Projet ESP32 généré par {APP_NAME} {APP_VERSION}\nAuteur: {APP_AUTHOR}\nDate: {APP_DATE}\n")
        self.logger.success(f"Projet créé: {base}")
        self.open_file(main_file)

    def _analyze_code(self):
        code = self.editor.get("1.0", "end-1c")
        lines = code.splitlines()
        issues = []
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                issues.append((i, "Ligne trop longue (>120 caractères)"))
            if "TODO" in line:
                issues.append((i, "TODO détecté"))
            if "FIXME" in line:
                issues.append((i, "FIXME détecté"))
        # Vérification basique parenthèses
        stack = []
        pairs = {"(": ")", "[": "]", "{": "}"}
        for ch in code:
            if ch in pairs:
                stack.append(ch)
            elif ch in pairs.values():
                if not stack:
                    issues.append((0, "Parenthèse fermante sans ouvrante"))
                else:
                    last = stack.pop()
                    if pairs[last] != ch:
                        issues.append((0, f"Appariement incorrect: {last} et {ch}"))
        if stack:
            issues.append((0, f"Parenthèses non fermées: {stack}"))
        self.editor.tag_remove("error_line", "1.0", "end")
        msg = f"Analyse: {len(lines)} lignes, {len(issues)} problèmes.\n"
        for ln, desc in issues:
            msg += f"  Ligne {ln}: {desc}\n"
            if ln > 0:
                self.editor.tag_add("error_line", f"{ln}.0", f"{ln+1}.0")
        self.logger.info(msg)

    def _format_code(self):
        code = self.editor.get("1.0", "end-1c")
        try:
            import autopep8
            formatted = autopep8.fix_code(code, options={"max_line_length": 120})
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", formatted)
            self.editor.highlight_all()
            self.logger.success("Code formaté.")
        except ImportError:
            # Formatage basique
            lines = code.splitlines()
            out = []
            indent = 0
            for line in lines:
                stripped = line.strip()
                if stripped.endswith(":"):
                    out.append("    " * indent + stripped)
                    indent += 1
                elif stripped.startswith(("return", "break", "continue", "pass", "raise")):
                    indent = max(0, indent - 1)
                    out.append("    " * indent + stripped)
                else:
                    out.append("    " * indent + stripped)
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", "\n".join(out))
            self.logger.info("Formatage basique appliqué (autopep8 non installé).")

    def _minify_code(self):
        code = self.editor.get("1.0", "end-1c")
        lines = [line.strip() for line in code.splitlines()]
        lines = [line for line in lines if line and not line.startswith("#")]
        minified = "\n".join(lines)
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", minified)
        self.editor.highlight_all()
        self.logger.info("Code minifié (commentaires et lignes vides supprimés).")

    def _show_preferences(self):
        win = tk.Toplevel(self)
        win.title("Préférences")
        win.configure(bg=self.theme["bg"])
        win.geometry("500x500")
        win.transient(self)
        frame = tk.Frame(win, bg=self.theme["bg"])
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        tk.Label(frame, text="Police:", bg=self.theme["bg"], fg=self.theme["fg"]).grid(row=0, column=0, sticky="w")
        fonts = get_monospace_fonts()
        font_var = StringVar(value=self.settings.get("font_family", "Consolas"))
        ttk.Combobox(frame, values=fonts, textvariable=font_var, state="readonly").grid(row=0, column=1, sticky="ew")
        tk.Label(frame, text="Taille:", bg=self.theme["bg"], fg=self.theme["fg"]).grid(row=1, column=0, sticky="w")
        size_var = IntVar(value=self.settings.get("font_size", 12))
        tk.Spinbox(frame, from_=6, to=32, textvariable=size_var).grid(row=1, column=1, sticky="w")
        tk.Label(frame, text="Indentation (espaces):", bg=self.theme["bg"], fg=self.theme["fg"]).grid(row=2, column=0, sticky="w")
        tab_var = IntVar(value=self.settings.get("tab_size", 4))
        tk.Spinbox(frame, from_=2, to=8, textvariable=tab_var).grid(row=2, column=1, sticky="w")
        auto_save_var = BooleanVar(value=self.settings.get("auto_save", True))
        tk.Checkbutton(frame, text="Sauvegarde automatique", variable=auto_save_var,
                       bg=self.theme["bg"], fg=self.theme["fg"], selectcolor=self.theme["bg"]).grid(row=3, column=0, columnspan=2, sticky="w")
        detect_var = BooleanVar(value=self.settings.get("detect_esp32", True))
        tk.Checkbutton(frame, text="Détection automatique ESP32", variable=detect_var,
                       bg=self.theme["bg"], fg=self.theme["fg"], selectcolor=self.theme["bg"]).grid(row=4, column=0, columnspan=2, sticky="w")
        auto_connect_var = BooleanVar(value=self.settings.get("auto_connect", False))
        tk.Checkbutton(frame, text="Connexion automatique ESP32", variable=auto_connect_var,
                       bg=self.theme["bg"], fg=self.theme["fg"], selectcolor=self.theme["bg"]).grid(row=5, column=0, columnspan=2, sticky="w")
        backup_var = BooleanVar(value=self.settings.get("backup_before_upload", True))
        tk.Checkbutton(frame, text="Backup avant upload", variable=backup_var,
                       bg=self.theme["bg"], fg=self.theme["fg"], selectcolor=self.theme["bg"]).grid(row=6, column=0, columnspan=2, sticky="w")
        def save_prefs():
            self.settings.set("font_family", font_var.get())
            self.settings.set("font_size", size_var.get())
            self.settings.set("tab_size", tab_var.get())
            self.settings.set("auto_save", auto_save_var.get())
            self.settings.set("detect_esp32", detect_var.get())
            self.settings.set("auto_connect", auto_connect_var.get())
            self.settings.set("backup_before_upload", backup_var.get())
            self.editor.set_font(font_var.get(), size_var.get())
            self.terminal.set_theme(self.theme)
            self.settings.save()
            win.destroy()
        tk.Button(frame, text="Enregistrer", command=save_prefs,
                  bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                  activebackground=self.theme["button_active"], relief="flat").grid(row=7, column=0, pady=10)
        tk.Button(frame, text="Annuler", command=win.destroy,
                  bg=self.theme["button_bg"], fg=self.theme["error"],
                  activebackground=self.theme["button_active"], relief="flat").grid(row=7, column=1, pady=10)
        frame.columnconfigure(1, weight=1)

    def _show_shortcuts(self):
        shortcuts = """Raccourcis clavier:

Ctrl+N : Nouveau fichier
Ctrl+O : Ouvrir
Ctrl+S : Enregistrer
Ctrl+Maj+S : Enregistrer sous
Ctrl+Z / Ctrl+Y : Annuler / Rétablir
Ctrl+X/C/V : Couper/Copier/Coller
Ctrl+F : Rechercher
Ctrl+G : Aller à la ligne
Ctrl+/ : Commenter/décommenter
Ctrl+D : Dupliquer la ligne
F5 : Exécuter sur ESP32
F6 : Exécuter la sélection
F7 : Téléverser fichier
F9 : Connecter/déconnecter port
"""
        messagebox.showinfo("Raccourcis", shortcuts)

    def _show_about(self):
        messagebox.showinfo("À propos",
            f"{APP_NAME} v{APP_VERSION}\nAuteur: {APP_AUTHOR}\nDate: {APP_DATE}\n\n"
            "IDE avancé pour le développement MicroPython sur ESP32.")

    # ─────────────────────────── Auto-save & logs ───────────────────────────

    def _start_auto_save(self):
        if self.settings.get("auto_save", True) and self.current_file:
            if self.editor.is_modified():
                self.save_file()
        self._auto_save_job = self.after(self.settings.get("auto_save_interval", 30) * 1000, self._start_auto_save)

    def write_log(self, line):
        self._log_lines.append(line)
        self._log_lines = self._log_lines[-200:]
        self.log_text.config(state="normal")
        self.log_text.insert("end", line + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def _update_position(self, event=None):
        try:
            idx = self.editor.index("insert")
            line, col = idx.split(".")
            self.status_bar.set_position(f"Ln {line}, Col {col}")
            self.line_canvas.redraw()
        except Exception:
            pass

    # ─────────────────────────── Fermeture ──────────────────────────────────

    def _on_close(self):
        if not self._check_save():
            return
        self.settings.set("window_geometry", self.geometry())
        self.settings.set("word_wrap", self.var_word_wrap.get())
        self.settings.set("show_line_numbers", self.var_show_line_numbers.get())
        self.settings.set("toolbar_visible", self.var_toolbar.get())
        self.settings.set("statusbar_visible", self.var_statusbar.get())
        self.settings.set("last_baud", self.terminal.baud_combo.get())
        if self.terminal.serial_port:
            self.settings.set("last_port", self.terminal.port_combo.get().split(" | ")[0] if self.terminal.port_combo.get() else "")
        self.settings.save()
        self.terminal.disconnect()
        self.destroy()


# ═══════════════════════════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    if sys.platform.startswith("win"):
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
    app = HackerESP32IDE()
    app.mainloop()


if __name__ == "__main__":
    main()
