#!/usr/bin/env python3
"""Point d'entrée - Gestion des gardes Clinique ALOUIA."""

import sys
from pathlib import Path

# Rend le lancement direct possible (double-clic, raccourci Windows, `python app/main.py`)
# en ajoutant la racine du projet au chemin d'import, en plus de `python -m app.main`.
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.ui.app_window import run_app  # noqa: E402


def main() -> None:
    run_app()


if __name__ == "__main__":
    main()
