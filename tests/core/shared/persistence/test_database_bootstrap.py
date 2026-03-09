"""Tests for persistence DB bootstrap helpers."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from core.shared.persistence import database


def test_init_db_creates_task_user_and_audit_tables(
    tmp_path: Path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "database.db"
    monkeypatch.setattr(database, "DATABASE_PATH", db_path)
    database.get_engine.cache_clear()

    try:
        database.init_db()

        with sqlite3.connect(db_path) as connection:
            tables = {
                row[0]
                for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
            }
    finally:
        database.get_engine.cache_clear()

    assert {"task_records", "user_records", "audit_log_records"} <= tables
    assert {"dataset_records", "result_bundle_records", "data_records"} <= tables
