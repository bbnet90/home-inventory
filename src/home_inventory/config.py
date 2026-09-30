from __future__ import annotations

from pathlib import Path


class Settings:
    """Application settings for a local-first inventory project."""

    project_root: Path = Path(__file__).resolve().parents[2]
    data_dir: Path = project_root / "data"
    database_path: Path = data_dir / "home_inventory.db"


settings = Settings()
