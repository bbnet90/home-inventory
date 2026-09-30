import pytest

from home_inventory.core.models import Item


def test_item_accepts_valid_values() -> None:
    item = Item(
        name="Lamp",
        category="Bedroom",
        location="Shelf A",
        quantity=2,
        condition="good",
    )

    assert item.name == "Lamp"
    assert item.quantity == 2
    assert item.condition == "good"


def test_item_rejects_empty_name() -> None:
    with pytest.raises(ValueError, match="name"):
        Item(name="   ", quantity=1)


def test_item_rejects_negative_quantity() -> None:
    with pytest.raises(ValueError, match="quantity"):
        Item(name="Chair", quantity=-1)
