from __future__ import annotations

import calendar
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, simpledialog, ttk
from typing import Any

from app.core.config import MONTHS_FR, STATUS_LABELS, VACATION_TYPES
from app.core.excel_io import export_comptage_excel, export_garde_excel, import_garde_excel
from app.core.models import AppConfig, Assignment
from app.core.pdf_forms import generate_demande_conge_pdf, generate_planning_conge_pdf
from app.core.stats import compute_month_stats, get_assignment, iter_service_columns, month_days, month_title, set_assignment
from app.core.storage import load_conges, load_garde, load_personnel, save_conges, save_garde, save_personnel
from app.core.utils import open_file, print_file, send_email_with_attachments


class GardeTab(ttk.Frame):
    def __init__(self, master, config: AppConfig, get_service_id, get_period):
        super().__init__(master)
        self.config = config
        self.get_service_id = get_service_id
        self.get_period = get_period
        self.entries: dict[str, Any] = {}
        self._build()

    def _build(self) -> None:
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=8, pady=8)
        ttk.Button(toolbar, text="Charger", command=self.load_data).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Enregistrer", command=self.save_data).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Exporter Excel", command=self.export_excel).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Importer Excel", command=self.import_excel).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Imprimer", command=self.print_garde).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Envoyer par mail", command=self.email_garde).pack(side="left", padx=4)

        hint = ttk.Label(
            self,
            text=(
                "Astuce (comme Excel) : cliquez une case et tapez le nom — "
                "Entrée/↓ pour descendre, Tab pour la case suivante, flèches pour se déplacer. "
                "Préfixes : [A]=absence, [R]=retard, [C]=congé. Double-clic = options détaillées. "
                "Les modifications sont enregistrées automatiquement."
            ),
            font=("Segoe UI", 8),
            foreground="#555555",
            wraplength=1150,
            justify="left",
        )
        hint.pack(fill="x", padx=10, pady=(0, 2))

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=8, pady=8)

        self.canvas = tk.Canvas(container, highlightthickness=0)
        self.scroll_y = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scroll_x = ttk.Scrollbar(container, orient="horizontal", command=self.canvas.xview)
        self.table = ttk.Frame(self.canvas)
        self.table.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.table, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll_y.pack(side="right", fill="y")
        self.scroll_x.pack(side="bottom", fill="x")

    def load_data(self) -> None:
        service_id = self.get_service_id()
        year, month = self.get_period()
        data = load_garde(service_id, year, month)
        self.entries = data.get("entries", {})
        self._render_table()

    def save_data(self) -> None:
        service_id = self.get_service_id()
        year, month = self.get_period()
        save_garde(
            {
                "service_id": service_id,
                "year": year,
                "month": month,
                "entries": self.entries,
            }
        )
        messagebox.showinfo("Enregistré", "La liste de garde a été enregistrée.")

    def _render_table(self) -> None:
        for child in self.table.winfo_children():
            child.destroy()
        self._cells: dict[tuple[int, int], dict[str, Any]] = {}

        service_id = self.get_service_id()
        year, month = self.get_period()
        service = self.config.service_by_id(service_id)
        if not service:
            return

        columns = iter_service_columns(service)
        tk.Label(
            self.table, text="Date", font=("Segoe UI", 10, "bold"), relief="ridge", bd=1, bg="#dfe6f0"
        ).grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        for idx, (_code, col_name, _key) in enumerate(columns, start=1):
            tk.Label(
                self.table,
                text=col_name,
                font=("Segoe UI", 9, "bold"),
                wraplength=110,
                relief="ridge",
                bd=1,
                bg="#dfe6f0",
            ).grid(row=0, column=idx, padx=0, pady=0, sticky="nsew")

        days = month_days(year, month)
        self._n_rows = len(days)
        self._n_cols = len(columns)
        for row_idx, day in enumerate(days, start=1):
            d = datetime.strptime(day, "%Y-%m-%d")
            weekend = d.weekday() >= 5
            tk.Label(
                self.table,
                text=d.strftime("%d/%m/%Y"),
                relief="ridge",
                bd=1,
                bg="#eef0f5" if not weekend else "#ffe9d6",
                anchor="w",
                padx=4,
            ).grid(row=row_idx, column=0, padx=0, pady=0, sticky="nsew")
            for col_idx, (_vac_code, _col_name, key) in enumerate(columns, start=1):
                assignment = get_assignment(self.entries, day, key)
                var = tk.StringVar(value=assignment.display_name())
                entry = tk.Entry(
                    self.table,
                    textvariable=var,
                    width=16,
                    relief="solid",
                    bd=1,
                    bg="#ffffff" if not weekend else "#fff6ee",
                )
                entry.grid(row=row_idx, column=col_idx, padx=0, pady=0, sticky="nsew")
                pos = (row_idx - 1, col_idx - 1)
                self._cells[pos] = {"entry": entry, "var": var, "day": day, "key": key, "orig": var.get()}
                entry.bind("<FocusOut>", lambda e, p=pos: self._commit_cell(p))
                entry.bind("<Return>", lambda e, p=pos: self._move(p, 1, 0))
                entry.bind("<Down>", lambda e, p=pos: self._move(p, 1, 0))
                entry.bind("<Up>", lambda e, p=pos: self._move(p, -1, 0))
                entry.bind("<Tab>", lambda e, p=pos: self._move(p, 0, 1))
                entry.bind("<Shift-Tab>", lambda e, p=pos: self._move(p, 0, -1))
                entry.bind("<ISO_Left_Tab>", lambda e, p=pos: self._move(p, 0, -1))
                entry.bind("<Double-Button-1>", lambda e, p=pos: self._open_editor(p))

    @staticmethod
    def _parse_cell_text(text: str) -> tuple[str, str]:
        text = text.strip()
        status = "normal"
        for prefix, st in (("[A]", "absence"), ("[R]", "retard"), ("[C]", "conge")):
            if text.upper().startswith(prefix):
                status = st
                text = text[len(prefix):].strip()
                break
        return text, status

    def _commit_cell(self, pos: tuple[int, int]) -> None:
        cell = self._cells.get(pos)
        if not cell:
            return
        value = cell["var"].get().strip()
        if value == cell["orig"]:
            return
        person, status = self._parse_cell_text(value)
        assignment = get_assignment(self.entries, cell["day"], cell["key"])
        assignment.person = person
        assignment.status = status
        assignment.replacement = ""
        set_assignment(self.entries, cell["day"], cell["key"], assignment)
        cell["var"].set(assignment.display_name())
        cell["orig"] = cell["var"].get()
        self._persist()

    def _move(self, pos: tuple[int, int], dr: int, dc: int) -> str:
        self._commit_cell(pos)
        r, c = pos
        nr, nc = r + dr, c + dc
        if nc < 0:
            nc, nr = self._n_cols - 1, nr - 1
        elif nc >= self._n_cols:
            nc, nr = 0, nr + 1
        nr = max(0, min(self._n_rows - 1, nr))
        target = self._cells.get((nr, nc))
        if target:
            target["entry"].focus_set()
            target["entry"].selection_range(0, "end")
        return "break"

    def _open_editor(self, pos: tuple[int, int]) -> str:
        cell = self._cells.get(pos)
        if not cell:
            return "break"
        self._commit_cell(pos)
        assignment = get_assignment(self.entries, cell["day"], cell["key"])
        dialog = CellEditor(self, self.config, assignment)
        self.wait_window(dialog)
        if dialog.result is not None:
            set_assignment(self.entries, cell["day"], cell["key"], dialog.result)
            cell["var"].set(dialog.result.display_name())
            cell["orig"] = cell["var"].get()
            self._persist()
        return "break"

    def _persist(self) -> None:
        service_id = self.get_service_id()
        year, month = self.get_period()
        save_garde(
            {
                "service_id": service_id,
                "year": year,
                "month": month,
                "entries": self.entries,
            }
        )

    def export_excel(self) -> None:
        service_id = self.get_service_id()
        year, month = self.get_period()
        path = export_garde_excel(
            self.config,
            service_id,
            year,
            month,
            {
                "service_id": service_id,
                "year": year,
                "month": month,
                "entries": self.entries,
            },
        )
        messagebox.showinfo("Export", f"Fichier exporté :\n{path}")
        open_file(path)

    def import_excel(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
        if not path:
            return
        try:
            data = import_garde_excel(path, self.config, self.get_service_id())
            self.entries = data.get("entries", {})
            self._render_table()
            messagebox.showinfo("Import", "Fichier Excel importé avec succès.")
        except Exception as exc:
            messagebox.showerror("Erreur", str(exc))

    def print_garde(self) -> None:
        service_id = self.get_service_id()
        year, month = self.get_period()
        path = export_garde_excel(
            self.config,
            service_id,
            year,
            month,
            {"service_id": service_id, "year": year, "month": month, "entries": self.entries},
        )
        print_file(path)

    def email_garde(self) -> None:
        to_email = simpledialog.askstring("Email", "Adresse email du destinataire :")
        if not to_email:
            return
        service_id = self.get_service_id()
        year, month = self.get_period()
        path = export_garde_excel(
            self.config,
            service_id,
            year,
            month,
            {"service_id": service_id, "year": year, "month": month, "entries": self.entries},
        )
        try:
            send_email_with_attachments(
                self.config.smtp,
                to_email,
                f"Liste de garde {month_title(month)} {year}",
                f"Veuillez trouver ci-joint la liste de garde.\n\n{self.config.chef_service}",
                [path],
            )
            messagebox.showinfo("Email", "Email envoyé avec succès.")
        except Exception as exc:
            messagebox.showerror("Erreur", str(exc))


class CellEditor(tk.Toplevel):
    def __init__(self, master, config: AppConfig, assignment: Assignment):
        super().__init__(master)
        self.title("Modifier la vacation")
        self.result: Assignment | None = None
        self.resizable(False, False)
        self.grab_set()

        personnel = [p["nom"] for p in load_personnel()]
        frame = ttk.Frame(self, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Personnel :").grid(row=0, column=0, sticky="w")
        self.person_var = tk.StringVar(value=assignment.person)
        person_cb = ttk.Combobox(frame, textvariable=self.person_var, values=personnel, width=30)
        person_cb.grid(row=0, column=1, pady=4)

        ttk.Label(frame, text="Statut :").grid(row=1, column=0, sticky="w")
        self.status_var = tk.StringVar(value=assignment.status)
        ttk.Combobox(
            frame,
            textvariable=self.status_var,
            values=list(STATUS_LABELS.keys()),
            state="readonly",
            width=28,
        ).grid(row=1, column=1, pady=4)

        ttk.Label(frame, text="Remplaçant (urgence) :").grid(row=2, column=0, sticky="w")
        self.replacement_var = tk.StringVar(value=assignment.replacement)
        ttk.Combobox(frame, textvariable=self.replacement_var, values=personnel, width=30).grid(row=2, column=1, pady=4)

        ttk.Label(frame, text="Note :").grid(row=3, column=0, sticky="nw")
        self.note_text = tk.Text(frame, width=32, height=3)
        self.note_text.grid(row=3, column=1, pady=4)
        self.note_text.insert("1.0", assignment.note)

        btns = ttk.Frame(frame)
        btns.grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(btns, text="Valider", command=self._ok).pack(side="left", padx=5)
        ttk.Button(btns, text="Effacer", command=self._clear).pack(side="left", padx=5)
        ttk.Button(btns, text="Annuler", command=self.destroy).pack(side="left", padx=5)

    def _ok(self) -> None:
        self.result = Assignment(
            person=self.person_var.get().strip(),
            status=self.status_var.get(),
            replacement=self.replacement_var.get().strip(),
            note=self.note_text.get("1.0", "end").strip(),
        )
        self.destroy()

    def _clear(self) -> None:
        self.result = Assignment()
        self.destroy()


class PersonnelTab(ttk.Frame):
    def __init__(self, master, config: AppConfig):
        super().__init__(master)
        self.config = config
        self.personnel = load_personnel()
        self._build()
        self.refresh()

    def _build(self) -> None:
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=8, pady=8)
        ttk.Button(toolbar, text="Ajouter", command=self.add_person).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Modifier", command=self.edit_person).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Supprimer", command=self.delete_person).pack(side="left", padx=4)

        columns = ("nom", "service", "telephone")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=18)
        self.tree.heading("nom", text="Nom")
        self.tree.heading("service", text="Service")
        self.tree.heading("telephone", text="Téléphone")
        self.tree.column("nom", width=220)
        self.tree.column("service", width=180)
        self.tree.column("telephone", width=140)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

    def refresh(self) -> None:
        self.personnel = load_personnel()
        self.tree.delete(*self.tree.get_children())
        for person in self.personnel:
            self.tree.insert("", "end", values=(person.get("nom", ""), person.get("service", ""), person.get("telephone", "")))

    def add_person(self) -> None:
        dialog = PersonEditor(self, self.config)
        self.wait_window(dialog)
        if dialog.result:
            self.personnel.append(dialog.result)
            save_personnel(self.personnel)
            self.refresh()

    def edit_person(self) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        idx = self.tree.index(selected[0])
        dialog = PersonEditor(self, self.config, self.personnel[idx])
        self.wait_window(dialog)
        if dialog.result:
            self.personnel[idx] = dialog.result
            save_personnel(self.personnel)
            self.refresh()

    def delete_person(self) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        if messagebox.askyesno("Confirmer", "Supprimer ce personnel ?"):
            idx = self.tree.index(selected[0])
            del self.personnel[idx]
            save_personnel(self.personnel)
            self.refresh()


