from contextlib import closing
import sqlite3

from .config import resolve_database_path
from .database.readonly import InventoryReader, open_readonly


def _short(name, width):
    name = " ".join(name.splitlines())
    return name if len(name) <= width else name[:width - 1] + "…"


def _lines(reader):
    count, units = reader.totals()
    if not count:
        return ["Henüz eşya yok.", 'Eklemek için: home-inventory add "Ad"']
    names, total = reader.depleted()
    depleted = "Tükenen yok"
    if names:
        suffix = f" (+{total - len(names)})" if total > len(names) else ""
        room = 44 - len("Tükenen: " + suffix) - 2 * (len(names) - 1)
        widths = [len(name) for name in names]
        while sum(widths) > room:
            index = widths.index(max(widths))
            widths[index] = min(widths[index] - 1, room)
        depleted = "Tükenen: " + ", ".join(_short(n, w) for n, w in zip(names, widths)) + suffix
    lines = [_short(f"{count} çeşit · {units} adet", 44), depleted, "Son eklenen:"]
    for name, quantity in reader.latest():
        suffix = f" × {quantity}"
        lines.append("• " + _short(name, 42 - len(suffix)) + suffix)
    return lines


def panel() -> dict:
    missing = ["Envanter henüz oluşturulmadı.", "Başlamak için: home-inventory init-db"]
    try:
        with closing(open_readonly(resolve_database_path())) as connection:
            connection.execute("BEGIN")
            lines = _lines(InventoryReader(connection))
    except FileNotFoundError:
        lines = missing
    except sqlite3.OperationalError as exc:
        if str(exc) != "no such table: items":
            raise
        lines = missing
    return {"title": "Evdeki Eşyalar", "lines": lines}
