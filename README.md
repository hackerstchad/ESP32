# ESP32 MicroPython IDE

**Auteur :** `hackers_tchad`  
**Date :** 2026  
**Licence :** MIT  
**Version :** 2026.1.0

---

## Table des matières

1. [Présentation](#présentation)
2. [Fonctionnalités](#fonctionnalités)
3. [Captures et aperçu](#captures-et-apercu)
4. [Architecture](#architecture)
5. [Installation](#installation)
6. [Utilisation](#utilisation)
7. [Configuration](#configuration)
8. [Détection automatique de l'ESP32](#détection-automatique-de-lesp32)
9. [Éditeur de code](#éditeur-de-code)
10. [Terminal REPL](#terminal-repl)
11. [Téléversement](#téléversement)
12. [Flasher un firmware](#flasher-un-firmware)
13. [Raccourcis clavier](#raccourcis-clavier)
14. [Fichiers et dossiers importants](#fichiers-et-dossiers-importants)
15. [Ressources](#ressources)
16. [Applications recommandées](#applications-recommandées)
17. [Livres recommandés](#livres-recommandés)
18. [Communautés](#communautés)
19. [Documentation officielle](#documentation-officielle)
20. [Matériel compatible](#matériel-compatible)
21. [Dépannage](#dépannage)
22. [Roadmap](#roadmap)
23. [Contribuer](#contribuer)
24. [Sécurité](#sécurité)
25. [Historique des versions](#historique-des-versions)
26. [Remerciements](#remerciements)
27. [Contact](#contact)

---

## Présentation

`ESP32 MicroPython IDE` est un environnement de développement intégré (IDE) complet écrit en Python, basé sur `tkinter`. Il est conçu pour détecter automatiquement les cartes **ESP32** branchées en USB, éditer du code MicroPython, interagir avec le **REPL**, transférer des fichiers et exécuter des programmes directement sur le microcontrôleur.

L'objectif est de fournir une expérience fluide pour les développeurs, étudiants, makers et professionnels qui veulent programmer des cartes ESP32 sans dépendre d'outils en ligne complexes. Le logiciel fonctionne hors ligne, garde les projets organisés et fournit une interface moderne avec coloration syntaxique, gestion d'onglets, explorateur de fichiers, terminal intégré et bien plus.

---

## Fonctionnalités

- Détection automatique des cartes ESP32, ESP32-S2, ESP32-S3, ESP32-C3, ESP32-C6 et autres modules compatibles.
- Connexion série via `pyserial` avec choix du port et du baud rate.
- Éditeur de code avec coloration syntaxique Python personnalisée.
- Numérotation des lignes, repli de lignes virtuel, retour à la ligne configurable.
- Gestion d'onglets pour ouvrir plusieurs fichiers simultanément.
- Explorateur de projets en arborescence avec icônes.
- Terminal REPL interactif avec historique des commandes.
- Téléversement de fichiers `main.py`, modules et projets complets vers l'ESP32.
- Exécution directe du code ouvert sur l'ESP32.
- Arrêt du programme en cours avec `Ctrl+C`.
- Redémarrage doux de l'ESP32 depuis l'interface.
- Support de deux langues : français et anglais.
- Thèmes sombre et clair.
- Sauvegarde automatique de la configuration utilisateur.
- Journalisation des événements dans un fichier de log quotidien.
- Barre d'état affichant le port connecté, la position du curseur et le mode.
- Gestionnaire de projets avec création rapide de squelette MicroPython.
- Support des ports USB/UART courants : CP2102, CH340, CH341, FT232, FT2232, native USB.
- Compatible Windows, Linux et macOS.

---

## Captures et aperçu

L'interface est organisée en plusieurs zones :

- Barre de menu en haut.
- Barre d'outils avec actions rapides.
- Panneau latéral gauche : explorateur de projet.
- Zone centrale : éditeur à onglets.
- Panneau inférieur : terminal REPL.
- Barre d'état en bas.

Les couleurs, polices et icônes ont été choisies pour offrir une lecture confortable et une expérience moderne.

---

## Architecture

Le projet est organisé de manière modulaire :

```text
esp32_ide/
├── app.py                 # Point d'entrée principal
├── core/                  # Configuration, thèmes, i18n, logging, constantes
├── editor/                # Éditeur, coloration syntaxique, onglets, arbre projet
├── gui/                   # Fenêtre principale, orchestration, gestionnaire de projet
├── serial/                # Détection, REPL, uploader
├── ui/                    # Composants réutilisables : barre d'outils, terminal, menus
├── utils/                 # Utilitaires divers
└── __init__.py
```

Cette séparation permet de maintenir le code facilement, d'ajouter des fonctionnalités et de tester les modules indépendamment.

---

## Installation

### Prérequis

- Python 3.10 ou supérieur.
- Un câble USB compatible avec votre carte ESP32.
- Les pilotes USB installés (CP210x, CH340, FTDI, etc.) selon votre carte.

### Étapes

1. Clonez ou extrayez le projet :

```bash
git clone https://github.com/hackers_tchad/esp32-ide.git
cd esp32-ide
```

2. Créez un environnement virtuel (recommandé) :

```bash
python -m venv venv
```

3. Activez l'environnement virtuel :

- Windows :

```bash
venv\Scripts\activate
```

- Linux / macOS :

```bash
source venv/bin/activate
```

4. Installez les dépendances :

```bash
pip install -r requirements.txt
```

5. Lancez l'application :

```bash
python -m esp32_ide
```

ou

```bash
python esp32_ide/app.py
```

---

## Utilisation

### Créer un nouveau projet

1. Cliquez sur `Fichier > Nouveau projet` ou utilisez le bouton correspondant.
2. Saisissez le nom du projet.
3. Un dossier est créé dans `~/ESP32Projects/` avec un fichier `main.py` de démarrage.

### Ouvrir un projet existant

1. Cliquez sur `Fichier > Ouvrir un projet`.
2. Sélectionnez le dossier contenant vos fichiers MicroPython.
3. L'arborescence s'affiche dans le panneau de gauche.

### Connecter l'ESP32

1. Branchez la carte ESP32 à un port USB.
2. Cliquez sur `Appareil > Connecter` ou sur l'icône de connexion.
3. L'IDE détecte automatiquement la carte et se connecte.
4. L'état de connexion apparaît dans la barre d'état.

### Éditer et exécuter

1. Ouvrez ou créez un fichier `.py`.
2. Écrivez votre code MicroPython.
3. Cliquez sur `Exécuter` ou appuyez sur `F5` pour lancer le fichier sur l'ESP32.
4. Les résultats s'affichent dans le terminal REPL.

### Téléverser un fichier

1. Sélectionnez le fichier à transférer.
2. Cliquez sur `Appareil > Téléverser`.
3. Le fichier est envoyé vers le système de fichiers de l'ESP32.

### Déconnecter

1. Cliquez sur `Appareil > Déconnecter`.
2. Le port série est fermé proprement.

---

## Configuration

Les préférences sont stockées dans `esp32_ide/config.json`. Vous pouvez modifier :

- Le thème (`dark` ou `light`).
- La police et la taille de l'éditeur.
- La taille des tabulations.
- L'affichage des numéros de ligne.
- Le retour à la ligne automatique.
- La sauvegarde automatique.
- Le baud rate de connexion.
- La langue de l'interface.
- Les dimensions de la fenêtre.

Les modifications sont appliquées au prochain démarrage pour certaines options, et immédiatement pour d'autres.

---

## Détection automatique de l'ESP32

L'IDE identifie les cartes ESP32 en se basant sur les identifiants USB VID/PID connus :

- Silicon Labs CP210x (`10C4:EA60`)
- WCH CH340 / CH341 (`1A86:7523`, `1A86:55D4`)
- FTDI FT232 / FT2232 (`0403:6001`, `0403:6010`)
- Espressif native USB (`303A:0002`, `303A:1001`, `303A:0009`)
- STMicroelectronics VCP (`0483:5740`)
- Raspberry Pi Pico / RP2040 (`2E8A:0005`)

Si plusieurs cartes sont branchées, l'IDE sélectionne la première détectée. Vous pouvez forcer un port préféré dans la configuration.

---

## Éditeur de code

L'éditeur intégré offre :

- Coloration syntaxique Python : mots-clés, chaînes, commentaires, nombres, fonctions, décorateurs.
- Numérotation des lignes.
- Mise en évidence de la ligne active.
- Indentation automatique.
- Conversion des tabulations en espaces.
- Sélection rectangulaire partielle.
- Gestion des modifications non enregistrées (indicateur `●`).
- Support du copier/coller/couper/annuler/rétablir.

Les fichiers sont ouverts dans des onglets. Un double-clic sur un fichier dans l'explorateur l'ouvre dans un nouvel onglet.

---

## Terminal REPL

Le terminal intégré permet d'interagir directement avec l'interpréteur MicroPython de l'ESP32. Vous pouvez :

- Envoyer des commandes Python ligne par ligne.
- Voir les réponses en temps réel.
- Interrompre un programme en cours avec `Ctrl+C`.
- Redémarrer la carte avec `Ctrl+D`.
- Naviguer dans l'historique avec les flèches haut/bas.
- Scroller dans l'historique des échanges.

Le terminal affiche aussi les messages de log de l'application pour faciliter le débogage.

---

## Téléversement

Le transfert de fichiers se fait via le REPL MicroPython. L'IDE envoie le contenu binaire du fichier par blocs de 256 octets. Cette méthode est compatible avec la plupart des cartes ESP32 sans nécessiter d'outils supplémentaires.

Vous pouvez téléverser :

- Le fichier actuellement ouvert.
- Tout un projet (tous les fichiers du dossier).
- Un fichier spécifique choisi par l'utilisateur.

Après le transfert, le fichier est disponible dans le système de fichiers de l'ESP32 et peut être exécuté.

---

## Flasher un firmware

Bien que l'IDE ne flashe pas directement le firmware, il est conçu pour fonctionner avec `esptool` installé via `requirements.txt`. Vous pouvez flasher MicroPython ou un firmware personnalisé avec les commandes suivantes :

```bash
esptool.py --port /dev/ttyUSB0 erase_flash
esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 firmware.bin
```

Remplacez `/dev/ttyUSB0` par le port détecté par l'IDE et `firmware.bin` par le fichier MicroPython adapté à votre carte.

---

## Raccourcis clavier

| Action | Raccourci |
|---|---|
| Nouveau fichier | `Ctrl+N` |
| Ouvrir fichier | `Ctrl+O` |
| Enregistrer | `Ctrl+S` |
| Enregistrer sous | `Ctrl+Shift+S` |
| Fermer l'onglet | `Ctrl+W` |
| Rechercher | `Ctrl+F` |
| Remplacer | `Ctrl+H` |
| Annuler | `Ctrl+Z` |
| Rétablir | `Ctrl+Y` |
| Couper | `Ctrl+X` |
| Copier | `Ctrl+C` |
| Coller | `Ctrl+V` |
| Connecter ESP32 | `F2` |
| Déconnecter ESP32 | `Shift+F2` |
| Exécuter sur ESP32 | `F5` |
| Arrêter l'exécution | `F6` |
| Téléverser fichier | `F7` |
| Redémarrer ESP32 | `F8` |
| Basculer thème | `Ctrl+T` |
| Préférences | `Ctrl+Comma` |
| Quitter | `Alt+F4` |

---

## Fichiers et dossiers importants

- `esp32_ide/app.py` : lanceur principal.
- `esp32_ide/core/config.json` : configuration utilisateur.
- `esp32_ide/logs/` : journaux quotidiens.
- `~/ESP32Projects/` : dossier par défaut des projets utilisateur.
- `requirements.txt` : dépendances Python.
- `README.md` : documentation.

---

## Ressources

### Documentation officielle

- MicroPython : https://micropython.org/
- Documentation MicroPython ESP32 : https://docs.micropython.org/en/latest/esp32/quickref.html
- Espressif ESP32 : https://www.espressif.com/en/products/socs/esp32
- ESP-IDF : https://docs.espressif.com/projects/esp-idf/en/latest/
- pySerial : https://pyserial.readthedocs.io/
- esptool : https://docs.espressif.com/projects/esptool/en/latest/
- Python tkinter : https://docs.python.org/3/library/tkinter.html

### Dépôts et firmwares

- Firmwares MicroPython officiels : https://micropython.org/download/
- Firmwares ESP32 : https://micropython.org/download/?port=esp32
- Firmwares ESP32-S2 : https://micropython.org/download/?port=esp32-s2
- Firmwares ESP32-S3 : https://micropython.org/download/?port=esp32-s3
- Firmwares ESP32-C3 : https://micropython.org/download/?port=esp32-c3
- Firmwares ESP32-C6 : https://micropython.org/download/?port=esp32-c6
- CircuitPython pour ESP32 : https://circuitpython.org/downloads
- ESP32-MPY-Jama : https://github.com/jczic/ESP32-MPY-Jama
- Thonny IDE : https://thonny.org/

### Tutoriels vidéo

- Chaîne MicroPython officielle : https://www.youtube.com/@micropython
- Tutoriels ESP32 en français : recherchez `ESP32 MicroPython hackers_tchad` sur YouTube.

---

## Applications recommandées

- **Thonny** : IDE Python léger avec support MicroPython intégré.
- **Mu Editor** : IDE éducatif pour MicroPython et CircuitPython.
- **ampy** : outil en ligne de commande pour gérer les fichiers sur ESP8266/ESP32.
- **rshell** : shell distant pour MicroPython.
- **mpremote** : outil officiel MicroPython pour interagir avec les cartes.
- **esptool.py** : utilitaire de flashage Espressif.
- **PuTTY / minicom** : terminaux série classiques.
- **VS Code** avec l'extension `MicroPico` ou `Pymakr`.
- **Arduino IDE** pour les projets ESP32 en C/C++.
- **PlatformIO** pour le développement embarqué multiplateforme.

---

## Livres recommandés

- *Programming Microcontrollers with Python* par Elektor.
- *MicroPython for the Internet of Things* par Charles Bell.
- *Python for Microcontrollers: Getting Started with MicroPython* par Donald Norris.
- *The Official ESP32 Book* par Dogan Ibrahim.
- *ESP32 Projects* par Rui Santos et Sara Santos.
- *Practical MicroPython* par Ivo Pullens.
- *MicroPython Cookbook* par Marwan Alsabbagh.
- *Internet of Things with ESP32* par Vedat Ozan Oner.
- *Embedded Systems with ARM Cortex-M Microcontrollers in Assembly Language and C*.
- *Getting Started with ESP32* par Rui Santos.
- *Hands-On MicroPython with the ESP32* par Harish Kumar Garg.
- *MicroPython and the Internet of Things* par Miguel Grinberg.
- *Programming ESP32 in MicroPython* par Gareth Halfacree.
- *Mastering MicroPython* par Christopher Kolonics.
- *IoT Projects with ESP32* par Agus Kurniawan.

---

## Communautés

- Forum MicroPython : https://forum.micropython.org/
- Reddit r/MicroPython : https://www.reddit.com/r/MicroPython/
- Reddit r/esp32 : https://www.reddit.com/r/esp32/
- Discord Espressif : https://discord.gg/espressif
- Groupe Facebook ESP32 Developers.
- Communauté Hackers Tchad : https://github.com/hackers_tchad
- Stack Overflow : tag `micropython` et `esp32`.

---

## Documentation officielle

- MicroPython : https://micropython.org/
- Documentation MicroPython ESP32 : https://docs.micropython.org/en/latest/esp32/quickref.html
- Espressif ESP32 : https://www.espressif.com/en/products/socs/esp32
- ESP-IDF : https://docs.espressif.com/projects/esp-idf/en/latest/
- pySerial : https://pyserial.readthedocs.io/
- esptool : https://docs.espressif.com/projects/esptool/en/latest/
- Python tkinter : https://docs.python.org/3/library/tkinter.html

---

## Matériel compatible

### Cartes ESP32 courantes

- ESP32-DevKitC
- ESP32-WROOM-32
- ESP32-WROVER
- ESP32-S2-DevKitM-1
- ESP32-S3-DevKitC-1
- ESP32-C3-DevKitM-1
- ESP32-C6-DevKitC-1
- NodeMCU-32S
- DOIT DevKit
- Lolin32
- Wemos D1 Mini ESP32
- M5Stack Core
- M5StickC
- LilyGo T-Display
- Unexpected Maker FeatherS2 / TinyS2
- SparkFun ESP32 Thing
- Adafruit Feather ESP32
- Raspberry Pi Pico W (mode compatibilité série)

### Convertisseurs USB/UART

- CP2102 / CP2104
- CH340G / CH340C / CH341
- FT232RL / FT2232H
- Native USB des ESP32-S2/S3/C3/C6

---

## Dépannage

### L'ESP32 n'est pas détecté

1. Vérifiez le câble USB (certains câbles ne transmettent pas les données).
2. Installez les pilotes USB appropriés.
3. Sur Linux, ajoutez votre utilisateur au groupe `dialout` :

```bash
sudo usermod -a -G dialout $USER
```

4. Redémarrez l'ordinateur ou débranchez/rebranchez la carte.
5. Vérifiez que le firmware MicroPython est bien flashé.

### Impossible de se connecter

1. Vérifiez qu'aucun autre programme n'utilise le port série.
2. Essayez un autre baud rate (souvent 115200).
3. Redémarrez la carte ESP32.
4. Consultez les logs dans `esp32_ide/logs/`.

### Le téléversement échoue

1. Assurez-vous que la connexion série est active.
2. Vérifiez que le fichier n'est pas trop volumineux.
3. Essayez de redémarrer la carte en mode REPL.
4. Utilisez `Ctrl+C` pour interrompre tout programme en cours.

### L'interface est lente

1. Désactivez la coloration syntaxique dans les préférences.
2. Réduisez la taille des fichiers ouverts.
3. Fermez les programmes consommateurs de ressources.
4. Augmentez la mémoire allouée si vous utilisez une machine virtuelle.

---

## Roadmap

- [ ] Support du flashage intégré via `esptool`.
- [ ] Support de WebREPL pour connexion sans fil.
- [ ] Complétion de code simple.
- [ ] Gestion des bibliothèques `upip` / `mip`.
- [ ] Débogage pas à pas.
- [ ] Support de l'OTA (Over-The-Air).
- [ ] Intégration d'un visualiseur de broches.
- [ ] Plugin pour générer des schémas de câblage.
- [ ] Mode plein écran amélioré.
- [ ] Export de projets vers des images de firmware.

---

## Contribuer

Les contributions sont les bienvenues !

1. Forkez le dépôt.
2. Créez une branche pour votre fonctionnalité.
3. Respectez le formatage `black`.
4. Ajoutez des tests si possible.
5. Soumettez une pull request.

---

## Sécurité

- Ne connectez jamais une broche GPIO de l'ESP32 à une tension supérieure à 3,3 V.
- Utilisez une alimentation stable pour éviter les corruptions de mémoire flash.
- Sauvegardez vos projets avant toute opération de flashage ou de téléversement.
- Méfiez-vous des firmwares provenant de sources non officielles.

---

## Historique des versions

### 2026.1.0

- Première version publique.
- Détection automatique de l'ESP32.
- Éditeur avec coloration syntaxique.
- Terminal REPL interactif.
- Gestionnaire de projets.
- Thèmes sombre et clair.
- Support français et anglais.

---

## Remerciements

Merci à la communauté MicroPython, à Espressif Systems, aux contributeurs de `pyserial`, `esptool` et `tkinter`, ainsi qu'à tous les makers et développeurs du Tchad et d'ailleurs qui partagent leurs connaissances.

---

## Contact

- Auteur : `hackers_tchad`
- Dépôt GitHub : https://github.com/hackers_tchad/esp32-ide
- Année : 2026

---

**Fin du README.**
