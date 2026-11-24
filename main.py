"""Консольный интерфейс проекта (вариант 9: задачи по программированию)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from logic import (
    add_record,
    delete_record,
    find_records,
    set_completed,
    statistics,
)
from storage import load_records, save_records

BASE = Path(__file__).resolve().parent
DATA_PATH = BASE / "data.json"

UNIT = "баллов"        # единица измерения для amount
TITLE_LABEL = "задачу"  # для подсказок


# ---------- ввод ----------

def ask_non_empty(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Значение не должно быть пустым.")


def ask_int(prompt: str, min_value: int = 0) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("Введите целое число.")
            continue
        if value < min_value:
            print(f"Число должно быть не меньше {min_value}.")
            continue
        return value


def ask_yes_no(prompt: str) -> bool:
    while True:
        answer = input(prompt).strip().lower()
        if answer in ("да", "yes", "y"):
            return True
        if answer in ("нет", "no", "n"):
            return False
        print("Ответьте 'да' или 'нет'.")


def ask_record_id(prompt: str = "ID: ") -> int:
    return ask_int(prompt, min_value=1)


# ---------- вывод ----------

def print_records(records: list[dict]) -> None:
    if not records:
        print("Нет записей")
        return
    for r in sorted(records, key=lambda x: x["id"]):
        status = "выполнено" if r["completed"] else "не выполнено"
        print(
            f"[{r['id']}] {r['title']} | категория: {r['category']} "
            f"| {r['amount']} {UNIT} | {status}"
        )


def print_statistics(stats: dict) -> None:
    print(f"Всего записей: {stats['total']}")
    print(f"Выполнено: {stats['completed']}")
    print(f"Не выполнено: {stats['not_completed']}")
    print(f"Сумма баллов: {stats['total_amount']}")
    if stats["by_category"]:
        print("По категориям:")
        for name, value in stats["by_category"].items():
            print(f"  {name}: {value}")


# ---------- обработчики ----------

def handle_show(records: list[dict]) -> None:
    print_records(records)


def handle_add(records: list[dict]) -> None:
    title = ask_non_empty("Название: ")
    category = ask_non_empty("Категория: ")
    amount = ask_int("Количество баллов (>= 0): ", min_value=0)
    record = add_record(records, title, category, amount)
    print(f"Добавлено: [{record['id']}] {record['title']}")


def handle_find(records: list[dict]) -> None:
    query = ask_non_empty("Подстрока названия: ")
    found = find_records(records, query)
    if not found:
        print("Ничего не найдено")
    else:
        print_records(found)


def handle_status(records: list[dict]) -> None:
    record_id = ask_record_id()
    completed = ask_yes_no("Отметить как выполнено? (да/нет): ")
    if set_completed(records, record_id, completed):
        print("Статус обновлён")
    else:
        print(f"Запись с ID {record_id} не найдена")


def handle_delete(records: list[dict]) -> None:
    record_id = ask_record_id("ID для удаления: ")
    if not ask_yes_no(f"Удалить запись {record_id}? (да/нет): "):
        print("Удаление отменено")
        return
    if delete_record(records, record_id):
        print("Запись удалена")
    else:
        print(f"Запись с ID {record_id} не найдена")


def handle_stats(records: list[dict]) -> None:
    print_statistics(statistics(records))


def try_save(records: list[dict]) -> bool:
    try:
        save_records(DATA_PATH, records)
    except OSError as error:
        print(f"Ошибка сохранения: {error}")
        return False
    print(f"Данные сохранены в {DATA_PATH.name}")
    return True


def handle_save(records: list[dict]) -> None:
    try_save(records)


# ---------- меню ----------

MENU = """
1 — Показать записи
2 — Добавить запись
3 — Найти записи
4 — Изменить статус
5 — Удалить запись
6 — Показать статистику
7 — Сохранить данные
0 — Выйти
"""

HANDLERS = {
    "1": handle_show,
    "2": handle_add,
    "3": handle_find,
    "4": handle_status,
    "5": handle_delete,
    "6": handle_stats,
    "7": handle_save,
}


def run_menu(records: list[dict]) -> None:
    while True:
        print(MENU)
        choice = input("Выберите пункт: ").strip()
        if choice == "0":
            if ask_yes_no("Сохранить данные перед выходом? (да/нет): "):
                if not try_save(records):
                    continue  # остаёмся в меню при ошибке записи
            return
        handler = HANDLERS.get(choice)
        if handler is None:
            print("Неизвестная команда")
            continue
        handler(records)


def main() -> int:
    try:
        records = load_records(DATA_PATH)
    except json.JSONDecodeError as error:
        print(f"Ошибка JSON в data.json: {error}")
        return 1
    except UnicodeError as error:
        print(f"Ошибка кодировки: {error}")
        return 1
    except ValueError as error:
        print(f"Ошибка структуры данных: {error}")
        return 1
    except OSError as error:
        print(f"Ошибка доступа: {error}")
        return 1

    if not records:
        print("Файл data.json отсутствует или пуст — начинаем с пустого списка")
    else:
        print(f"Загружено записей: {len(records)}")

    run_menu(records)
    return 0


if __name__ == "__main__":
    sys.exit(main())
