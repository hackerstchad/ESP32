"""
Fenêtre principale de l'IDE ESP32 MicroPython.
"""

import platform
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Optional

from ..core.config import get_config
from ..core.constants import APP_NAME, APP_VERSION, PROJECTS_DIR
from ..core.i18n import translate
from ..core.logger import get_logger, setup_logging
from ..core.theme import get_theme, set_theme, toggle_theme
from ..editor.code_editor import CodeEditor
from ..editor.project_tree import ProjectTree
from ..editor.tab_manager import TabInfo, TabManager
from ..serial.detector import detect_esp32_port, list_serial_ports
from ..serial.repl import MicroPythonRepl
from ..serial.uploader import Uploader
from ..ui.dialogs import (
    ask_new_project_name,
    ask_open_file,
    ask_project_directory,
    ask_save_file,
    ask_yes_no_cancel,
    show_error,
    show_info,
)
from ..ui.menus import MenuBar
from ..ui.statusbar import StatusBar
from ..ui.terminal import TerminalFrame
from ..ui.toolbar import Toolbar

logger = get_logger(__name__)


class MainWindow:
    """Fenêtre principale orchestrant l'éditeur, le terminal et l'ESP32."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} — {APP_VERSION}")
        self.root.geometry("1400x900")
        self.root.configure(bg=get_theme().background)

        if platform.system() == "Windows":
            try:
                self.root.state("zoomed")
            except Exception:
                pass

        self._theme = get_theme()
        self._repl = MicroPythonRepl()
        self._uploader = Uploader(self._repl)
        self._project_path: Optional[Path] = None
        self._scanning = False
        self._auto_save_job: Optional[str] = None

        self._build_ui()
        self._bind_shortcuts()
        self._start_auto_scan()
        self._load_last_project()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        # Menu principal
        self.menu = MenuBar(self.root, self)
        self.root.config(menu=self.menu.menubar)

        # Barre d'outils
        self.toolbar = Toolbar(self.root, self)
        self.toolbar.pack(fill=tk.X, padx=0, pady=0)

        # Panneau principal
        self.paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=self._theme.border)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Sidebar
        self.sidebar = tk.Frame(self.paned, width=240, bg=self._theme.panel)
        self.sidebar.pack_propagate(False)
        self.project_tree = ProjectTree(self.sidebar, self._open_file_in_tab)

        # Zone centrale
        self.center = tk.Frame(self.paned, bg=self._theme.background)
        self.center.pack(fill=tk.BOTH, expand=True)

        self.paned.add(self.sidebar)
        self.paned.add(self.center)

        # Éditeur
        self.tab_manager = TabManager(self.center, self._create_editor, theme=self._theme)

        # Terminal
        self.terminal = TerminalFrame(self.center, self)
        self.terminal.pack(fill=tk.X, side=tk.BOTTOM)

        # Barre d'état
        self.statusbar = StatusBar(self.root)
        self.statusbar.pack(fill=tk.X, side=tk.BOTTOM)

    def _create_editor(self, parent: tk.Widget) -> CodeEditor:
        return CodeEditor(parent, theme=self._theme)

    def _bind_shortcuts(self) -> None:
        self.root.bind("<Control-n>", lambda e: self.action_new_file())
        self.root.bind("<Control-o>", lambda e: self.action_open_file())
        self.root.bind("<Control-s>", lambda e: self.action_save_file())
        self.root.bind("<Control-Shift-S>", lambda e: self.action_save_as())
        self.root.bind("<Control-r>", lambda e: self.action_run_on_device())
        self.root.bind("<Control-u>", lambda e: self.action_upload_project())
        self.root.bind("<F5>", lambda e: self.action_run_on_device())
        self.root.bind("<F6>", lambda e: self.action_upload_project())

    def run(self) -> None:
        self.root.mainloop()

    # ───────────────────────────── Actions fichiers

    def action_new_project(self) -> None:
        path = ask_new_project_name(self.root)
        if path:
            self.load_project(path)

    def action_open_project(self) -> None:
        path = ask_project_directory(self.root)
        if path:
            self.load_project(path)

    def action_new_file(self) -> None:
        self.tab_manager.add_tab()

    def action_open_file(self) -> None:
        path = ask_open_file(self.root, self._project_path)
        if path:
            self._open_file_in_tab(path)

    def action_save_file(self) -> bool:
        tab = self.tab_manager.current_tab()
        if not tab:
            return False
        if tab.path:
            return self._save_tab(tab, tab.path)
        return self.action_save_as()

    def action_save_as(self) -> bool:
        tab = self.tab_manager.current_tab()
        if not tab:
            return False
        path = ask_save_file(self.root, self._project_path)
        if not path:
            return False
        return self._save_tab(tab, path)

    def _save_tab(self, tab: TabInfo, path: Path) -> bool:
        try:
            path.write_text(tab.editor.get_text(), encoding="utf-8")
            tab.path = path
            tab.mark_saved()
            self.tab_manager.update_titles()
            self.statusbar.status = f"Enregistré {path.name}"
            if self._project_path and path.is_relative_to(self._project_path):
                self.project_tree.refresh()
            return True
        except Exception as e:
            show_error(self.root, f"Erreur d'enregistrement : {e}")
            return False

    def _open_file_in_tab(self, path: Path) -> None:
        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            show_error(self.root, f"Impossible d'ouvrir {path} : {e}")
            return
        self.tab_manager.add_tab(path, content)

    def load_project(self, path: Path) -> None:
        self._project_path = path
        self.project_tree.load_project(path)
        get_config().set("paths.last_project", str(path))
        self.root.title(f"{APP_NAME} — {path.name}")
        main_py = path / "main.py"
        if main_py.exists():
            self._open_file_in_tab(main_py)

    def _load_last_project(self) -> None:
        last = get_config().get("paths.last_project")
        if last and Path(last).exists():
            self.load_project(Path(last))
        else:
            PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
            if not any(PROJECTS_DIR.iterdir()):
                demo = PROJECTS_DIR / "Demo"
                demo.mkdir(exist_ok=True)
                (demo / "main.py").write_text(DEFAULT_DEMO_PY, encoding="utf-8")
            self.load_project(PROJECTS_DIR / "Demo")

    def _on_close(self) -> None:
        for tab in self.tab_manager.tabs:
            if tab.is_modified:
                self.tab_manager.notebook.select(tab.frame)
                result = ask_yes_no_cancel(self.root, "Modifications non enregistrées", f"{tab.title}\n{translate('prompt_save_changes')}")
                if result is True:
                    if not self.action_save_file():
                        return
                elif result is None:
                    return
        self._repl.disconnect()
        self.root.destroy()

    # ───────────────────────────── Connexion ESP32

    def _start_auto_scan(self) -> None:
        self._scan_ports()
        self._schedule_scan()

    def _schedule_scan(self) -> None:
        interval = get_config().get("serial.reconnect_interval_ms", 2000)
        self.root.after(interval, self._scan_ports_and_schedule)

    def _scan_ports_and_schedule(self) -> None:
        if not self._scanning:
            self._scan_ports()
        self._schedule_scan()

    def _scan_ports(self) -> None:
        self._scanning = True
        self.statusbar.status = translate("status_scanning")
        try:
            ports = list_serial_ports()
            esp_ports = [p for p in ports if p.is_esp32]
            self.toolbar.update_ports(ports)
            if self._repl.is_connected:
                self.statusbar.status = translate("status_connected", port=self._repl.port, baud=self._repl.baud_rate)
                return
            preferred = get_config().get("serial.preferred_port")
            target = None
            if preferred:
                for p in esp_ports:
                    if p.port == preferred:
                        target = p
                        break
            if not target and esp_ports:
                target = esp_ports[0]
            if target and get_config().get("serial.auto_connect", True):
                self.root.after(100, lambda: self._connect_async(target.port, target.chip_guess))
            else:
                self.statusbar.status = translate("status_disconnected")
                self.statusbar.set_connection_state(False)
        except Exception as e:
            logger.error(f"Erreur scan ports: {e}")
        finally:
            self._scanning = False

    def action_connect(self, port: str, baud: int) -> None:
        self._connect_async(port, "Manuel")

    def action_disconnect(self) -> None:
        self._repl.disconnect()
        self.statusbar.set_connection_state(False)
        self.statusbar.status = translate("status_disconnected")

    def _connect_async(self, port: str, chip: str) -> None:
        def _task():
            try:
                if self._repl.connect(port, DEFAULT_BAUD):
                    self.root.after(0, lambda: self._on_connected(port, chip))
                else:
                    self.root.after(0, lambda: self._on_connection_failed(port))
            except Exception as e:
                logger.error(f"Connexion échouée: {e}")
                self.root.after(0, lambda: self._on_connection_failed(port))
        threading.Thread(target=_task, daemon=True).start()

    def _on_connected(self, port: str, chip: str) -> None:
        self.statusbar.set_connection_state(True, port)
        self.statusbar.status = f"{chip} connecté sur {port}"
        self.terminal.append_text(f"[+] Connecté à {port} @ {DEFAULT_BAUD}\n", "success")
        get_config().set("serial.preferred_port", port)

    def _on_connection_failed(self, port: str) -> None:
        self.statusbar.set_connection_state(False)
        self.statusbar.status = f"Échec connexion {port}"
        self.terminal.append_text(f"[-] Échec connexion {port}\n", "error")

    # ───────────────────────────── Exécution / Upload

    def action_run_on_device(self) -> None:
        tab = self.tab_manager.current_tab()
        if not tab:
            show_error(self.root, "Aucun fichier actif.")
            return
        if not self._repl.is_connected:
            show_error(self.root, translate("error_no_port"))
            return
        code = tab.editor.get_text()
        name = tab.path.name if tab.path else "script.py"
        self.terminal.append_text(f"[>] Exécution de {name}...\n", "info")

        def _task():
            try:
                if self._uploader.upload_text(code, name):
                    output = self._uploader.run_remote(name)
                    self.root.after(0, lambda: self.terminal.append_text("".join(output), "text"))
                else:
                    self.root.after(0, lambda: show_error(self.root, translate("error_upload", msg="upload annulé")))
            except Exception as e:
                self.root.after(0, lambda: show_error(self.root, translate("error_upload", msg=str(e))))
        threading.Thread(target=_task, daemon=True).start()

    def action_upload_project(self) -> None:
        if not self._project_path:
            show_error(self.root, "Aucun projet ouvert.")
            return
        if not self._repl.is_connected:
            show_error(self.root, translate("error_no_port"))
            return
        self.terminal.append_text(f"[↑] Upload du projet {self._project_path.name}...\n", "info")

        def _task():
            try:
                ok = self._uploader.upload_project(self._project_path)
                self.root.after(0, lambda: self.terminal.append_text(
                    "[+] Upload terminé\n" if ok else "[-] Upload échoué\n", "success" if ok else "error"
                ))
            except Exception as e:
                self.root.after(0, lambda: self.terminal.append_text(f"[-] {e}\n", "error"))
        threading.Thread(target=_task, daemon=True).start()

    def action_send_repl_interrupt(self) -> None:
        if self._repl.is_connected:
            self._repl.interrupt()
            self.terminal.append_text("[\x03] Interruption envoyée\n", "warning")

    def action_soft_reboot(self) -> None:
        if self._repl.is_connected:
            self._repl.soft_reboot()
            self.terminal.append_text("[↻] Redémarrage logiciel\n", "info")

    # ───────────────────────────── Affichage / Préférences

    def action_toggle_theme(self) -> None:
        new_theme = toggle_theme()
        self._theme = new_theme
        self._apply_theme()

    def _apply_theme(self) -> None:
        self.root.configure(bg=self._theme.background)
        # La mise à jour complète des widgets nécessiterait une refonte ;
        # pour l'instant on redémarre l'application.
        show_info(self.root, "Thème mis à jour. Redémarrez l'application pour appliquer pleinement.")

    def action_preferences(self) -> None:
        show_info(self.root, "Les préférences sont stockées dans config.json.")

    def action_about(self) -> None:
        show_info(self.root, f"{APP_NAME}\nVersion {APP_VERSION}\nAuteur : {APP_AUTHOR}\n{APP_YEAR}")


DEFAULT_DEMO_PY = '''# Demo ESP32 MicroPython
# Auteur : hackers_tchad
# Date   : 2026

from machine import Pin, PWM
import time

LED_PIN = 2

led = Pin(LED_PIN, Pin.OUT)
pwm = PWM(led)
pwm.freq(1000)

print("ESP32 prêt")

while True:
    for duty in range(0, 1024, 16):
        pwm.duty(duty)
        time.sleep_ms(2)
    for duty in range(1023, -1, -16):
        pwm.duty(duty)
        time.sleep_ms(2)
'''
