"""
Boîtes de dialogue personnalisées.
"""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog
from typing import Optional

from ..core.constants import PROJECTS_DIR
from ..core.i18n import translate
from ..core.theme import get_theme


def ask_yes_no_cancel(parent: tk.Widget, title: str, message: str) -> str:
    return messagebox.askyesnocancel(title, message, parent=parent)


def show_error(parent: tk.Widget, message: str) -> None:
    messagebox.showerror(translate("app_title"), message, parent=parent)


def show_info(parent: tk.Widget, message: str) -> None:
    messagebox.showinfo(translate("app_title"), message, parent=parent)


def ask_open_file(parent: tk.Widget, initial_dir: Optional[Path] = None) -> Optional[Path]:
    path = filedialog.askopenfilename(
        parent=parent,
        initialdir=initial_dir or Path.home(),
        title=translate("open_project"),
        filetypes=[("Fichiers Python", "*.py"), ("Tous fichiers", "*.*")],
    )
    return Path(path) if path else None


def ask_save_file(parent: tk.Widget, initial_dir: Optional[Path] = None, default_name: str = "main.py") -> Optional[Path]:
    path = filedialog.asksaveasfilename(
        parent=parent,
        initialdir=initial_dir or Path.home(),
        initialfile=default_name,
        title=translate("save_as"),
        defaultextension=".py",
        filetypes=[("Fichiers Python", "*.py"), ("Tous fichiers", "*.*")],
    )
    return Path(path) if path else None


def ask_project_directory(parent: tk.Widget) -> Optional[Path]:
    path = filedialog.askdirectory(parent=parent, initialdir=PROJECTS_DIR, title=translate("open_project"))
    return Path(path) if path else None


def ask_new_project_name(parent: tk.Widget) -> Optional[Path]:
    name = simpledialog.askstring(translate("new_project"), "Nom du projet :", parent=parent)
    if not name:
        return None
    project_path = PROJECTS_DIR / name
    if project_path.exists():
        show_error(parent, "Un projet avec ce nom existe déjà.")
        return None
    project_path.mkdir(parents=True, exist_ok=True)
    (project_path / "main.py").write_text(DEFAULT_MAIN_PY, encoding="utf-8")
    (project_path / "README.md").write_text(f"# {name}\n\nProjet ESP32 MicroPython.\n", encoding="utf-8")
    return project_path


DEFAULT_MAIN_PY = '''# Projet ESP32 MicroPython
# Auteur : hackers_tchad

from machine import Pin
import time

led = Pin(2, Pin.OUT)

while True:
    led.value(not led.value())
    time.sleep_ms(500)
'''
