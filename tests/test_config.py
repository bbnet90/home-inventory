from pathlib import Path

from home_inventory.config import settings


def test_default_database_path_is_in_data_directory() -> None:
    assert settings.database_path.name == "home_inventory.db"
    assert settings.database_path.parent.name == "data"
    assert settings.database_path.parent.is_absolute()


def test_data_directory_exists_in_project_root() -> None:
    project_root = Path(__file__).resolve().parents[1]
    assert (project_root / "data").exists()
