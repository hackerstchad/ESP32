"""
Gestionnaire de projet interne.
"""

from pathlib import Path
from typing import List, Optional

from ..core.config import get_config
from ..core.constants import PROJECTS_DIR


class ProjectManager:
    """Gère l'ouverture, la création et le suivi des projets."""

    def __init__(self):
        self.current_project: Optional[Path] = None

    def create_project(self, name: str) -> Path:
        project_path = PROJECTS_DIR / name
        project_path.mkdir(parents=True, exist_ok=True)
        (project_path / "main.py").write_text(self._default_main(), encoding="utf-8")
        (project_path / "README.md").write_text(f"# {name}\n\nProjet ESP32.\n", encoding="utf-8")
        self.current_project = project_path
        get_config().set("paths.last_project", str(project_path))
        return project_path

    def open_project(self, path: Path) -> Path:
        if not path.exists():
            raise FileNotFoundError(f"Projet introuvable: {path}")
        self.current_project = path
        get_config().set("paths.last_project", str(path))
        return path

    def recent_projects(self) -> List[Path]:
        return []

    @staticmethod
    def _default_main() -> str:
        return '''# Projet ESP32 MicroPython
# Auteur : hackers_tchad

from machine import Pin
import time

led = Pin(2, Pin.OUT)

while True:
    led.value(not led.value())
    time.sleep_ms(500)
'''
