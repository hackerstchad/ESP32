"""
Terminal REPL embarqué.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from ..core.constants import REPL_PROMPT
from ..core.theme import get_theme


class TerminalWidget:
    """Console série interactive avec historique de commandes."""

    def __init__(self, parent: tk.Widget, on_user_input: Optional[Callable[[str], None]] = None):
        self.parent = parent
        self.theme = get_theme()
        self.on_user_input = on_user_input
        self.history: list[str] = []
        self.history_index = 0
        self.input_start = "1.0"

        self.frame = tk.Frame(parent, bg=self.theme.panel)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.text = tk.Text(
            self.frame,
            bg=self.theme.background,
            fg=self.theme.foreground,
            insertbackground=self.theme.caret,
            font=("JetBrains Mono", 11),
            relief=tk.FLAT,
            wrap=tk.WORD,
            state=tk.NORMAL,
            padx=8,
            pady=8,
        )
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.frame, command=self.text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.config(yscrollcommand=scrollbar.set)

        self.text.bind("<Return>", self._on_return)
        self.text.bind("<Up>", self._on_history_up)
        self.text.bind("<Down>", self._on_history_down)
        self.text.bind("<Key>", self._protect_prompt)
        self.text.bind("<BackSpace>", self._on_backspace)

        self._tags()
        self.print("ESP32 MicroPython IDE Terminal\n", "info")
        self._show_prompt()

    def _tags(self) -> None:
        self.text.tag_config("info", foreground=self.theme.info)
        self.text.tag_config("success", foreground=self.theme.success)
        self.text.tag_config("warning", foreground=self.theme.warning)
        self.text.tag_config("error", foreground=self.theme.error)
        self.text.tag_config("prompt", foreground=self.theme.accent)
        self.text.tag_config("input", foreground=self.theme.foreground)

    def _show_prompt(self) -> None:
        self.text.insert(tk.END, REPL_PROMPT, "prompt")
        self.text.see(tk.END)
        self.input_start = self.text.index(tk.END)

    def _protect_prompt(self, event) -> Optional[str]:
        if event.keysym in ("Up", "Down", "Left", "Right", "Return", "BackSpace", "Tab"):
            return None
        cursor = self.text.index(tk.INSERT)
        if self.text.compare(cursor, "<", self.input_start):
            return "break"
        return None

    def _on_backspace(self, event) -> Optional[str]:
        cursor = self.text.index(tk.INSERT)
        if self.text.compare(cursor, "<=", self.input_start):
            return "break"
        return None

    def _on_return(self, event) -> str:
        line = self.text.get(self.input_start, tk.END).strip()
        self.text.insert(tk.END, "\n")
        if line:
            self.history.append(line)
            self.history_index = len(self.history)
            if self.on_user_input:
                self.on_user_input(line)
        self._show_prompt()
        return "break"

    def _on_history_up(self, event) -> str:
        if self.history and self.history_index > 0:
            self.history_index -= 1
            self._replace_input(self.history[self.history_index])
        return "break"

    def _on_history_down(self, event) -> str:
        if self.history_index < len(self.history):
            self.history_index += 1
            if self.history_index == len(self.history):
                self._replace_input("")
            else:
                self._replace_input(self.history[self.history_index])
        return "break"

    def _replace_input(self, text: str) -> None:
        self.text.delete(self.input_start, tk.END)
        self.text.insert(self.input_start, text, "input")
        self.text.mark_set(tk.INSERT, tk.END)
        self.text.see(tk.END)

    def print(self, message: str, tag: Optional[str] = None) -> None:
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, message, tag or "")
        self.text.see(tk.END)
        self.text.config(state=tk.NORMAL)

    def print_line(self, message: str, tag: Optional[str] = None) -> None:
        self.print(message + "\n", tag)

    def clear(self) -> None:
        self.text.delete("1.0", tk.END)
        self._show_prompt()

    def enable_input(self, enabled: bool) -> None:
        self.text.config(state=tk.NORMAL if enabled else tk.DISABLED)

    def append_serial(self, data: str) -> None:
        self.print(data)
