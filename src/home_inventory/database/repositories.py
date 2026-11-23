from __future__ import annotations

from pathlib import Path

from home_inventory.config import settings
from home_inventory.core.models import Item
from home_inventory.database.connection import connection_scope
from home_inventory.database.schema import ensure_schema
from home_inventory.database.text import escape_like, fold_text


class InventoryRepository:
    """Persistence layer for inventory items using SQLite."""

    def __init__(self, database_path: str | Path | None = None) -> None:
        self.database_path = Path(database_path) if database_path is not None else settings.database_path
        ensure_schema(self.database_path)

    def _row_to_item(self, row) -> Item:
        return Item(
            id=row["id"],
            name=row["name"],
            category=row["category"],
            location=row["location"],
            quantity=row["quantity"],
            condition=row["condition"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def create_item(
        self,
        name: str | Item | None = None,
        category: str | None = None,
        location: str | None = None,
        quantity: int = 1,
        condition: str = "new",
    ) -> Item:
        if isinstance(name, Item):
            item = name
        else:
            item = Item(
                name=name or "",
                category=category,
                location=location,
                quantity=quantity,
                condition=condition,
            )

        with connection_scope(self.database_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO items (name, category, location, quantity, condition, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """,
                (item.name, item.category, item.location, item.quantity, item.condition),
            )
            item.id = cursor.lastrowid
            row = connection.execute(
                "SELECT * FROM items WHERE id = ?",
                (item.id,),
            ).fetchone()
            if row is None:
                raise RuntimeError("Failed to fetch created item.")
            return self._row_to_item(row)

    def get_item_by_id(self, item_id: int) -> Item | None:
        with connection_scope(self.database_path) as connection:
            row = connection.execute(
                "SELECT * FROM items WHERE id = ?",
                (item_id,),
            ).fetchone()
            if row is None:
                return None
            return self._row_to_item(row)

    def list_items(self) -> list[Item]:
        with connection_scope(self.database_path) as connection:
            rows = connection.execute(
                "SELECT * FROM items ORDER BY id ASC"
            ).fetchall()
            return [self._row_to_item(row) for row in rows]

    def update_item(self, item_id: int, **fields: object) -> Item:
        existing = self.get_item_by_id(item_id)
        if existing is None:
            raise KeyError(f"Item with id {item_id} not found.")

        update_fields: dict[str, object] = dict(fields)
        if not update_fields:
            return existing

        assignments = []
        values: list[object] = []
        for key, value in update_fields.items():
            assignments.append(f"{key} = ?")
            values.append(value)

        values.append(item_id)

        with connection_scope(self.database_path) as connection:
            connection.execute(
                f"UPDATE items SET {', '.join(assignments)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                values,
            )
            connection.commit()

        updated = self.get_item_by_id(item_id)
        if updated is None:
            raise RuntimeError("Failed to fetch updated item.")
        return updated

    def delete_item(self, item_id: int) -> bool:
        with connection_scope(self.database_path) as connection:
            cursor = connection.execute("DELETE FROM items WHERE id = ?", (item_id,))
            connection.commit()
            return cursor.rowcount > 0

    def search_items_by_name(self, query: str) -> list[Item]:
        term = (query or "").strip()
        if not term:
            return self.list_items()

        with connection_scope(self.database_path) as connection:
            pattern = f"%{escape_like(fold_text(term))}%"
            rows = connection.execute(
                "SELECT * FROM items WHERE fold_text(name) LIKE ? ESCAPE '\\' ORDER BY id ASC",
                (pattern,),
            ).fetchall()
            return [self._row_to_item(row) for row in rows]
