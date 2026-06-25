from __future__ import annotations

import calendar
from collections import defaultdict
from typing import Any

from app.core.config import MONTHS_FR
from app.core.models import AppConfig, Assignment
from app.core.storage import load_garde


def cell_key(vacation_code: str, column: str) -> str:
    return f"{vacation_code}::{column}"


def parse_cell_key(key: str) -> tuple[str, str]:
    vacation_code, column = key.split("::", 1)
    return vacation_code, column


def iter_service_columns(service: dict[str, Any]) -> list[tuple[str, str, str]]:
    columns: list[tuple[str, str, str]] = []
    for vacation in service.get("vacations", []):
        code = vacation["code"]
        for col in vacation.get("colonnes", []):
            columns.append((code, col, cell_key(code, col)))
    return columns


def month_days(year: int, month: int) -> list[str]:
    count = calendar.monthrange(year, month)[1]
    return [f"{year}-{month:02d}-{day:02d}" for day in range(1, count + 1)]


def get_assignment(entries: dict[str, Any], day: str, key: str) -> Assignment:
    day_entries = entries.get(day, {})
    return Assignment.from_dict(day_entries.get(key))


def set_assignment(entries: dict[str, Any], day: str, key: str, assignment: Assignment) -> None:
    entries.setdefault(day, {})[key] = assignment.to_dict()


def effective_person(assignment: Assignment) -> str:
    name = (assignment.replacement or assignment.person).strip()
    return name


def compute_month_stats(
    config: AppConfig,
    service_id: str,
    year: int,
    month: int,
) -> list[dict[str, Any]]:
    service = config.service_by_id(service_id)
    if not service:
        return []

    garde = load_garde(service_id, year, month)
    entries = garde.get("entries", {})
    columns = iter_service_columns(service)

    stats: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "person": "",
            "vacation_counts": defaultdict(int),
            "total_vacations": 0,
            "total_heures": 0.0,
            "absences": 0,
            "retards": 0,
            "conges": 0,
        }
    )

    for day in month_days(year, month):
        for vacation_code, _column, key in columns:
            assignment = get_assignment(entries, day, key)
            person = effective_person(assignment)
            if not person:
                continue

            person_key = person.lower()
            row = stats[person_key]
            row["person"] = person
            if assignment.status == "absence":
                row["absences"] += 1
                continue
            if assignment.status == "retard":
                row["retards"] += 1
            if assignment.status == "conge":
                row["conges"] += 1
                continue

            hours = config.vacation_hours_for(vacation_code)
            row["vacation_counts"][vacation_code] += 1
            row["total_vacations"] += 1
            row["total_heures"] += hours

    result = []
    for row in stats.values():
        surcharge = row["total_heures"] > config.surcharge_heures
        result.append(
            {
                **row,
                "vacation_counts": dict(row["vacation_counts"]),
                "surcharge": surcharge,
            }
        )

    result.sort(key=lambda item: item["person"].lower())
    return result


def month_title(month: int) -> str:
    return MONTHS_FR[month - 1]
