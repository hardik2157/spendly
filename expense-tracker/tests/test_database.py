"""Database layer tests. These skip until database/db.py implements the functions."""

import sqlite3

import pytest

from database import db

implemented = pytest.mark.skipif(
    not all(hasattr(db, name) for name in ("get_db", "init_db", "seed_db")),
    reason="database/db.py not implemented yet (Step 1)",
)


@pytest.fixture
def conn(tmp_path, monkeypatch):
    test_db = tmp_path / "test.db"
    if hasattr(db, "DATABASE"):
        monkeypatch.setattr(db, "DATABASE", str(test_db))
    connection = db.get_db()
    yield connection
    connection.close()


@implemented
def test_get_db_returns_sqlite_connection(conn):
    assert isinstance(conn, sqlite3.Connection)


@implemented
def test_get_db_sets_row_factory(conn):
    assert conn.row_factory is sqlite3.Row


@implemented
def test_get_db_enables_foreign_keys(conn):
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1


@implemented
def test_init_db_is_idempotent(conn):
    db.init_db()
    db.init_db()  # second call must not raise
    tables = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    assert {"users", "expenses"} <= tables


@implemented
def test_seed_db_inserts_sample_data(conn):
    db.init_db()
    db.seed_db()
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    assert count > 0
