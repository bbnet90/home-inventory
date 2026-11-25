"""Side-effect-free inventory queries."""

import sqlite3
from pathlib import Path


def open_readonly(path: str | Path) -> sqlite3.Connection:
    path = Path(path).resolve()
    # Regular rollback-mode reads retain SQLite's shared locks.
    uri = path.as_uri() + "?mode=ro"
    with path.open("rb") as header:
        wal_mode = header.read(20)[18:20] == bytes((2, 2))
    if wal_mode:
        # Avoid creating or updating the WAL index on a dashboard read.
        try:
            pending = Path(str(path) + "-wal").stat().st_size
        except FileNotFoundError:
            pending = 0
        if pending:
            raise sqlite3.OperationalError("Database has an uncheckpointed WAL")
        uri += "&immutable=1"
    return sqlite3.connect(uri, uri=True)



class InventoryReader:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def totals(self) -> tuple[int, int]:
        # Python integers can sum multiple maximum-sized SQLite quantities.
        count = units = 0
        for (quantity,) in self.connection.execute("SELECT quantity FROM items"):
            count += 1
            units += quantity
        return count, units

    def depleted(self) -> tuple[list[str], int]:
        count, = self.connection.execute("SELECT count(*) FROM items WHERE quantity=0").fetchone()
        rows = self.connection.execute("SELECT name FROM items WHERE quantity=0 ORDER BY id DESC LIMIT 3")
        return [name for name, in rows], count

    def latest(self):
        return self.connection.execute("SELECT name, quantity FROM items ORDER BY id DESC LIMIT 3").fetchall()
