from contextlib import closing
from importlib.metadata import EntryPoint
from pathlib import Path
import os
import subprocess
import sys
import tomllib
import sqlite3

import pytest

from home_inventory.database.readonly import open_readonly
from home_inventory.database.schema import ensure_schema
from home_inventory.panel import panel


def test_missing_and_uninitialized(tmp_path, monkeypatch):
    path = tmp_path / "absent" / "test.db"
    monkeypatch.setenv("HOME_INVENTORY_DB", str(path))
    empty = panel()
    assert empty["lines"] == ["Envanter henüz oluşturulmadı.", "Başlamak için: home-inventory init-db"]
    assert not path.parent.exists()
    path.parent.mkdir()
    with closing(sqlite3.connect(path)) as conn:
        conn.execute("CREATE TABLE unrelated(a)")
    before = path.read_bytes(), path.stat().st_mtime_ns
    assert panel() == empty
    assert before == (path.read_bytes(), path.stat().st_mtime_ns)
    assert list(path.parent.iterdir()) == [path]


def test_populated(tmp_path, monkeypatch):
    path = ensure_schema(tmp_path / "a#b?.db")
    monkeypatch.setenv("HOME_INVENTORY_DB", str(path))
    assert panel()["lines"] == ["Henüz eşya yok.", 'Eklemek için: home-inventory add "Ad"']
    with closing(sqlite3.connect(path)) as conn, conn:
        conn.executemany("INSERT INTO items(name,quantity) VALUES (?,?)",
                         [("old", 0), ("masa", 0), ("kalem", 0), ("[kutu]", 0), ("ş"*60, 2)])
    result = panel()
    assert result["title"] == "Evdeki Eşyalar"
    assert result["lines"] == ["5 çeşit · 2 adet", "Tükenen: [kutu], kalem, masa (+1)",
                               "Son eklenen:", "• " + "ş"*37 + "… × 2", "• [kutu] × 0", "• kalem × 0"]
    assert all(isinstance(s, str) and len(s) <= 44 for s in result["lines"])
    with closing(open_readonly(path)) as conn, pytest.raises(sqlite3.OperationalError, match="readonly"):
        conn.execute("INSERT INTO items(name) VALUES ('x')")


def test_entry_point():
    root = Path(__file__).resolve().parents[1]
    project = tomllib.loads((root / "pyproject.toml").read_text())["project"]
    group = "command_center.panels"
    spec = project["entry-points"][group]["inventory"]
    assert EntryPoint("inventory", spec, group).load() is panel
    env = dict(os.environ, PYTHONPATH=str(root / "src"))
    subprocess.run([sys.executable, "-c", "import sys; import home_inventory.panel; "
                    "assert 'command_center' not in sys.modules"], env=env, check=True)


def test_no_depleted_items(tmp_path, monkeypatch):
    path = ensure_schema(tmp_path / "db")
    monkeypatch.setenv("HOME_INVENTORY_DB", str(path))
    with closing(sqlite3.connect(path)) as conn, conn:
        conn.execute("INSERT INTO items(name) VALUES ('cam')")
    assert panel()["lines"][1] == "Tükenen yok"