class PersonEditor(tk.Toplevel):
    def __init__(self, master, config: AppConfig, person: dict | None = None):
        super().__init__(master)
        self.title("Personnel")
        self.result = None
        self.config = config
        person = person or {}
        self.grab_set()

        frame = ttk.Frame(self, padding=12)
        frame.pack()

        ttk.Label(frame, text="Nom :").grid(row=0, column=0, sticky="w")
        self.nom_var = tk.StringVar(value=person.get("nom", ""))
        ttk.Entry(frame, textvariable=self.nom_var, width=35).grid(row=0, column=1, pady=4)

        ttk.Label(frame, text="Service :").grid(row=1, column=0, sticky="w")
        services = [s["nom"] for s in config.services]
        self.service_var = tk.StringVar(value=person.get("service", services[0] if services else ""))
        ttk.Combobox(frame, textvariable=self.service_var, values=services, width=33).grid(row=1, column=1, pady=4)

        ttk.Label(frame, text="Téléphone :").grid(row=2, column=0, sticky="w")
        self.tel_var = tk.StringVar(value=person.get("telephone", ""))
        ttk.Entry(frame, textvariable=self.tel_var, width=35).grid(row=2, column=1, pady=4)

        ttk.Button(frame, text="Enregistrer", command=self._save).grid(row=3, column=0, columnspan=2, pady=10)

    def _save(self) -> None:
        nom = self.nom_var.get().strip()
        if not nom:
            messagebox.showerror("Erreur", "Le nom est obligatoire.")
            return
        self.result = {
            "nom": nom,
            "service": self.service_var.get().strip(),
            "telephone": self.tel_var.get().strip(),
        }
        self.destroy()


