from home_inventory.core.services import InventoryService


def test_service_create_and_get_item(tmp_path) -> None:
    service = InventoryService(tmp_path / "service.db")

    created = service.create_item("USB-C Cable", category="electronics", quantity=3)
    found = service.get_item(created.id)

    assert found is not None
    assert found.name == "USB-C Cable"
    assert found.quantity == 3


def test_service_update_and_delete_item(tmp_path) -> None:
    service = InventoryService(tmp_path / "service.db")
    created = service.create_item("Laptop Stand")

    updated = service.update_item(created.id, quantity=2, location="desk")
    assert updated.quantity == 2
    assert updated.location == "desk"

    assert service.delete_item(created.id) is True
    assert service.get_item(created.id) is None


def test_service_validates_invalid_values(tmp_path) -> None:
    service = InventoryService(tmp_path / "service.db")

    try:
        service.create_item("   ")
        assert False, "Expected ValueError for empty name"
    except ValueError:
        pass

    try:
        service.create_item("Chair", quantity=-1)
        assert False, "Expected ValueError for negative quantity"
    except ValueError:
        pass
