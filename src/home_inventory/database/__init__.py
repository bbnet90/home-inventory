"""Database layer for the local inventory application."""

from .connection import get_connection
from .schema import ensure_schema

__all__ = ["get_connection", "ensure_schema", "InventoryRepository"]


def __getattr__(name: str):
    if name == "InventoryRepository":
        from .repositories import InventoryRepository

        return InventoryRepository
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
