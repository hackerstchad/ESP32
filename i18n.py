"""
Support multilingue simplifié.
"""

from .config import get_config

MESSAGES = {
    "fr": {
        "app_title": "ESP32 MicroPython IDE",
        "file": "Fichier",
        "edit": "Édition",
        "view": "Affichage",
        "device": "Appareil",
        "tools": "Outils",
        "help": "Aide",
        "new_project": "Nouveau projet",
        "open_project": "Ouvrir un projet",
        "save": "Enregistrer",
        "save_as": "Enregistrer sous",
        "close": "Fermer",
        "exit": "Quitter",
        "undo": "Annuler",
        "redo": "Rétablir",
        "cut": "Couper",
        "copy": "Copier",
        "paste": "Coller",
        "find": "Rechercher",
        "replace": "Remplacer",
        "preferences": "Préférences",
        "connect": "Connecter",
        "disconnect": "Déconnecter",
        "refresh_ports": "Rafraîchir les ports",
        "upload": "Téléverser",
        "run": "Exécuter",
        "stop": "Arrêter",
        "terminal": "Terminal",
        "console": "Console",
        "explorer": "Explorateur",
        "status_ready": "Prêt",
        "status_connected": "Connecté à {port} @ {baud}",
        "status_disconnected": "Déconnecté",
        "status_scanning": "Détection en cours...",
        "error_no_port": "Aucun port ESP32 détecté.",
        "error_upload": "Échec du téléversement : {msg}",
        "success_upload": "Téléversement réussi.",
        "prompt_save_changes": "Voulez-vous enregistrer les modifications ?",
        "about": "À propos",
    },
    "en": {
        "app_title": "ESP32 MicroPython IDE",
        "file": "File",
        "edit": "Edit",
        "view": "View",
        "device": "Device",
        "tools": "Tools",
        "help": "Help",
        "new_project": "New project",
        "open_project": "Open project",
        "save": "Save",
        "save_as": "Save as",
        "close": "Close",
        "exit": "Exit",
        "undo": "Undo",
        "redo": "Redo",
        "cut": "Cut",
        "copy": "Copy",
        "paste": "Paste",
        "find": "Find",
        "replace": "Replace",
        "preferences": "Preferences",
        "connect": "Connect",
        "disconnect": "Disconnect",
        "refresh_ports": "Refresh ports",
        "upload": "Upload",
        "run": "Run",
        "stop": "Stop",
        "terminal": "Terminal",
        "console": "Console",
        "explorer": "Explorer",
        "status_ready": "Ready",
        "status_connected": "Connected to {port} @ {baud}",
        "status_disconnected": "Disconnected",
        "status_scanning": "Scanning...",
        "error_no_port": "No ESP32 port detected.",
        "error_upload": "Upload failed: {msg}",
        "success_upload": "Upload successful.",
        "prompt_save_changes": "Do you want to save changes?",
        "about": "About",
    },
}


def translate(key: str, **kwargs) -> str:
    lang = get_config().get("ui.language", "fr")
    text = MESSAGES.get(lang, MESSAGES["fr"]).get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text


def set_language(lang: str) -> None:
    get_config().set("ui.language", lang)
