"""
Barre de menus de l'application.
"""

import tkinter as tk
from tkinter import Menu
from typing import Callable, Dict

from ..core.i18n import translate
from ..core.theme import get_theme


class MenuBar:
    """Barre de menus principale."""

    def __init__(self, parent: tk.Tk, callbacks: Dict[str, Callable]):
        self.parent = parent
        self.callbacks = callbacks
        self.theme = get_theme()
        self.menubar = tk.Menu(parent, bg=self.theme.panel, fg=self.theme.foreground, activebackground=self.theme.highlight, activeforeground=self.theme.foreground, tearoff=0)
        parent.config(menu=self.menubar)

        self._build_file_menu()
        self._build_edit_menu()
        self._build_view_menu()
        self._build_device_menu()
        self._build_tools_menu()
        self._build_help_menu()

    def _build_file_menu(self) -> None:
        menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=translate("file"), menu=menu)
        menu.add_command(label=translate("new_project"), command=self.callbacks.get("new_project"), accelerator="Ctrl+Shift+N")
        menu.add_command(label=translate("open_project"), command=self.callbacks.get("open_project"), accelerator="Ctrl+Shift+O")
        menu.add_separator()
        menu.add_command(label=translate("save"), command=self.callbacks.get("save"), accelerator="Ctrl+S")
        menu.add_command(label=translate("save_as"), command=self.callbacks.get("save_as"), accelerator="Ctrl+Shift+S")
        menu.add_separator()
        menu.add_command(label=translate("exit"), command=self.callbacks.get("exit"), accelerator="Alt+F4")

    def _build_edit_menu(self) -> None:
        menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=translate("edit"), menu=menu)
        menu.add_command(label=translate("undo"), command=self.callbacks.get("undo"), accelerator="Ctrl+Z")
        menu.add_command(label=translate("redo"), command=self.callbacks.get("redo"), accelerator="Ctrl+Y")
        menu.add_separator()
        menu.add_command(label=translate("cut"), command=self.callbacks.get("cut"), accelerator="Ctrl+X")
        menu.add_command(label=translate("copy"), command=self.callbacks.get("copy"), accelerator="Ctrl+C")
        menu.add_command(label=translate("paste"), command=self.callbacks.get("paste"), accelerator="Ctrl+V")
        menu.add_separator()
        menu.add_command(label=translate("find"), command=self.callbacks.get("find"), accelerator="Ctrl+F")
        menu.add_command(label=translate("replace"), command=self.callbacks.get("replace"), accelerator="Ctrl+H")

    def _build_view_menu(self) -> None:
        menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=translate("view"), menu=menu)
        menu.add_command(label="Thème sombre/clair", command=self.callbacks.get("toggle_theme"))
        menu.add_separator()
        menu.add_command(label="Explorateur", command=self.callbacks.get("toggle_explorer"))
        menu.add_command(label="Terminal", command=self.callbacks.get("toggle_terminal"))

    def _build_device_menu(self) -> None:
        menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=translate("device"), menu=menu)
        menu.add_command(label=translate("refresh_ports"), command=self.callbacks.get("refresh_ports"))
        menu.add_command(label=translate("connect"), command=self.callbacks.get("connect"), accelerator="Ctrl+Shift+C")
        menu.add_command(label=translate("disconnect"), command=self.callbacks.get("disconnect"))
        menu.add_separator()
        menu.add_command(label=translate("upload"), command=self.callbacks.get("upload"), accelerator="Ctrl+U")
        menu.add_command(label=translate("run"), command=self.callbacks.get("run"), accelerator="F5")
        menu.add_command(label=translate("stop"), command=self.callbacks.get("stop"), accelerator="Shift+F5")

    def _build_tools_menu(self) -> None:
        menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=translate("tools"), menu=menu)
        menu.add_command(label="Gestionnaire de firmware", command=self.callbacks.get("firmware_manager"))
        menu.add_command(label="Nettoyer la carte", command=self.callbacks.get("clean_board"))
        menu.add_separator()
        menu.add_command(label=translate("preferences"), command=self.callbacks.get("preferences"))

    def _build_help_menu(self) -> None:
        menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=translate("help"), menu=menu)
        menu.add_command(label="Documentation MicroPython", command=self.callbacks.get("open_docs"))
        menu.add_command(label=translate("about"), command=self.callbacks.get("about"))
