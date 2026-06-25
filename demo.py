#!/usr/bin/env python3
"""
Démonstration sans interface graphique.
Lancez : python demo.py

Montre l'import Excel, le comptage et l'export — utile pour tester
sans ouvrir l'application complète.
"""

from __future__ import annotations

from pathlib import Path

from app.core.excel_io import export_comptage_excel, export_garde_excel, import_garde_excel
from app.core.models import AppConfig
from app.core.pdf_forms import generate_demande_conge_pdf, generate_planning_conge_pdf
from app.core.stats import compute_month_stats, month_title
from app.core.storage import save_config, save_garde


def separator(title: str) -> None:
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


def main() -> None:
    separator("DÉMONSTRATION - Gestion des Gardes Clinique ALOUIA")

    config = AppConfig(
        clinique="Clinique ALOUIA",
        lieu="Birtouta",
        chef_service="Mahdjate Oussama",
        configured=True,
    )
    save_config(config)

    print()
    print("✓ Configuration")
    print(f"  Clinique  : {config.clinique}")
    print(f"  Lieu      : {config.lieu}")
    print(f"  Chef      : {config.chef_service}")

    separator("Structure des colonnes (comme votre Excel)")
    for service in config.services:
        print(f"\n  [{service['nom']}]")
        for vac in service["vacations"]:
            label = vac.get("label", vac["code"])
            cols = ", ".join(vac["colonnes"])
            print(f"    • {label} ({vac['code']})")
            print(f"      Colonnes : {cols}")

    example = Path(__file__).parent / "examples" / "exemple_liste_garde_instrumentiste.xlsx"
    if not example.exists():
        print(f"\n✗ Fichier exemple introuvable : {example}")
        return

    separator("Import de votre fichier Excel")
    from openpyxl import load_workbook

    wb = load_workbook(example, data_only=True)
    wb.active = wb["octobre"]
    tmp = Path("/tmp/demo_octobre.xlsx")
    wb.save(tmp)

    data = import_garde_excel(tmp, config, "instrumentiste")
    save_garde(data)
    print(f"  Mois importé : {month_title(data['month'])} {data['year']}")
    print(f"  Jours chargés : {len(data['entries'])}")
    print(f"  Service     : Instrumentiste")

    separator("Comptage mensuel (heures par personne)")
    stats = compute_month_stats(config, "instrumentiste", data["year"], data["month"])
    print(f"  Personnel actif : {len(stats)} personnes")
    print()
    print(f"  {'Personnel':<25} {'Vacations':>10} {'Heures':>8} {'Surcharge':>10}")
    print(f"  {'-'*25} {'-'*10} {'-'*8} {'-'*10}")
    for row in stats[:10]:
        flag = "⚠ OUI" if row["surcharge"] else "non"
        print(
            f"  {row['person'][:25]:<25} {row['total_vacations']:>10} "
            f"{row['total_heures']:>8.0f} {flag:>10}"
        )
    if len(stats) > 10:
        print(f"  ... et {len(stats) - 10} autres personnes")

    separator("Export des fichiers")
    garde_path = export_garde_excel(config, "instrumentiste", data["year"], data["month"], data)
    comptage_path = export_comptage_excel(config, "instrumentiste", data["year"], data["month"])
    pdf_demande = generate_demande_conge_pdf(
        config,
        {
            "person": "Sara Zarzi",
            "service": "Instrumentiste",
            "type_conge": "Congé annuel",
            "date_debut": "15/07/2026",
            "date_fin": "20/07/2026",
            "nb_jours": 6,
            "motif": "Congé planifié",
        },
    )
    pdf_planning = generate_planning_conge_pdf(
        config,
        {
            "year": data["year"],
            "month": data["month"],
            "mois_label": month_title(data["month"]),
            "items": [
                {
                    "person": "Sara Zarzi",
                    "service": "Instrumentiste",
                    "date_debut": "15/07/2026",
                    "date_fin": "20/07/2026",
                    "nb_jours": 6,
                    "statut": "Planifié",
                }
            ],
        },
    )

    print(f"  ✓ Liste de garde Excel : {garde_path}")
    print(f"  ✓ Comptage Excel       : {comptage_path}")
    print(f"  ✓ Demande de congé PDF : {pdf_demande}")
    print(f"  ✓ Planning congés PDF  : {pdf_planning}")

    separator("FIN DE LA DÉMONSTRATION")
    print()
    print("  L'interface graphique complète s'ouvre sur Windows avec :")
    print("    python app/main.py")
    print()
    print("  Ou double-cliquez sur le raccourci après installation.")
    print()


if __name__ == "__main__":
    main()
