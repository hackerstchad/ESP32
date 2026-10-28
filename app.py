#!/usr/bin/env python3
"""
ESP32 MicroPython IDE
Point d'entrée principal de l'application.
Auteur : hackers_tchad
Date   : 2026
"""

import sys


def main() -> int:
    try:
        from esp32_ide.core.logger import setup_logging
        from esp32_ide.gui.main_window import MainWindow
    except ImportError as exc:
        print(f"Erreur d'importation: {exc}")
        print("Assurez-vous d'installer les dépendances : pip install -r requirements.txt")
        return 1

    setup_logging()
    app = MainWindow()
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
