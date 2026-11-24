"""Чтение и запись JSON. Без консольных диалогов."""
from __future__ import annotations

import json
from pathlib import Path

from logic import validate_records


def load_records(path: str | Path) -> list[dict]:
    """Читает и валидирует data.json.

    Если файла нет — возвращает [].
    При повреждённом JSON / структуре — бросает ValueError / JSONDecodeError.
    """
    path = Path(path)
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    validate_records(data)
    return data


def save_records(path: str | Path, records: list[dict]) -> None:
    """Пишет записи в UTF-8. Бросает OSError при ошибке записи."""
    path = Path(path)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=2)
