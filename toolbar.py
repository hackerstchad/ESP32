"""
Barre d'outils principale.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Tuple

from ..core.constants import BAUD_RATES, DEFAULT_BAUD
from ..core.i18n import translate
from ..core.theme import get_theme


class Toolbar:
    """Barre d'actions flottante en haut de l'application."""

    def __init__(
        self,
        parent: tk.Widget,
        on_connect: Callable,
        on_disconnect: Callable,
        on_refresh_ports: Callable,
        on_upload: Callable,
        on_run: Callable,
        on_stop: Callable,
    ):
        self.parent = parent
        self.theme = get_theme()
        self.callbacks = {
            "connect": on_connect,
            "disconnect": on_disconnect,
            "refresh_ports": on_refresh_ports,
            "upload": on_upload,
            "run": on_run,
            "stop": on_stop,
        }

        self.frame = tk.Frame(parent, bg=self.theme.panel, height=48)
        self.frame.pack(fill=tk.X, side=tk.TOP)
        self.frame.pack_propagate(False)

        self.port_var = tk.StringVar()
        self.baud_var = tk.IntVar(value=DEFAULT_BAUD)
        self.status_var = tk.StringVar(value=translate("status_disconnected"))

        self._build()

    def _build(self) -> None:
        pad = dict(padx=4, pady=6)

        tk.Label(self.frame, text=translate("device"), bg=self.theme.panel, fg=self.theme.muted).pack(side=tk.LEFT, **pad)
        self.port_combo = ttk.Combobox(self.frame, textvariable=self.port_var, width=28, state="readonly")
        self.port_combo.pack(side=tk.LEFT, **pad)

        self.refresh_btn = tk.Button(
            self.frame,
            text="🔄",
            command=self.callbacks["refresh_ports"],
            bg=self.theme.input_bg,
            fg=self.theme.foreground,
            activebackground=self.theme.accent,
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            font=("Segoe UI Emoji", 11),
        )
        self.refresh_btn.pack(side=tk.LEFT, **pad)

        tk.Label(self.frame, text="Baud", bg=self.theme.panel, fg=self.theme.muted).pack(side=tk.LEFT, **pad)
        self.baud_combo = ttk.Combobox(
            self.frame,
            textvariable=self.baud_var,
            values=BAUD_RATES,
            width=10,
            state="readonly",
        )
        self.baud_combo.pack(side=tk.LEFT, **pad)

        self.connect_btn = self._icon_button("🔗", self.callbacks["connect"], translate("connect"))
        self.disconnect_btn = self._icon_button("⛔", self.callbacks["disconnect"], translate("disconnect"))
        self.upload_btn = self._icon_button("⬆️", self.callbacks["upload"], translate("upload"))
        self.run_btn = self._icon_button("▶️", self.callbacks["run"], translate("run"))
        self.stop_btn = self._icon_button("⏹️", self.callbacks["stop"], translate("stop"))

        self.status_label = tk.Label(
            self.frame,
            textvariable=self.status_var,
            bg=self.theme.panel,
            fg=self.theme.muted,
            anchor=tk.E,
        )
        self.status_label.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=12)

    def _icon_button(self, text: str, command: Callable, tooltip: str) -> tk.Button:
        btn = tk.Button(
            self.frame,
            text=text,
            command=command,
            bg=self.theme.input_bg,
            fg=self.theme.foreground,
            activebackground=self.theme.accent,
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            font=("Segoe UI Emoji", 12),
            width=3,
        )
        btn.pack(side=tk.LEFT, padx=2, pady=6)
        self._add_tooltip(btn, tooltip)
        return btn

    def _add_tooltip(self, widget: tk.Widget, text: str) -> None:
        tip = tk.Toplevel(widget)
        tip.withdraw()
        tip.overrideredirect(True)
        label = tk.Label(tip, text=text, bg="#1f2428", fg="#ffffff", padx=6, pady=2)
        label.pack()

        def enter(event, t=tip, l=label):
            t.deiconify()
            t.geometry(f"+{event.x_root + 12}+{event.y_root + 12}")

        def leave(event, t=tip):
            t.withdraw()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def set_ports(self, ports: List[Tuple[str, str]]) -> None:
        values = [p[0] for p in ports]
        self.port_combo["values"] = values
        if values and not self.port_var.get():
            self.port_var.set(values[0])

    def set_status(self, message: str, color: Optional[str] = None) -> None:
        self.status_var.set(message)
        self.status_label.config(fg=color or self.theme.muted)

    def get_selected_port(self) -> str:
        return self.port_var.get()

    def get_selected_baud(self) -> int:
        return self.baud_var.get()

    def set_connected_state(self, connected: bool) -> None:
        state = tk.DISABLED if connected else tk.NORMAL
        self.connect_btn.config(state=state)
        self.disconnect_btn.config(state=tk.NORMAL if connected else tk.DISABLED)
        self.port_combo.config(state=tk.DISABLED if connected else "readonly")
        self.baud_combo.config(state=tk.DISABLED if connected else "readonly")
