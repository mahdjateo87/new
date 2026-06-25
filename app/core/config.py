from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "Gestion des Gardes - Clinique ALOUIA"
APP_VERSION = "1.0.0"

VACATION_TYPES = {
    "08H16H": {"label": "08H - 16H", "heures": 8},
    "16H08H": {"label": "16H - 08H (Nuit)", "heures": 16},
    "24H": {"label": "24H", "heures": 24},
    "16H22H": {"label": "16H - 22H", "heures": 6},
    "2SUR2": {"label": "2 sur 2", "heures": 24},
    "2JOUROFF": {"label": "2 jours OFF", "heures": 0},
    "2JOURON": {"label": "2 jours ON", "heures": 16},
}

STATUS_LABELS = {
    "normal": "Présent",
    "absence": "Absence",
    "retard": "Retard",
    "conge": "Congé",
}

STATUS_PREFIX = {
    "absence": "[A]",
    "retard": "[R]",
    "conge": "[C]",
}

DEFAULT_SERVICES = [
    {
        "id": "instrumentiste",
        "nom": "Instrumentiste",
        "vacations": [
            {
                "code": "08H16H",
                "label": "JOURNALIER DE 08H À 16H",
                "colonnes": [
                    "salle 1",
                    "salle 2",
                    "salle 3",
                    "salle 4",
                    "salle 5",
                    "SALLE 6",
                ],
            },
            {
                "code": "24H",
                "label": "24H",
                "colonnes": [
                    "SALLE 6 24H",
                ],
            },
            {
                "code": "16H22H",
                "label": "16H/22H AS",
                "colonnes": [
                    "AS",
                ],
            },
            {
                "code": "16H08H",
                "label": "NUIT DE 16H À 08H",
                "colonnes": [
                    "salle 1",
                    "salle 2",
                    "salle 3",
                ],
            },
        ],
    },
    {
        "id": "hygiene",
        "nom": "Femme d'hygiène",
        "vacations": [
            {
                "code": "08H16H",
                "label": "JOURNALIER DE 08H À 16H",
                "colonnes": [
                    "mat",
                    "chir",
                ],
            },
            {
                "code": "16H08H",
                "label": "NUIT DE 16H À 08H",
                "colonnes": [
                    "mat",
                    "chir",
                ],
            },
        ],
    },
    {
        "id": "sterilisation",
        "nom": "Stérilisation",
        "vacations": [
            {
                "code": "08H16H",
                "label": "JOURNALIER DE 08H À 16H",
                "colonnes": [
                    "jour 08H-16H",
                ],
            },
            {
                "code": "16H08H",
                "label": "NUIT DE 16H À 08H",
                "colonnes": [
                    "nuit 16H-08H",
                ],
            },
            {
                "code": "24H",
                "label": "24H",
                "colonnes": [
                    "24H",
                ],
            },
            {
                "code": "2SUR2",
                "label": "2 SUR 2",
                "colonnes": [
                    "2 sur 2",
                ],
            },
        ],
    },
]

MONTHS_FR = [
    "janvier",
    "février",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "août",
    "septembre",
    "octobre",
    "novembre",
    "décembre",
]


def app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path.home() / ".local" / "share"
    path = base / "CliniqueAlouiaGardes"
    path.mkdir(parents=True, exist_ok=True)
    return path


def config_path() -> Path:
    return data_dir() / "config.json"


def personnel_path() -> Path:
    return data_dir() / "personnel.json"


def gardes_dir() -> Path:
    path = data_dir() / "gardes"
    path.mkdir(parents=True, exist_ok=True)
    return path


def conges_dir() -> Path:
    path = data_dir() / "conges"
    path.mkdir(parents=True, exist_ok=True)
    return path


def exports_dir() -> Path:
    path = data_dir() / "exports"
    path.mkdir(parents=True, exist_ok=True)
    return path
