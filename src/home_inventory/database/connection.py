from __future__ import annotations

import sqlite3
from pathlib import Path

from home_inventory.config import settings


def get_connection(database_path: str | Path | None = None) -> sqlite3.Connection:
    """Return a SQLite connection to the local database file."""
    target = Path(database_path) if database_path is not None else settings.database_path
    target.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(target)
    connection.row_factory = sqlite3.Row
    return connection
