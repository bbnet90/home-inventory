import sqlite3

from home_inventory.database.schema import ensure_schema


def test_schema_creates_items_table(tmp_path) -> None:
    database_path = tmp_path / "schema_test.db"
    ensure_schema(database_path)

    with sqlite3.connect(database_path) as connection:
        tables = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='items'"
        ).fetchall()

    assert tables == [("items",)]


def test_default_database_schema_uses_expected_columns(tmp_path) -> None:
    database_path = tmp_path / "inventory.db"
    ensure_schema(database_path)

    with sqlite3.connect(database_path) as connection:
        columns = connection.execute(
            "PRAGMA table_info(items)"
        ).fetchall()

    names = [column[1] for column in columns]
    assert "id" in names
    assert "name" in names
    assert "category" in names
    assert "location" in names
    assert "quantity" in names
    assert "condition" in names
