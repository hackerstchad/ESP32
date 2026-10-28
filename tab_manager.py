"""
Gestionnaire d'onglets d'édition.
"""

import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Callable, Dict, List, Optional

from ..core.theme import get_theme


class TabInfo:
    def __init__(self, path: Optional[Path], editor, frame):
        self.path = path
        self.editor = editor
        self.frame = frame
        self.saved_hash: int = self._hash_content()
        self.title = self._make_title()

    def _hash_content(self) -> int:
        return hash(self.editor.get_text())

    def _make_title(self) -> str:
        if self.path:
            return self.path.name
        return "Sans titre"

    def mark_saved(self) -> None:
        self.saved_hash = self._hash_content()

    @property
    def is_modified(self) -> bool:
        return self._hash_content() != self.saved_hash


class TabManager:
    """Widget à onglets personnalisé synchronisé avec des éditeurs CodeEditor."""

    def __init__(self, parent: tk.Widget, new_editor_callback: Callable, theme=None):
        self.parent = parent
        self.theme = theme or get_theme()
        self.new_editor_callback = new_editor_callback
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.tabs: List[TabInfo] = []
        self._tab_frames: Dict[int, tk.Widget] = {}

        style = ttk.Style()
        style.configure("TNotebook", background=self.theme.background, tabmargins=[2, 5, 2, 0])
        style.configure("TNotebook.Tab", background=self.theme.panel, foreground=self.theme.foreground)
        style.map("TNotebook.Tab", background=[("selected", self.theme.background)])

        self.notebook.bind("<Button-2>", self._on_tab_close_click)
        self.notebook.bind("<Button-3>", self._on_tab_menu)

    def add_tab(self, path: Optional[Path] = None, content: str = "") -> TabInfo:
        frame = tk.Frame(self.notebook, bg=self.theme.background)
        editor = self.new_editor_callback(frame)
        editor.set_text(content)
        info = TabInfo(path, editor, frame)
        self.tabs.append(info)
        title = info.title
        self.notebook.add(frame, text=title)
        self.notebook.select(frame)
        editor.focus_set()
        return info

    def current_tab(self) -> Optional[TabInfo]:
        if not self.tabs:
            return None
        try:
            idx = self.notebook.index("current")
            return self.tabs[idx]
        except Exception:
            return None

    def current_editor(self):
        tab = self.current_tab()
        return tab.editor if tab else None

    def update_titles(self) -> None:
        for idx, info in enumerate(self.tabs):
            title = info.title
            if info.is_modified:
                title = f"● {title}"
            self.notebook.tab(idx, text=title)

    def close_tab(self, index: Optional[int] = None) -> bool:
        if index is None:
            index = self.notebook.index("current")
        if index < 0 or index >= len(self.tabs):
            return False
        info = self.tabs[index]
        if info.is_modified:
            return False
        self.notebook.forget(index)
        self.tabs.pop(index)
        return True

    def close_current(self) -> bool:
        return self.close_tab()

    def _on_tab_close_click(self, event) -> None:
        try:
            idx = self.notebook.index(f"@{event.x},{event.y}")
            self.close_tab(idx)
        except Exception:
            pass

    def _on_tab_menu(self, event) -> None:
        pass
