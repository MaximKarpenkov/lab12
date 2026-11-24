"""Тесты логики без файлов и меню."""
import pytest

from logic import (
    add_record,
    delete_record,
    find_records,
    set_completed,
    statistics,
    validate_records,
)


SAMPLE = [
    {"id": 1, "title": "Python", "category": "учёба", "amount": 4, "completed": False},
    {"id": 2, "title": "Дополнительно", "category": "учёба", "amount": 2, "completed": True},
]


def test_validate_ok():
    validate_records(SAMPLE)


@pytest.mark.parametrize("bad", [
    {"not": "list"},
    [{"id": True, "title": "a", "category": "c", "amount": 1, "completed": False}],
    [{"id": 1, "title": "a", "category": "c", "amount": -1, "completed": False}],
    [{"id": 1, "title": "a", "category": "c", "amount": 1, "completed": "yes"}],
    [{"id": 1, "title": "  ", "category": "c", "amount": 1, "completed": False}],
    [{"id": 1, "title": "a", "category": "c", "amount": 1}],
    [SAMPLE[0], SAMPLE[0]],
])
def test_validate_errors(bad):
    with pytest.raises(ValueError):
        validate_records(bad)


def test_add_assigns_next_id_and_strips():
    records = [dict(r) for r in SAMPLE]
    rec = add_record(records, "  Новая  ", "  учёба ", 3)
    assert rec["id"] == 3
    assert rec["title"] == "Новая"
    assert rec["category"] == "учёба"
    assert rec["completed"] is False


def test_add_invalid_amount():
    with pytest.raises(ValueError):
        add_record([], "a", "b", -1)


def test_find_case_insensitive_and_returns_copies():
    records = [dict(r) for r in SAMPLE]
    found = find_records(records, "PY")
    assert [r["id"] for r in found] == [1]
    found[0]["title"] = "изменено"
    assert records[0]["title"] == "Python"  # исходник не изменён


def test_find_empty_query():
    with pytest.raises(ValueError):
        find_records(SAMPLE, "   ")


def test_set_completed_unknown_and_known():
    records = [dict(r) for r in SAMPLE]
    assert set_completed(records, 999, True) is False
    assert set_completed(records, 1, True) is True
    assert records[0]["completed"] is True


def test_delete_and_id_not_reused():
    records = [dict(r) for r in SAMPLE]
    assert delete_record(records, 1) is True
    assert records[0]["id"] == 2
    new = add_record(records, "x", "y", 0)
    assert new["id"] == 3  # не переиспользуем удалённый 1


def test_statistics_empty():
    stats = statistics([])
    assert stats == {
        "total": 0, "completed": 0, "not_completed": 0,
        "total_amount": 0, "by_category": {},
    }


def test_statistics_two_categories():
    records = [
        {"id": 1, "title": "a", "category": "учёба", "amount": 4, "completed": False},
        {"id": 2, "title": "b", "category": "учёба", "amount": 2, "completed": True},
        {"id": 3, "title": "c", "category": "практика", "amount": 5, "completed": False},
    ]
    stats = statistics(records)
    assert stats["total"] == 3
    assert stats["completed"] == 1
    assert stats["not_completed"] == 2
    assert stats["total_amount"] == 11
    # категории отсортированы по алфавиту: "практика" < "учёба" (кириллица)
    assert list(stats["by_category"]) == ["практика", "учёба"]
