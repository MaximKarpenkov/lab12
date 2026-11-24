"""Логика работы с записями (без консоли и файлов).

Контракты:
  validate_records(records) -> None, бросает ValueError.
  add_record(records, title, category, amount) -> dict: новая запись
      (список изменяется, запись добавляется).
  find_records(records, query) -> list[dict]: копии найденных записей,
      исходный список НЕ меняется.
  set_completed(records, record_id, completed) -> bool:
      True при успехе, False если ID не найден. Список меняется при успехе.
  delete_record(records, record_id) -> bool:
      True при успехе, False если ID не найден. Список меняется при успехе.
  statistics(records) -> dict: агрегаты, исходный список НЕ меняется.
"""
from __future__ import annotations


def validate_records(records) -> None:
    """Проверяет весь набор записей перед началом работы."""
    if not isinstance(records, list):
        raise ValueError("Корень JSON должен быть списком")

    seen_ids: set[int] = set()
    for index, item in enumerate(records):
        where = f"запись #{index}"

        if not isinstance(item, dict):
            raise ValueError(f"{where}: ожидался объект")

        for key in ("id", "title", "category", "amount", "completed"):
            if key not in item:
                raise ValueError(f"{where}: отсутствует поле '{key}'")

        # id
        tid = item["id"]
        if type(tid) is not int:
            raise ValueError(f"{where}: 'id' должен быть целым (не bool)")
        if tid <= 0:
            raise ValueError(f"{where}: 'id' должен быть положительным")
        if tid in seen_ids:
            raise ValueError(f"{where}: повторяющийся id={tid}")
        seen_ids.add(tid)

        # title / category
        for key in ("title", "category"):
            value = item[key]
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{where}: '{key}' должен быть непустой строкой")

        # amount
        amount = item["amount"]
        if type(amount) is not int:
            raise ValueError(f"{where}: 'amount' должен быть целым (не bool)")
        if amount < 0:
            raise ValueError(f"{where}: 'amount' не может быть отрицательным")

        # completed
        if type(item["completed"]) is not bool:
            raise ValueError(f"{where}: 'completed' должен быть bool")


def _next_id(records: list[dict]) -> int:
    return max((r["id"] for r in records), default=0) + 1


def add_record(
    records: list[dict],
    title: str,
    category: str,
    amount: int,
) -> dict:
    """Добавляет запись и возвращает её. Валидирует аргументы."""
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Название не должно быть пустым")
    if not isinstance(category, str) or not category.strip():
        raise ValueError("Категория не должна быть пустой")
    if type(amount) is not int:
        raise ValueError("Количество должно быть целым числом")
    if amount < 0:
        raise ValueError("Количество не может быть отрицательным")

    record = {
        "id": _next_id(records),
        "title": title.strip(),
        "category": category.strip(),
        "amount": amount,
        "completed": False,
    }
    records.append(record)
    return record


def find_records(records: list[dict], query: str) -> list[dict]:
    """Поиск по подстроке названия без учёта регистра."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Поисковый запрос не должен быть пустым")
    needle = query.strip().lower()
    return [dict(r) for r in records if needle in r["title"].lower()]


def set_completed(records: list[dict], record_id: int, completed: bool) -> bool:
    """Явно устанавливает статус. True — успех, False — ID не найден."""
    if type(completed) is not bool:
        raise ValueError("Статус должен быть bool")
    for record in records:
        if record["id"] == record_id:
            record["completed"] = completed
            return True
    return False


def delete_record(records: list[dict], record_id: int) -> bool:
    """Удаляет запись по ID. True — успех, False — ID не найден."""
    for index, record in enumerate(records):
        if record["id"] == record_id:
            del records[index]
            return True
    return False


def statistics(records: list[dict]) -> dict:
    """Агрегаты по текущему списку. Исходные данные не меняются."""
    total = len(records)
    completed = sum(1 for r in records if r["completed"])
    total_amount = sum(r["amount"] for r in records)

    by_category: dict[str, int] = {}
    for r in records:
        category = r["category"].strip()
        by_category[category] = by_category.get(category, 0) + r["amount"]

    return {
        "total": total,
        "completed": completed,
        "not_completed": total - completed,
        "total_amount": total_amount,
        "by_category": dict(sorted(by_category.items())),
    }
