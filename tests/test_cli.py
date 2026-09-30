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
