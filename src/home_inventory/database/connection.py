from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from home_inventory.config import settings
from home_inventory.database.text import fold_text


def get_connection(database_path: str | Path | None = None) -> sqlite3.Connection:
    """Return a SQLite connection to the local database file."""
    target = Path(database_path) if database_path is not None else settings.database_path
    target.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(target)
    connection.row_factory = sqlite3.Row
    connection.create_function("fold_text", 1, fold_text, deterministic=True)
    return connection


@contextmanager
def connection_scope(database_path: str | Path | None = None) -> Iterator[sqlite3.Connection]:
    """Open a connection, commit on success, roll back on error, always close.

    ``with sqlite3.connect(...)`` only manages the transaction and leaves the
    connection open, so repositories use this wrapper instead.
    """
    connection = get_connection(database_path)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
