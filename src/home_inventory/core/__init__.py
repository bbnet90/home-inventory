"""Core business logic layer."""

from .models import Item

__all__ = ["Item", "InventoryService"]


def __getattr__(name: str):
    if name == "InventoryService":
        from .services import InventoryService

        return InventoryService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
