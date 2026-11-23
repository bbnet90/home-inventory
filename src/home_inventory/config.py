from __future__ import annotations

import os
from pathlib import Path

DATABASE_ENV_VAR = "HOME_INVENTORY_DB"
DATABASE_FILENAME = "home_inventory.db"


def _source_checkout_root() -> Path | None:
    """Return the repository root when running from a source checkout, else None."""
    root = Path(__file__).resolve().parents[2]
    return root if (root / "pyproject.toml").is_file() else None


def _default_data_dir() -> Path:
    checkout_root = _source_checkout_root()
    if checkout_root is not None:
        return checkout_root / "data"

    # Regular (non-editable) install: never write next to site-packages.
    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    base_dir = Path(xdg_data_home) if xdg_data_home else Path.home() / ".local" / "share"
    return base_dir / "home-inventory"


def resolve_database_path() -> Path:
    """Resolve the SQLite path: $HOME_INVENTORY_DB, else a sensible local default."""
    override = os.environ.get(DATABASE_ENV_VAR)
    if override:
        return Path(override).expanduser().resolve()
    return _default_data_dir() / DATABASE_FILENAME


class Settings:
    """Application settings for a local-first inventory project."""

    database_path: Path = resolve_database_path()
    data_dir: Path = database_path.parent


settings = Settings()
