from __future__ import annotations

from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.core.config import exports_dir
from app.core.models import AppConfig


def _styles():
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "TitleFr",
        parent=styles["Heading1"],
        fontSize=16,
        alignment=1,
        spaceAfter=12,
    )
    normal = ParagraphStyle(
        "NormalFr",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
    )
    return title, normal


def generate_demande_conge_pdf(config: AppConfig, demande: dict, output: Path | None = None) -> Path:
    if output is None:
        output = exports_dir() / f"demande_conge_{demande.get('id', datetime.now().strftime('%Y%m%d%H%M%S'))}.pdf"

    title_style, normal = _styles()
    doc = SimpleDocTemplate(str(output), pagesize=A4, rightMargin=2 * cm, leftMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm)
    story = []

    story.append(Paragraph(config.clinique, title_style))
    story.append(Paragraph(f"{config.lieu}", normal))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("<b>DEMANDE DE CONGÉ</b>", title_style))
    story.append(Spacer(1, 0.5 * cm))

    data = [
        ["Nom et prénom", demande.get("person", "")],
        ["Service", demande.get("service", "")],
        ["Type de congé", demande.get("type_conge", "")],
        ["Date début", demande.get("date_debut", "")],
        ["Date fin", demande.get("date_fin", "")],
        ["Nombre de jours", str(demande.get("nb_jours", ""))],
        ["Motif", demande.get("motif", "")],
        ["Date de la demande", demande.get("date_demande", datetime.now().strftime("%d/%m/%Y"))],
    ]

    table = Table(data, colWidths=[5 * cm, 11 * cm])
    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph(f"Signature du demandeur : _________________________", normal))
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(f"Avis du chef de service ({config.chef_service}) : _________________________", normal))
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph("Décision de la direction : _________________________", normal))

    doc.build(story)
    return output


def generate_planning_conge_pdf(config: AppConfig, planning: dict, output: Path | None = None) -> Path:
    if output is None:
        output = exports_dir() / f"planning_conge_{planning.get('year')}_{planning.get('month', '')}.pdf"

    title_style, normal = _styles()
    doc = SimpleDocTemplate(str(output), pagesize=A4, rightMargin=1.5 * cm, leftMargin=1.5 * cm, topMargin=2 * cm, bottomMargin=2 * cm)
    story = []

    story.append(Paragraph(config.clinique, title_style))
    story.append(Paragraph(f"Planning des congés - {planning.get('mois_label', '')} {planning.get('year', '')}", title_style))
    story.append(Spacer(1, 0.5 * cm))

    rows = [["Personnel", "Service", "Début", "Fin", "Jours", "Statut"]]
    for item in planning.get("items", []):
        rows.append(
            [
                item.get("person", ""),
                item.get("service", ""),
                item.get("date_debut", ""),
                item.get("date_fin", ""),
                str(item.get("nb_jours", "")),
                item.get("statut", "Planifié"),
            ]
        )

    table = Table(rows, colWidths=[4 * cm, 3.5 * cm, 2.5 * cm, 2.5 * cm, 1.5 * cm, 3 * cm])
    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(f"Établi par : {config.chef_service}", normal))

    doc.build(story)
    return output
