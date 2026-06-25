from __future__ import annotations

import tkinter as tk
from datetime import datetime
from tkinter import ttk

from app.core.config import APP_NAME, MONTHS_FR
from app.core.models import AppConfig
from app.core.storage import save_config
from app.ui.setup_wizard import SetupWizard
from app.ui.tabs import ComptageTab, CongeTab, GardeTab, ParametresTab, PersonnelTab


class AppWindow(tk.Tk):
    def __init__(self, config: AppConfig):
        super().__init__()
        self.config = config
        self.title(APP_NAME)
        self.geometry("1200x750")
        self.minsize(1000, 650)

        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        elif "clam" in style.theme_names():
            style.theme_use("clam")

        self._build_header()
        self._build_tabs()

        if not self.config.configured:
            self.after(200, self._show_setup)

    def _build_header(self) -> None:
        self.header_frame = ttk.Frame(self, padding=10)
        self.header_frame.pack(fill="x")
        header = self.header_frame

        ttk.Label(
            header,
            text=f"{self.config.clinique} — {self.config.lieu}",
            font=("Segoe UI", 14, "bold"),
        ).pack(side="left")

        ttk.Label(
            header,
            text=f"Chef de service : {self.config.chef_service}",
            font=("Segoe UI", 10),
        ).pack(side="right")

        controls = ttk.Frame(header)
        controls.pack(side="right", padx=20)

        now = datetime.now()
        self.year_var = tk.IntVar(value=now.year)
        self.month_var = tk.IntVar(value=now.month)

        ttk.Label(controls, text="Service :").pack(side="left", padx=(0, 4))
        self._service_map = {s["nom"]: s["id"] for s in self.config.services}
        self._service_id_to_name = {s["id"]: s["nom"] for s in self.config.services}
        self.service_display_var = tk.StringVar(value=self.config.services[0]["nom"])
        self.service_combo = ttk.Combobox(
            controls,
            textvariable=self.service_display_var,
            values=[s["nom"] for s in self.config.services],
            width=22,
            state="readonly",
        )
        self.service_combo.pack(side="left", padx=4)
        self.service_combo.bind("<<ComboboxSelected>>", lambda e: self._on_period_change())

        ttk.Label(controls, text="Mois :").pack(side="left", padx=(12, 4))
        self.month_combo = ttk.Combobox(
            controls,
            values=list(range(1, 13)),
            textvariable=self.month_var,
            width=4,
            state="readonly",
        )
        self.month_combo.pack(side="left")
        ttk.Label(controls, text="Année :").pack(side="left", padx=(12, 4))
        self.year_spin = ttk.Spinbox(controls, from_=2020, to=2035, textvariable=self.year_var, width=6)
        self.year_spin.pack(side="left")
        ttk.Button(controls, text="Appliquer", command=self._on_period_change).pack(side="left", padx=8)

    def _build_tabs(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self.garde_tab = GardeTab(
            notebook,
            self.config,
            get_service_id=self.get_service_id,
            get_period=self.get_period,
        )
        self.comptage_tab = ComptageTab(
            notebook,
            self.config,
            get_service_id=self.get_service_id,
            get_period=self.get_period,
        )
        self.personnel_tab = PersonnelTab(notebook, self.config)
        self.conge_tab = CongeTab(notebook, self.config, get_period=self.get_period)
        self.parametres_tab = ParametresTab(notebook, self.config, on_save=self._update_config)

        notebook.add(self.garde_tab, text="Liste de garde")
        notebook.add(self.comptage_tab, text="Comptage")
        notebook.add(self.personnel_tab, text="Personnel")
        notebook.add(self.conge_tab, text="Congés")
        notebook.add(self.parametres_tab, text="Paramètres")

    def get_service_id(self) -> str:
        name = self.service_display_var.get()
        return self._service_map.get(name, self.config.services[0]["id"])

    def get_period(self) -> tuple[int, int]:
        return int(self.year_var.get()), int(self.month_var.get())

    def _on_period_change(self) -> None:
        month = int(self.month_var.get())
        year = int(self.year_var.get())
        service = self.service_display_var.get()
        self.title(f"{APP_NAME} — {service} — {MONTHS_FR[month - 1]} {year}")
        self.garde_tab.load_data()
        self.comptage_tab.refresh()

    def _update_config(self, config: AppConfig) -> None:
        self.config = config
        save_config(config)
        self._service_map = {s["nom"]: s["id"] for s in self.config.services}
        self._service_id_to_name = {s["id"]: s["nom"] for s in self.config.services}
        self.title(APP_NAME)
        if hasattr(self, "header_frame"):
            self.header_frame.destroy()
        self._build_header()

    def _show_setup(self) -> None:
        SetupWizard(self, self.config, on_complete=self._on_setup_complete)

    def _on_setup_complete(self) -> None:
        save_config(self.config)
        self._update_config(self.config)
        self.garde_tab.load_data()
        self.comptage_tab.refresh()


def run_app(config: AppConfig | None = None) -> None:
    from app.core.storage import load_config

    cfg = config or load_config()
    app = AppWindow(cfg)
    app.garde_tab.load_data()
    app.comptage_tab.refresh()
    app.mainloop()
