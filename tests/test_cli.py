from home_inventory.cli.main import main
from home_inventory.core.services import InventoryService


def test_cli_add_and_list_command(tmp_path, capsys) -> None:
    database_path = tmp_path / "cli.db"
    service_factory = lambda: InventoryService(database_path)

    exit_code = main(["add", "USB-C Cable", "--category", "electronics", "--quantity", "3"], service_factory=service_factory)
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Created item" in captured.out

    exit_code = main(["list"], service_factory=service_factory)
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "USB-C Cable" in captured.out


def test_cli_update_and_remove_command(tmp_path, capsys) -> None:
    database_path = tmp_path / "cli.db"
    service_factory = lambda: InventoryService(database_path)

    main(["add", "Keyboard"], service_factory=service_factory)
    exit_code = main(["update", "1", "--quantity", "5"], service_factory=service_factory)
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Updated item" in captured.out

    exit_code = main(["remove", "1"], service_factory=service_factory)
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Removed item" in captured.out


def test_cli_find_matches_turkish_names_case_insensitively(tmp_path, capsys) -> None:
    service_factory = lambda: InventoryService(tmp_path / "cli.db")
    main(["add", "Şemsiye"], service_factory=service_factory)
    main(["add", "İstanbul Haritası"], service_factory=service_factory)
    capsys.readouterr()

    assert main(["find", "şem"], service_factory=service_factory) == 0
    assert "Şemsiye" in capsys.readouterr().out

    assert main(["find", "istanbul"], service_factory=service_factory) == 0
    assert "İstanbul Haritası" in capsys.readouterr().out


def test_cli_find_wildcards_are_literal(tmp_path, capsys) -> None:
    service_factory = lambda: InventoryService(tmp_path / "cli.db")
    main(["add", "100% Cotton"], service_factory=service_factory)
    main(["add", "Plain"], service_factory=service_factory)
    capsys.readouterr()

    main(["find", "%"], service_factory=service_factory)
    out = capsys.readouterr().out
    assert "100% Cotton" in out
    assert "Plain" not in out


def test_cli_add_rejects_conflicting_names(tmp_path, capsys) -> None:
    service_factory = lambda: InventoryService(tmp_path / "cli.db")

    exit_code = main(["add", "First", "--name", "Second"], service_factory=service_factory)
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "not both" in captured.err
    assert main(["list"], service_factory=service_factory) == 0
    assert "No items found." in capsys.readouterr().out


def test_cli_add_accepts_same_name_given_twice(tmp_path, capsys) -> None:
    service_factory = lambda: InventoryService(tmp_path / "cli.db")

    assert main(["add", "Lamp", "--name", "Lamp"], service_factory=service_factory) == 0
    assert "Created item #1: Lamp" in capsys.readouterr().out


def test_cli_status_does_not_build_a_service(capsys) -> None:
    def factory():
        raise AssertionError("status must not create a service or touch the database")

    assert main(["status"], service_factory=factory) == 0
    assert "database_path=" in capsys.readouterr().out


def test_cli_huge_quantity_gives_friendly_error(tmp_path, capsys) -> None:
    service_factory = lambda: InventoryService(tmp_path / "cli.db")

    exit_code = main(["add", "Big", "--quantity", "99999999999999999999"], service_factory=service_factory)
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "too large" in captured.err
    assert "SQLite" not in captured.err


def test_cli_update_with_empty_category_clears_it(tmp_path, capsys) -> None:
    service_factory = lambda: InventoryService(tmp_path / "cli.db")
    main(["add", "Lamp", "--category", "home"], service_factory=service_factory)
    capsys.readouterr()

    assert main(["update", "1", "--category", ""], service_factory=service_factory) == 0
    capsys.readouterr()
    main(["show", "1"], service_factory=service_factory)
    assert "Category: -" in capsys.readouterr().out
