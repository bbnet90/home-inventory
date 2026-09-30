from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CHECK(length(trim(name)) > 0),
    category TEXT,
    location TEXT,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK(quantity >= 0),
    condition TEXT NOT NULL DEFAULT 'new',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def ensure_schema(database_path: str | Path) -> Path:
    """Create the local SQLite file and the initial schema if absent."""
    target = Path(database_path)
    target.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(target)
    try:
        connection.execute(SCHEMA_SQL)
        connection.commit()
    finally:
        connection.close()

    return target
