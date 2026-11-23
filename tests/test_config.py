from pathlib import Path

from home_inventory.config import settings


def test_default_database_path_is_in_data_directory() -> None:
    assert settings.database_path.name == "home_inventory.db"
    assert settings.database_path.parent.name == "data"
    assert settings.database_path.parent.is_absolute()


def test_data_directory_exists_in_project_root() -> None:
    project_root = Path(__file__).resolve().parents[1]
    assert (project_root / "data").exists()


def test_env_var_overrides_database_path(monkeypatch, tmp_path) -> None:
    from home_inventory import config

    target = tmp_path / "custom" / "my.db"
    monkeypatch.setenv(config.DATABASE_ENV_VAR, str(target))

    assert config.resolve_database_path() == target.resolve()


def test_installed_package_does_not_write_next_to_site_packages(monkeypatch, tmp_path) -> None:
    from home_inventory import config

    monkeypatch.delenv(config.DATABASE_ENV_VAR, raising=False)
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    monkeypatch.setattr(config, "_source_checkout_root", lambda: None)

    assert config.resolve_database_path() == tmp_path / "home-inventory" / "home_inventory.db"


def test_source_checkout_uses_project_data_directory(monkeypatch, tmp_path) -> None:
    from home_inventory import config

    monkeypatch.delenv(config.DATABASE_ENV_VAR, raising=False)
    monkeypatch.setattr(config, "_source_checkout_root", lambda: tmp_path)

    assert config.resolve_database_path() == tmp_path / "data" / "home_inventory.db"
