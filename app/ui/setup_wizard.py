from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from app.core.config import VACATION_TYPES
from app.core.models import AppConfig
from app.core.storage import save_config


class SetupWizard(tk.Toplevel):
    def __init__(self, master: tk.Tk, config: AppConfig, on_complete):
        super().__init__(master)
        self.title("Configuration initiale")
        self.config = config
        self.on_complete = on_complete
        self.resizable(False, False)
        self.grab_set()

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Bienvenue - Configuration de l'application",
            font=("Segoe UI", 14, "bold"),
        ).grid(row=0, column=0, columnspan=2, pady=(0, 15))

        ttk.Label(frame, text="Nom de la clinique :").grid(row=1, column=0, sticky="w", pady=4)
        self.clinique_var = tk.StringVar(value=config.clinique)
        ttk.Entry(frame, textvariable=self.clinique_var, width=40).grid(row=1, column=1, pady=4)

        ttk.Label(frame, text="Lieu :").grid(row=2, column=0, sticky="w", pady=4)
        self.lieu_var = tk.StringVar(value=config.lieu)
        ttk.Entry(frame, textvariable=self.lieu_var, width=40).grid(row=2, column=1, pady=4)

        ttk.Label(frame, text="Chef de service :").grid(row=3, column=0, sticky="w", pady=4)
        self.chef_var = tk.StringVar(value=config.chef_service)
        ttk.Entry(frame, textvariable=self.chef_var, width=40).grid(row=3, column=1, pady=4)

        ttk.Label(frame, text="Seuil surcharge (heures/mois) :").grid(row=4, column=0, sticky="w", pady=4)
        self.surcharge_var = tk.StringVar(value=str(config.surcharge_heures))
        ttk.Entry(frame, textvariable=self.surcharge_var, width=10).grid(row=4, column=1, sticky="w", pady=4)

        ttk.Separator(frame).grid(row=5, column=0, columnspan=2, sticky="ew", pady=12)
        ttk.Label(frame, text="Heures par type de vacation (modifiable plus tard)").grid(
            row=6, column=0, columnspan=2, sticky="w"
        )

        self.hour_vars: dict[str, tk.StringVar] = {}
        row = 7
        for code, meta in VACATION_TYPES.items():
            ttk.Label(frame, text=meta["label"]).grid(row=row, column=0, sticky="w", pady=2)
            var = tk.StringVar(value=str(config.vacation_hours.get(code, meta["heures"])))
            self.hour_vars[code] = var
            ttk.Entry(frame, textvariable=var, width=8).grid(row=row, column=1, sticky="w", pady=2)
            row += 1

        ttk.Button(frame, text="Enregistrer et démarrer", command=self._save).grid(
            row=row, column=0, columnspan=2, pady=16
        )

    def _save(self) -> None:
        clinique = self.clinique_var.get().strip()
        chef = self.chef_var.get().strip()
        if not clinique or not chef:
            messagebox.showerror("Erreur", "Le nom de la clinique et le chef de service sont obligatoires.")
            return
        try:
            surcharge = float(self.surcharge_var.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erreur", "Le seuil de surcharge doit être un nombre.")
            return

        self.config.clinique = clinique
        self.config.lieu = self.lieu_var.get().strip()
        self.config.chef_service = chef
        self.config.surcharge_heures = surcharge
        for code, var in self.hour_vars.items():
            try:
                self.config.vacation_hours[code] = float(var.get().replace(",", "."))
            except ValueError:
                messagebox.showerror("Erreur", f"Heures invalides pour {code}.")
                return
        self.config.configured = True
        save_config(self.config)
        self.on_complete()
        self.destroy()