class ComptageTab(ttk.Frame):
    def __init__(self, master, config: AppConfig, get_service_id, get_period):
        super().__init__(master)
        self.config = config
        self.get_service_id = get_service_id
        self.get_period = get_period
        self._build()

    def _build(self) -> None:
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=8, pady=8)
        ttk.Button(toolbar, text="Actualiser", command=self.refresh).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Exporter Excel", command=self.export_excel).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Imprimer", command=self.print_comptage).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Envoyer par mail", command=self.email_comptage).pack(side="left", padx=4)

        columns = ("person", "vacations", "heures", "absences", "retards", "conges", "surcharge")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        headings = {
            "person": "Personnel",
            "vacations": "Vacations",
            "heures": "Heures",
            "absences": "Absences",
            "retards": "Retards",
            "conges": "Congés",
            "surcharge": "Surcharge",
        }
        for col, label in headings.items():
            self.tree.heading(col, text=label)
            self.tree.column(col, width=110 if col != "person" else 180)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)
        self.tree.tag_configure("surcharge", background="#ffc7ce")

    def refresh(self) -> None:
        service_id = self.get_service_id()
        year, month = self.get_period()
        stats = compute_month_stats(self.config, service_id, year, month)
        self.tree.delete(*self.tree.get_children())
        for row in stats:
            tags = ("surcharge",) if row["surcharge"] else ()
            self.tree.insert(
                "",
                "end",
                values=(
                    row["person"],
                    row["total_vacations"],
                    round(row["total_heures"], 1),
                    row["absences"],
                    row["retards"],
                    row["conges"],
                    "OUI" if row["surcharge"] else "NON",
                ),
                tags=tags,
            )

    def export_excel(self) -> None:
        service_id = self.get_service_id()
        year, month = self.get_period()
        path = export_comptage_excel(self.config, service_id, year, month)
        messagebox.showinfo("Export", f"Comptage exporté :\n{path}")
        open_file(path)

    def print_comptage(self) -> None:
        service_id = self.get_service_id()
        year, month = self.get_period()
        path = export_comptage_excel(self.config, service_id, year, month)
        print_file(path)

    def email_comptage(self) -> None:
        to_email = simpledialog.askstring("Email", "Adresse email du destinataire :")
        if not to_email:
            return
        service_id = self.get_service_id()
        year, month = self.get_period()
        path = export_comptage_excel(self.config, service_id, year, month)
        try:
            send_email_with_attachments(
                self.config.smtp,
                to_email,
                f"Comptage vacations {month_title(month)} {year}",
                f"Comptage mensuel des vacations.\n\n{self.config.chef_service}",
                [path],
            )
            messagebox.showinfo("Email", "Email envoyé avec succès.")
        except Exception as exc:
            messagebox.showerror("Erreur", str(exc))


