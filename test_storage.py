"""Тесты чтения/записи через временную папку."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from storage import load_records, save_records


SAMPLE = [
    {"id": 1, "title": "Python", "category": "учёба", "amount": 4, "completed": False},
    {"id": 2, "title": "Задача", "category": "практика", "amount": 2, "completed": True},
]


def test_missing_file_returns_empty():
    with TemporaryDirectory() as tmp:
        assert load_records(Path(tmp) / "data.json") == []


def test_round_trip(tmp_dir_factory):
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "data.json"
        save_records(path, SAMPLE)
        restored = load_records(path)
        assert restored == SAMPLE


def test_corrupt_json_raises(tmp_path):
    path = tmp_path / "data.json"
    path.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        load_records(path)


def test_invalid_structure_raises(tmp_path):
    path = tmp_path / "data.json"
    path.write_text(json.dumps([{"id": 1}]), encoding="utf-8")
    with pytest.raises(ValueError):
        load_records(path)


def test_file_not_rewritten_on_bad_start(tmp_path):
    path = tmp_path / "data.json"
    bad = '{"broken": true}'
    path.write_text(bad, encoding="utf-8")
    with pytest.raises(ValueError):
        load_records(path)
    # main.py в таком случае завершится без save; проверяем, что сам файл не тронут
    assert path.read_text(encoding="utf-8") == bad
Запуск:

bash
python -m pytest -v
