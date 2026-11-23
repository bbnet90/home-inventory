from __future__ import annotations

from pathlib import Path

from home_inventory.config import settings
from home_inventory.core.models import Item
from home_inventory.database.repositories import InventoryRepository
from home_inventory.database.schema import ensure_schema


DEFAULT_CONDITION = "new"
# Largest value the SQLite INTEGER column can hold.
MAX_QUANTITY = 2**63 - 1


class InventoryService:
    """Business logic boundary for inventory operations."""

    def __init__(self, database_path: str | Path | None = None, repository: InventoryRepository | None = None) -> None:
        self.database_path = Path(database_path) if database_path is not None else settings.database_path
        self.repository = repository or InventoryRepository(self.database_path)

    def initialize_storage(self) -> Path:
        """Create the local SQLite database and the base schema."""
        return ensure_schema(self.database_path)

    @staticmethod
    def _validate_name(name: str) -> str:
        cleaned = (name or "").strip()
        if not cleaned:
            raise ValueError("Item name is required.")
        return cleaned

    @staticmethod
    def _validate_quantity(quantity: int) -> int:
        numeric_quantity = int(quantity)
        if numeric_quantity < 0:
            raise ValueError("Item quantity cannot be negative.")
        if numeric_quantity > MAX_QUANTITY:
            raise ValueError(f"Item quantity is too large (maximum is {MAX_QUANTITY}).")
        return numeric_quantity

    @staticmethod
    def _clean_optional(value: object) -> str | None:
        """Strip text; blank becomes None (used for category and location)."""
        if value is None:
            return None
        return str(value).strip() or None

    @staticmethod
    def _clean_condition(value: object) -> str:
        """Strip text; blank falls back to the default condition."""
        if value is None:
            return DEFAULT_CONDITION
        return str(value).strip() or DEFAULT_CONDITION

    def create_item(
        self,
        name: str,
        category: str | None = None,
        location: str | None = None,
        quantity: int = 1,
        condition: str = "new",
    ) -> Item:
        cleaned_name = self._validate_name(name)
        cleaned_quantity = self._validate_quantity(quantity)
        return self.repository.create_item(
            name=cleaned_name,
            category=self._clean_optional(category),
            location=self._clean_optional(location),
            quantity=cleaned_quantity,
            condition=self._clean_condition(condition),
        )

    def get_item(self, item_id: int) -> Item | None:
        return self.repository.get_item_by_id(item_id)

    def list_items(self) -> list[Item]:
        return self.repository.list_items()

    def search_items(self, query: str) -> list[Item]:
        return self.repository.search_items_by_name(query)

    def update_item(self, item_id: int, **fields: object) -> Item:
        if "name" in fields:
            fields["name"] = self._validate_name(str(fields["name"]))
        if "quantity" in fields:
            fields["quantity"] = self._validate_quantity(int(fields["quantity"]))
        # Same cleaning as create_item, so update cannot store blank strings.
        # A blank category/location clears the value (stored as NULL).
        for key in ("category", "location"):
            if key in fields:
                fields[key] = self._clean_optional(fields[key])
        if "condition" in fields:
            fields["condition"] = self._clean_condition(fields["condition"])
        return self.repository.update_item(item_id, **fields)

    def delete_item(self, item_id: int) -> bool:
        return self.repository.delete_item(item_id)
