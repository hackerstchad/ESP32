"""
Widget éditeur de code avec numéros de ligne, coloration et indentation.
"""

import tkinter as tk
from tkinter import ttk, font as tkfont
from typing import Callable, Optional

from ..core.config import get_config
from ..core.theme import get_theme
from .syntax import SyntaxHighlighter


class CodeEditor(ttk.Frame):
    """Éditeur de code intégré."""

    def __init__(self, master=None, on_change: Optional[Callable] = None, **kwargs):
        super().__init__(master, **kwargs)
        self.on_change = on_change
        self._modified = False
        self._ignore_change = False

        self._setup_fonts()
        self._build_ui()
        self._bind_events()
        self._apply_theme()
        self.highlighter = SyntaxHighlighter(self.text)

    def _setup_fonts(self) -> None:
        cfg = get_config()
        family = cfg.get("editor.font_family", "JetBrains Mono")
        size = cfg.get("editor.font_size", 12)
        try:
            self.editor_font = tkfont.Font(family=family, size=size)
        except tk.TclError:
            self.editor_font = tkfont.Font(family="Consolas", size=size)
        self.line_font = tkfont.Font(family=self.editor_font.cget("family"), size=size)

    def _build_ui(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Gouttière numéros de ligne
        self.line_canvas = tk.Canvas(
            self,
            width=50,
            highlightthickness=0,
        )
        self.line_canvas.grid(row=0, column=0, sticky="ns")

        # Widget Text principal
        self.text = tk.Text(
            self,
            wrap="none",
            font=self.editor_font,
            undo=True,
            maxundo=-1,
            autoseparators=True,
            borderwidth=0,
            highlightthickness=0,
            padx=8,
            pady=8,
            insertwidth=2,
        )
        self.text.grid(row=0, column=1, sticky="nsew")

        # Scrollbar verticale
        self.vscroll = ttk.Scrollbar(self, orient="vertical", command=self._on_vscroll)
        self.vscroll.grid(row=0, column=2, sticky="ns")

        # Scrollbar horizontale
        self.hscroll = ttk.Scrollbar(self, orient="horizontal", command=self.text.xview)
        self.hscroll.grid(row=1, column=1, sticky="ew")

        self.text.config(yscrollcommand=self._text_yscroll, xscrollcommand=self.hscroll.set)

    def _bind_events(self) -> None:
        self.text.bind("<KeyRelease>", self._on_key_release)
        self.text.bind("<Return>", self._on_return)
        self.text.bind("<Tab>", self._on_tab)
        self.text.bind("<BackSpace>", self._on_backspace)
        self.text.bind("<Configure>", lambda e: self._draw_line_numbers())
        self.text.bind("<MouseWheel>", lambda e: self._draw_line_numbers())
        self.text.bind("<<Modified>>", self._on_modified)

    def _apply_theme(self) -> None:
        theme = get_theme()
        self.text.config(
            bg=theme.background,
            fg=theme.foreground,
            insertbackground=theme.caret,
            selectbackground=theme.selection,
        )
        self.line_canvas.config(bg=theme.line_number_bg)
        self.text.tag_configure("sel", background=theme.selection)

    def _on_vscroll(self, *args):
        self.text.yview(*args)
        self._draw_line_numbers()

    def _text_yscroll(self, first, last):
        self.vscroll.set(first, last)
        self._draw_line_numbers()

    def _draw_line_numbers(self) -> None:
        self.line_canvas.delete("all")
        theme = get_theme()
        first, _ = self.text.yview()
        top = int(float(self.text.index("@0,0")))
        bottom = int(float(self.text.index(f"@0,{self.text.winfo_height()}")))
        y = 0
        for line in range(top, bottom + 1):
            dline = self.text.dlineinfo(f"{line}.0")
            if dline:
                y = dline[1]
                self.line_canvas.create_text(
                    45, y,
                    text=str(line),
                    anchor="ne",
                    font=self.line_font,
                    fill=theme.line_number_fg,
                )

    def _on_key_release(self, event=None) -> None:
        if event and event.keysym in ("Up", "Down", "Left", "Right", "Prior", "Next"):
            return
        self.highlighter.apply()
        self._draw_line_numbers()
        if self.on_change:
            self.on_change()

    def _on_modified(self, event=None) -> None:
        if self._ignore_change:
            return
        flag = self.text.edit_modified()
        if flag:
            self._modified = True
            if self.on_change:
                self.on_change()
        self.text.edit_modified(False)

    def _on_return(self, event=None) -> str:
        line = self.text.get("insert linestart", "insert lineend")
        indent = ""
        for ch in line:
            if ch in " \t":
                indent += ch
            else:
                break
        if line.strip().endswith(":"):
            indent += "    "
        self.text.insert("insert", "\n" + indent)
        self._on_key_release()
        return "break"

    def _on_tab(self, event=None) -> str:
        tab_size = get_config().get("editor.tab_size", 4)
        try:
            sel_first = self.text.index("sel.first")
            sel_last = self.text.index("sel.last")
            if sel_first != sel_last:
                start_line = int(float(sel_first))
                end_line = int(float(sel_last))
                for ln in range(start_line, end_line + 1):
                    self.text.insert(f"{ln}.0", " " * tab_size)
                return "break"
        except tk.TclError:
            pass
        self.text.insert("insert", " " * tab_size)
        return "break"

    def _on_backspace(self, event=None) -> Optional[str]:
        try:
            sel_first = self.text.index("sel.first")
            sel_last = self.text.index("sel.last")
            if sel_first != sel_last:
                return None
        except tk.TclError:
            pass

        tab_size = get_config().get("editor.tab_size", 4)
        line = self.text.get("insert linestart", "insert")
        if line and all(c == " " for c in line) and len(line) > 0 and len(line) % tab_size == 0:
            self.text.delete(f"insert -{tab_size}c", "insert")
            return "break"
        return None

    def set_content(self, content: str) -> None:
        self._ignore_change = True
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.text.edit_modified(False)
        self._modified = False
        self._ignore_change = False
        self.highlighter.apply()
        self._draw_line_numbers()

    def get_content(self) -> str:
        return self.text.get("1.0", "end-1c")

    def is_modified(self) -> bool:
        return self._modified

    def mark_saved(self) -> None:
        self._modified = False
        self.text.edit_modified(False)

    def insert_text(self, text: str) -> None:
        self.text.insert("insert", text)
        self._on_key_release()

    def get_selected_text(self) -> str:
        try:
            return self.text.get("sel.first", "sel.last")
        except tk.TclError:
            return ""

    def replace_selected(self, replacement: str) -> None:
        try:
            self.text.delete("sel.first", "sel.last")
        except tk.TclError:
            pass
        self.text.insert("insert", replacement)

    def find(self, query: str, case_sensitive: bool = False) -> Optional[str]:
        if not query:
            return None
        start = self.text.index("insert")
        pos = self.text.search(query, start, nocase=not case_sensitive, stopindex="end")
        if not pos:
            pos = self.text.search(query, "1.0", nocase=not case_sensitive, stopindex="end")
        if pos:
            end = f"{pos}+{len(query)}c"
            self.text.tag_remove("sel", "1.0", "end")
            self.text.tag_add("sel", pos, end)
            self.text.mark_set("insert", end)
            self.text.see(pos)
        return pos

    def apply_theme(self) -> None:
        self._apply_theme()
        self.highlighter._setup_tags()
        self.highlighter.apply()
        self._draw_line_numbers()
