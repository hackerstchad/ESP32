"""
Barre d'état stylisée.
"""

import tkinter as tk
from typing import Optional

from ..core.theme import get_theme


class StatusBar(tk.Frame):
    """Barre d'état affichant les informations contextuelles."""

    def __init__(self, parent: tk.Widget, **kwargs):
        self.theme = get_theme()
        super().__init__(parent, bg=self.theme.input_bg, height=28, **kwargs)
        self.pack_propagate(False)

        self._status = tk.StringVar(value="Prêt")
        self._port = tk.StringVar(value="—")
        self._position = tk.StringVar(value="Ln 1, Col 1")
        self._mode = tk.StringVar(value="Normal")

        self._status_label = tk.Label(
            self,
            textvariable=self._status,
            bg=self.theme.input_bg,
            fg=self.theme.foreground,
            font=("Segoe UI", 9),
            anchor=tk.W,
            padx=10,
        )
        self._status_label.pack(side=tk.LEFT, fill=tk.Y)

        self._port_label = tk.Label(
            self,
            textvariable=self._port,
            bg=self.theme.input_bg,
            fg=self.theme.muted,
            font=("Segoe UI", 9),
            padx=10,
        )
        self._port_label.pack(side=tk.RIGHT, fill=tk.Y)

        self._position_label = tk.Label(
            self,
            textvariable=self._position,
            bg=self.theme.input_bg,
            fg=self.theme.muted,
            font=("Segoe UI", 9),
            padx=10,
        )
        self._position_label.pack(side=tk.RIGHT, fill=tk.Y)

        self._mode_label = tk.Label(
            self,
            textvariable=self._mode,
            bg=self.theme.input_bg,
            fg=self.theme.accent,
            font=("Segoe UI", 9),
            padx=10,
        )
        self._mode_label.pack(side=tk.RIGHT, fill=tk.Y)

        self._indicators: dict = {}

    @property
    def status(self) -> str:
        return self._status.get()

    @status.setter
    def status(self, value: str) -> None:
        self._status.set(value)

    @property
    def port(self) -> str:
        return self._port.get()

    @port.setter
    def port(self, value: str) -> None:
        self._port.set(value)

    @property
    def position(self) -> str:
        return self._position.get()

    @position.setter
    def position(self, value: str) -> None:
        self._position.set(value)

    @property
    def mode(self) -> str:
        return self._mode.get()

    @mode.setter
    def mode(self, value: str) -> None:
        self._mode.set(value)

    def set_connection_state(self, connected: bool, port: Optional[str] = None) -> None:
        if connected:
            self._port_label.config(fg=self.theme.success)
            self.port = f"● {port or 'Connecté'}"
        else:
            self._port_label.config(fg=self.theme.error)
            self.port = "○ Déconnecté"