class CongeTab(ttk.Frame):
    def __init__(self, master, config: AppConfig, get_period):
        super().__init__(master)
        self.config = config
        self.get_period = get_period
        self.conges = load_conges()
        self._build()
        self.refresh()

    def _build(self) -> None:
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=8, pady=8)
        ttk.Button(toolbar, text="Nouvelle demande", command=self.new_demande).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Imprimer demande", command=self.print_demande).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Planning congés PDF", command=self.print_planning).pack(side="left", padx=4)

        columns = ("person", "service", "debut", "fin", "jours", "statut")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col, label in [
            ("person", "Personnel"),
            ("service", "Service"),
            ("debut", "Début"),
            ("fin", "Fin"),
            ("jours", "Jours"),
            ("statut", "Statut"),
        ]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=120)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

    def refresh(self) -> None:
        self.conges = load_conges()
        self.tree.delete(*self.tree.get_children())
        for item in self.conges:
            self.tree.insert(
                "",
                "end",
                values=(
                    item.get("person", ""),
                    item.get("service", ""),
                    item.get("date_debut", ""),
                    item.get("date_fin", ""),
                    item.get("nb_jours", ""),
                    item.get("statut", ""),
                ),
            )

    def new_demande(self) -> None:
        dialog = DemandeCongeEditor(self, self.config)
        self.wait_window(dialog)
        if dialog.result:
            dialog.result["id"] = datetime.now().strftime("%Y%m%d%H%M%S")
            self.conges.append(dialog.result)
            save_conges(self.conges)
            self.refresh()

    def print_demande(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Sélection", "Sélectionnez une demande.")
            return
        idx = self.tree.index(selected[0])
        path = generate_demande_conge_pdf(self.config, self.conges[idx])
        open_file(path)

    def print_planning(self) -> None:
        year, month = self.get_period()
        items = [
            c
            for c in self.conges
            if c.get("date_debut", "").endswith(f"/{year:04d}") or c.get("date_debut", "").endswith(f"/{year}")
        ]
        planning = {
            "year": year,
            "month": month,
            "mois_label": month_title(month),
            "items": items,
        }
        path = generate_planning_conge_pdf(self.config, planning)
        open_file(path)


class DemandeCongeEditor(tk.Toplevel):
    def __init__(self, master, config: AppConfig):
        super().__init__(master)
        self.config = config
        self.result = None
        self.grab_set()

        personnel = load_personnel()
        frame = ttk.Frame(self, padding=12)
        frame.pack()

        ttk.Label(frame, text="Personnel :").grid(row=0, column=0, sticky="w")
        self.person_var = tk.StringVar()
        ttk.Combobox(frame, textvariable=self.person_var, values=[p["nom"] for p in personnel], width=30).grid(row=0, column=1)

        ttk.Label(frame, text="Service :").grid(row=1, column=0, sticky="w")
        self.service_var = tk.StringVar(value=config.services[0]["nom"])
        ttk.Combobox(frame, textvariable=self.service_var, values=[s["nom"] for s in config.services], width=28).grid(row=1, column=1)

        ttk.Label(frame, text="Type :").grid(row=2, column=0, sticky="w")
        self.type_var = tk.StringVar(value="Congé annuel")
        ttk.Entry(frame, textvariable=self.type_var, width=32).grid(row=2, column=1)

        ttk.Label(frame, text="Date début (JJ/MM/AAAA) :").grid(row=3, column=0, sticky="w")
        self.debut_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.debut_var, width=32).grid(row=3, column=1)

        ttk.Label(frame, text="Date fin (JJ/MM/AAAA) :").grid(row=4, column=0, sticky="w")
        self.fin_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.fin_var, width=32).grid(row=4, column=1)

        ttk.Label(frame, text="Nombre de jours :").grid(row=5, column=0, sticky="w")
        self.jours_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.jours_var, width=10).grid(row=5, column=1, sticky="w")

        ttk.Label(frame, text="Motif :").grid(row=6, column=0, sticky="nw")
        self.motif = tk.Text(frame, width=32, height=3)
        self.motif.grid(row=6, column=1)

        ttk.Button(frame, text="Enregistrer", command=self._save).grid(row=7, column=0, columnspan=2, pady=10)

    def _save(self) -> None:
        if not self.person_var.get().strip():
            messagebox.showerror("Erreur", "Le personnel est obligatoire.")
            return
        self.result = {
            "person": self.person_var.get().strip(),
            "service": self.service_var.get().strip(),
            "type_conge": self.type_var.get().strip(),
            "date_debut": self.debut_var.get().strip(),
            "date_fin": self.fin_var.get().strip(),
            "nb_jours": self.jours_var.get().strip(),
            "motif": self.motif.get("1.0", "end").strip(),
            "date_demande": datetime.now().strftime("%d/%m/%Y"),
            "statut": "En attente",
        }
        self.destroy()


