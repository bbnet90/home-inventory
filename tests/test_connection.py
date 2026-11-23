import sqlite3

import pytest

from home_inventory.database.connection import connection_scope
from home_inventory.database.schema import ensure_schema


def test_connection_scope_closes_connection(tmp_path) -> None:
    path = ensure_schema(tmp_path / "scope.db")

    with connection_scope(path) as connection:
        connection.execute("SELECT 1")

    with pytest.raises(sqlite3.ProgrammingError):
        connection.execute("SELECT 1")


def test_connection_scope_commits_on_success(tmp_path) -> None:
    path = ensure_schema(tmp_path / "scope.db")

    with connection_scope(path) as connection:
        connection.execute("INSERT INTO items (name) VALUES ('Lamp')")

    with connection_scope(path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 1


def test_connection_scope_rolls_back_and_closes_on_error(tmp_path) -> None:
    path = ensure_schema(tmp_path / "scope.db")

    with pytest.raises(RuntimeError):
        with connection_scope(path) as connection:
            connection.execute("INSERT INTO items (name) VALUES ('Lamp')")
            raise RuntimeError("boom")

    with pytest.raises(sqlite3.ProgrammingError):
        connection.execute("SELECT 1")

    with connection_scope(path) as fresh:
        assert fresh.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 0
