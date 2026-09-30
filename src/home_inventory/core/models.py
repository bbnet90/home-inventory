from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass(slots=True)
class Item:
    """Minimal domain model for an inventory item."""

    name: str
    category: str | None = None
    location: str | None = None
    quantity: int = 1
    condition: str = "new"
    id: int | None = None
    created_at: str | None = None
    updated_at: str | None = None

    def __post_init__(self) -> None:
        cleaned_name = (self.name or "").strip()
        if not cleaned_name:
            raise ValueError("Item name is required.")
        self.name = cleaned_name

        if self.category is not None:
            cleaned_category = (self.category or "").strip()
            self.category = cleaned_category or None

        if self.location is not None:
            cleaned_location = (self.location or "").strip()
            self.location = cleaned_location or None

        if self.quantity < 0:
            raise ValueError("Item quantity cannot be negative.")

        cleaned_condition = (self.condition or "").strip() or "new"
        self.condition = cleaned_condition

        if self.created_at is None:
            self.created_at = _utc_timestamp()
        if self.updated_at is None:
            self.updated_at = self.created_at
