from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.core.config import config_path, conges_dir, gardes_dir, personnel_path
from app.core.models import AppConfig


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def load_config() -> AppConfig:
    return AppConfig.from_dict(_read_json(config_path(), None))


def save_config(config: AppConfig) -> None:
    _write_json(config_path(), config.to_dict())


def load_personnel() -> list[dict[str, Any]]:
    return _read_json(personnel_path(), [])


def save_personnel(personnel: list[dict[str, Any]]) -> None:
    _write_json(personnel_path(), personnel)


def garde_file(service_id: str, year: int, month: int) -> Path:
    return gardes_dir() / f"{service_id}_{year}_{month:02d}.json"


def load_garde(service_id: str, year: int, month: int) -> dict[str, Any]:
    default = {
        "service_id": service_id,
        "year": year,
        "month": month,
        "entries": {},
        "notes": "",
    }
    return _read_json(garde_file(service_id, year, month), default)


def save_garde(data: dict[str, Any]) -> None:
    service_id = data["service_id"]
    year = int(data["year"])
    month = int(data["month"])
    _write_json(garde_file(service_id, year, month), data)


def load_conges() -> list[dict[str, Any]]:
    path = conges_dir() / "demandes.json"
    return _read_json(path, [])


def save_conges(conges: list[dict[str, Any]]) -> None:
    path = conges_dir() / "demandes.json"
    _write_json(path, conges)
