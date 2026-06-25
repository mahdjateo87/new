# AGENTS.md

## Cursor Cloud specific instructions

### What this is
Python 3 **Tkinter desktop application** for managing operating-room on-call schedules
("gardes") at the Clinique ALOUIA. There is no backend/web server — it is a single
local GUI app that stores data on disk under `~/.local/share/CliniqueAlouiaGardes/`
(Linux) and reads `examples/exemple_liste_garde_instrumentiste.xlsx` for the demo.

Note: the real application code lives on the `cursor/clinique-alouia-gardes-a085`
branch. The `main` branch only contains a placeholder `README.md`.

### Dependencies / environment
- A virtualenv lives at `.venv` (gitignored). The update script (re)creates it with
  `--system-site-packages` so the system `tkinter` is visible inside the venv.
- `python3-tk` is a **system** package required for the GUI; it is preinstalled in the
  VM snapshot (not part of the update script). If `import tkinter` fails, install it
  with `sudo apt-get install -y python3-tk`.
- Python deps (`openpyxl`, `reportlab`) come from `requirements.txt`.

### Running
- Run the GUI from the repo root as a **module**: `DISPLAY=:1 .venv/bin/python -m app.main`.
  Do NOT use the README's `python app/main.py` — it fails with
  `ModuleNotFoundError: No module named 'app'` because the repo root is not on
  `sys.path` when invoked that way.
- A desktop is served on `DISPLAY=:1` (TigerVNC); the GUI must target that display.
- `demo.py` is a headless smoke test of the core logic (Excel import, monthly stats,
  Excel/PDF export) and needs no display: `.venv/bin/python demo.py`.

### Non-obvious gotchas
- The **Comptage** (count) tab reads assignments from **disk**, not from the in-memory
  grid. After editing the "Liste de garde" grid you must click **Enregistrer** there
  before the Comptage tab (via **Actualiser**) reflects the new hours.
- On first launch (no saved config) a setup wizard appears; running `demo.py` writes a
  config, so delete `~/.local/share/CliniqueAlouiaGardes/` to see the wizard again.

### Lint / test / build
- No linter and no automated test framework are configured. `demo.py` is the de-facto
  smoke test.
- "Build" is Windows-only (PyInstaller via `installer/build_windows.bat`) and does not
  run on Linux; develop/run with the Python commands above instead.
