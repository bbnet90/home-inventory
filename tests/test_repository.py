from home_inventory.database.repositories import InventoryRepository


def test_repository_creates_and_fetches_item(tmp_path) -> None:
    repo = InventoryRepository(tmp_path / "inventory.db")

    item = repo.create_item(
        name="Desk",
        category="Office",
        location="Room 1",
        quantity=1,
        condition="new",
    )

    fetched = repo.get_item_by_id(item.id)
    assert fetched is not None
    assert fetched.name == "Desk"
    assert fetched.quantity == 1


def test_repository_lists_and_searches_items(tmp_path) -> None:
    repo = InventoryRepository(tmp_path / "inventory.db")
    repo.create_item(name="Laptop", quantity=1, condition="good")
    repo.create_item(name="Keyboard", quantity=2, condition="good")

    items = repo.list_items()
    matches = repo.search_items_by_name("LAP")

    assert len(items) == 2
    assert len(matches) == 1
    assert matches[0].name == "Laptop"


def test_repository_updates_and_deletes_item(tmp_path) -> None:
    repo = InventoryRepository(tmp_path / "inventory.db")
    item = repo.create_item(name="Table", quantity=1, condition="fair")

    updated = repo.update_item(item.id, quantity=3, condition="good")
    assert updated.quantity == 3
    assert updated.condition == "good"

    assert repo.delete_item(item.id) is True
    assert repo.get_item_by_id(item.id) is None


def test_repository_handles_missing_and_empty_state(tmp_path) -> None:
    repo = InventoryRepository(tmp_path / "empty.db")

    assert repo.get_item_by_id(123) is None
    assert repo.list_items() == []
    assert repo.search_items_by_name("missing") == []
    assert repo.delete_item(123) is False

    item = repo.create_item(name="Chair", quantity=0)
    assert item.quantity == 0
    assert repo.update_item(item.id, quantity=2).quantity == 2
