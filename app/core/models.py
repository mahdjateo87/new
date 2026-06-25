from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from app.core.config import DEFAULT_SERVICES, VACATION_TYPES


@dataclass
class Assignment:
    person: str = ""
    status: str = "normal"
    replacement: str = ""
    note: str = ""

    def display_name(self) -> str:
        name = self.replacement.strip() or self.person.strip()
        if not name:
            return ""
        prefix = {"absence": "[A]", "retard": "[R]", "conge": "[C]"}.get(self.status, "")
        if prefix:
            return f"{prefix} {name}"
        return name

    def to_dict(self) -> dict[str, Any]:
        return {
            "person": self.person,
            "status": self.status,
            "replacement": self.replacement,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "Assignment":
        if not data:
            return cls()
        return cls(
            person=data.get("person", ""),
            status=data.get("status", "normal"),
            replacement=data.get("replacement", ""),
            note=data.get("note", ""),
        )


@dataclass
class AppConfig:
    clinique: str = "Clinique ALOUIA"
    lieu: str = "Birtouta"
    chef_service: str = "Mahdjate Oussama"
    services: list[dict[str, Any]] = field(default_factory=lambda: deepcopy(DEFAULT_SERVICES))
    vacation_hours: dict[str, float] = field(
        default_factory=lambda: {k: v["heures"] for k, v in VACATION_TYPES.items()}
    )
    surcharge_heures: float = 176.0
    configured: bool = False
    smtp: dict[str, Any] = field(
        default_factory=lambda: {
            "server": "",
            "port": 587,
            "email": "",
            "password": "",
            "use_tls": True,
        }
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "clinique": self.clinique,
            "lieu": self.lieu,
            "chef_service": self.chef_service,
            "services": self.services,
            "vacation_hours": self.vacation_hours,
            "surcharge_heures": self.surcharge_heures,
            "configured": self.configured,
            "smtp": self.smtp,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "AppConfig":
        if not data:
            return cls()
        cfg = cls()
        cfg.clinique = data.get("clinique", cfg.clinique)
        cfg.lieu = data.get("lieu", cfg.lieu)
        cfg.chef_service = data.get("chef_service", cfg.chef_service)
        cfg.services = data.get("services", deepcopy(DEFAULT_SERVICES))
        cfg.vacation_hours = data.get(
            "vacation_hours", {k: v["heures"] for k, v in VACATION_TYPES.items()}
        )
        cfg.surcharge_heures = float(data.get("surcharge_heures", cfg.surcharge_heures))
        cfg.configured = bool(data.get("configured", False))
        cfg.smtp = data.get("smtp", cfg.smtp)
        return cfg

    def service_by_id(self, service_id: str) -> dict[str, Any] | None:
        for service in self.services:
            if service["id"] == service_id:
                return service
        return None

    def vacation_label(self, code: str) -> str:
        return VACATION_TYPES.get(code, {}).get("label", code)

    def vacation_hours_for(self, code: str) -> float:
        return float(self.vacation_hours.get(code, VACATION_TYPES.get(code, {}).get("heures", 0)))
