"""
Explorateur de projets en arbre.
"""

import os
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Callable, Optional

from ..core.constants import SUPPORTED_EXTS
from ..core.theme import get_theme


class ProjectTree:
    """Arborescence de fichiers d'un projet."""

    def __init__(self, parent: tk.Widget, on_open: Callable[[Path], None]):
        self.parent = parent
        self.on_open = on_open
        self.theme = get_theme()
        self.root_path: Optional[Path] = None

        self.tree = ttk.Treeview(parent, selectmode="browse")
        self.tree.heading("#0", text="Projet", anchor=tk.W)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Return>", self._on_double_click)

        self._setup_style()

    def _setup_style(self) -> None:
        style = ttk.Style()
        style.configure("Treeview", background=self.theme.panel, foreground=self.theme.foreground, fieldbackground=self.theme.panel)
        style.configure("Treeview.Heading", background=self.theme.input_bg, foreground=self.theme.foreground)
        style.map("Treeview", background=[("selected", self.theme.highlight)])

    def load_project(self, path: Path) -> None:
        self.root_path = path
        self.tree.delete(*self.tree.get_children())
        self.tree.heading("#0", text=path.name)
        self._insert_node("", path)

    def _insert_node(self, parent: str, path: Path) -> None:
        icon = "📁" if path.is_dir() else self._file_icon(path)
        node = self.tree.insert(parent, "end", text=f"{icon} {path.name}", open=False, values=[str(path)])
        if path.is_dir():
            try:
                for child in sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
                    self._insert_node(node, child)
            except PermissionError:
                pass

    def _file_icon(self, path: Path) -> str:
        ext = path.suffix.lower()
        if ext == ".py":
            return "🐍"
        if ext in (".txt", ".md"):
            return "📝"
        if ext == ".json":
            return "📋"
        if ext in (".html", ".css", ".js"):
            return "🌐"
        return "📄"

    def _on_double_click(self, event=None) -> None:
        item = self.tree.selection()
        if not item:
            return
        path_str = self.tree.item(item[0], "values")
        if not path_str:
            return
        path = Path(path_str[0])
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTS:
            self.on_open(path)

    def refresh(self) -> None:
        if self.root_path:
            self.load_project(self.root_path)