class ParametresTab(ttk.Frame):
    def __init__(self, master, config: AppConfig, on_save):
        super().__init__(master)
        self.config = config
        self.on_save = on_save
        self._build()

    def _build(self) -> None:
        frame = ttk.Frame(self, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Clinique :").grid(row=0, column=0, sticky="w")
        self.clinique_var = tk.StringVar(value=self.config.clinique)
        ttk.Entry(frame, textvariable=self.clinique_var, width=40).grid(row=0, column=1, pady=4)

        ttk.Label(frame, text="Lieu :").grid(row=1, column=0, sticky="w")
        self.lieu_var = tk.StringVar(value=self.config.lieu)
        ttk.Entry(frame, textvariable=self.lieu_var, width=40).grid(row=1, column=1, pady=4)

        ttk.Label(frame, text="Chef de service :").grid(row=2, column=0, sticky="w")
        self.chef_var = tk.StringVar(value=self.config.chef_service)
        ttk.Entry(frame, textvariable=self.chef_var, width=40).grid(row=2, column=1, pady=4)

        ttk.Label(frame, text="Seuil surcharge (h) :").grid(row=3, column=0, sticky="w")
        self.surcharge_var = tk.StringVar(value=str(self.config.surcharge_heures))
        ttk.Entry(frame, textvariable=self.surcharge_var, width=10).grid(row=3, column=1, sticky="w")

        ttk.Separator(frame).grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)
        ttk.Label(frame, text="Configuration SMTP (envoi email)").grid(row=5, column=0, columnspan=2, sticky="w")

        self.smtp_server = tk.StringVar(value=self.config.smtp.get("server", ""))
        self.smtp_port = tk.StringVar(value=str(self.config.smtp.get("port", 587)))
        self.smtp_email = tk.StringVar(value=self.config.smtp.get("email", ""))
        self.smtp_password = tk.StringVar(value=self.config.smtp.get("password", ""))

        for idx, (label, var) in enumerate(
            [
                ("Serveur SMTP", self.smtp_server),
                ("Port", self.smtp_port),
                ("Email", self.smtp_email),
                ("Mot de passe", self.smtp_password),
            ],
            start=6,
        ):
            ttk.Label(frame, text=label + " :").grid(row=idx, column=0, sticky="w")
            show = "*" if "passe" in label.lower() else None
            ttk.Entry(frame, textvariable=var, width=40, show=show).grid(row=idx, column=1, pady=2)

        ttk.Separator(frame).grid(row=10, column=0, columnspan=2, sticky="ew", pady=10)
        ttk.Label(frame, text="Heures par type de vacation").grid(row=11, column=0, columnspan=2, sticky="w")
        self.hour_vars: dict[str, tk.StringVar] = {}
        row = 12
        for code, meta in VACATION_TYPES.items():
            ttk.Label(frame, text=meta["label"]).grid(row=row, column=0, sticky="w")
            var = tk.StringVar(value=str(self.config.vacation_hours.get(code, meta["heures"])))
            self.hour_vars[code] = var
            ttk.Entry(frame, textvariable=var, width=8).grid(row=row, column=1, sticky="w")
            row += 1

        ttk.Separator(frame).grid(row=row, column=0, columnspan=2, sticky="ew", pady=10)
        row += 1
        ttk.Label(frame, text="Vacations par service (personnalisation)").grid(row=row, column=0, columnspan=2, sticky="w")
        row += 1

        self.services_list = tk.Listbox(frame, height=4, width=45)
        self.services_list.grid(row=row, column=0, columnspan=2, sticky="w", pady=4)
        for service in self.config.services:
            vacs = ", ".join(v["code"] for v in service.get("vacations", []))
            self.services_list.insert("end", f"{service['nom']} : {vacs}")

        row += 1
        ttk.Button(frame, text="Modifier service sélectionné", command=self.edit_service).grid(row=row, column=0, columnspan=2, sticky="w", pady=4)
        row += 1
        ttk.Button(frame, text="Enregistrer les paramètres", command=self.save).grid(row=row, column=0, columnspan=2, pady=12)

    def edit_service(self) -> None:
        selection = self.services_list.curselection()
        if not selection:
            return
        idx = selection[0]
        dialog = ServiceEditor(self, self.config.services[idx])
        self.wait_window(dialog)
        if dialog.result:
            self.config.services[idx] = dialog.result
            self.services_list.delete(0, "end")
            for service in self.config.services:
                vacs = ", ".join(v["code"] for v in service.get("vacations", []))
                self.services_list.insert("end", f"{service['nom']} : {vacs}")

    def save(self) -> None:
        try:
            self.config.surcharge_heures = float(self.surcharge_var.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erreur", "Seuil de surcharge invalide.")
            return
        self.config.clinique = self.clinique_var.get().strip()
        self.config.lieu = self.lieu_var.get().strip()
        self.config.chef_service = self.chef_var.get().strip()
        self.config.smtp = {
            "server": self.smtp_server.get().strip(),
            "port": int(self.smtp_port.get() or 587),
            "email": self.smtp_email.get().strip(),
            "password": self.smtp_password.get(),
            "use_tls": True,
        }
        for code, var in self.hour_vars.items():
            try:
                self.config.vacation_hours[code] = float(var.get().replace(",", "."))
            except ValueError:
                messagebox.showerror("Erreur", f"Heures invalides pour {code}")
                return
        self.on_save(self.config)
        messagebox.showinfo("Paramètres", "Paramètres enregistrés.")


class ServiceEditor(tk.Toplevel):
    def __init__(self, master, service: dict):
        super().__init__(master)
        self.result = None
        self.service = service.copy()
        self.grab_set()

        frame = ttk.Frame(self, padding=12)
        frame.pack(fill="both", expand=True)

        name_row = ttk.Frame(frame)
        name_row.pack(fill="x", pady=(0, 8))
        ttk.Label(name_row, text="Nom du service :").pack(side="left")
        self.nom_var = tk.StringVar(value=service.get("nom", ""))
        ttk.Entry(name_row, textvariable=self.nom_var, width=30).pack(side="left", padx=6)

        self.vacation_frames: list[dict] = []
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill="both", expand=True)

        for vacation in self.service.get("vacations", []):
            self._add_vacation_row(list_frame, vacation)

        ttk.Button(frame, text="Ajouter vacation", command=lambda: self._add_vacation_row(list_frame)).pack(anchor="w", pady=6)
        ttk.Button(frame, text="Enregistrer", command=self._save).pack(anchor="e", pady=8)

    def _add_vacation_row(self, parent, vacation: dict | None = None) -> None:
        vacation = vacation or {"code": "08H16H", "colonnes": ["poste 1"]}
        row_frame = ttk.LabelFrame(parent, text="Vacation", padding=8)
        row_frame.pack(fill="x", pady=4)

        code_var = tk.StringVar(value=vacation.get("code", "08H16H"))
        ttk.Label(row_frame, text="Type :").grid(row=0, column=0, sticky="w")
        ttk.Combobox(
            row_frame,
            textvariable=code_var,
            values=list(VACATION_TYPES.keys()),
            state="readonly",
            width=12,
        ).grid(row=0, column=1, sticky="w")

        ttk.Label(row_frame, text="Colonnes (séparées par ;) :").grid(row=1, column=0, sticky="w")
        cols_var = tk.StringVar(value="; ".join(vacation.get("colonnes", [])))
        ttk.Entry(row_frame, textvariable=cols_var, width=45).grid(row=1, column=1, sticky="w")

        self.vacation_frames.append({"code_var": code_var, "cols_var": cols_var, "frame": row_frame})

    def _save(self) -> None:
        nom = self.nom_var.get().strip()
        if not nom:
            messagebox.showerror("Erreur", "Le nom du service est obligatoire.")
            return
        vacations = []
        for item in self.vacation_frames:
            cols = [c.strip() for c in item["cols_var"].get().split(";") if c.strip()]
            if not cols:
                messagebox.showerror("Erreur", "Chaque vacation doit avoir au moins une colonne.")
                return
            vacations.append({"code": item["code_var"].get(), "colonnes": cols})
        self.service["nom"] = nom
        self.service["vacations"] = vacations
        self.result = self.service
        self.destroy()
