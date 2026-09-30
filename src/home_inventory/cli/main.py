from __future__ import annotations

import argparse
import sys
from collections.abc import Callable

from home_inventory import __version__
from home_inventory.config import settings
from home_inventory.core.services import InventoryService


def _error(message: str) -> int:
    print(message, file=sys.stderr)
    return 1


def handle_status(_args: argparse.Namespace, _service: InventoryService | None = None) -> int:
    print(f"home-inventory {__version__}")
    print(f"database_path={settings.database_path}")
    print("mode=local-first sqlite")
    return 0


def handle_init_db(_args: argparse.Namespace, service: InventoryService | None = None) -> int:
    active_service = service or InventoryService(settings.database_path)
    created_path = active_service.initialize_storage()
    print(f"database initialized at {created_path}")
    return 0


def handle_add(args: argparse.Namespace, service: InventoryService | None = None) -> int:
    active_service = service or InventoryService(settings.database_path)
    name = args.name_option or args.name
    if not name:
        return _error("Item name is required.")

    try:
        item = active_service.create_item(
            name=name,
            category=args.category,
            location=args.location,
            quantity=args.quantity,
            condition=args.condition,
        )
    except ValueError as exc:
        return _error(str(exc))
    except Exception as exc:  # pragma: no cover - safety net for unexpected DB issues
        return _error(f"Unable to create item: {exc}")

    print(f"Created item #{item.id}: {item.name}")
    return 0


def handle_find(args: argparse.Namespace, service: InventoryService | None = None) -> int:
    active_service = service or InventoryService(settings.database_path)
    query = (args.query or "").strip()
    if not query:
        return _error("Search query is required.")

    items = active_service.search_items(query)
    if not items:
        print("No items found.")
        return 0

    print("ID | NAME | CATEGORY | LOCATION | QUANTITY | CONDITION")
    for item in items:
        print(f"{item.id} | {item.name} | {item.category or '-'} | {item.location or '-'} | {item.quantity} | {item.condition}")
    return 0


def handle_list(args: argparse.Namespace, service: InventoryService | None = None) -> int:
    active_service = service or InventoryService(settings.database_path)
    items = active_service.list_items()
    if not items:
        print("No items found.")
        return 0

    print("ID | NAME | CATEGORY | LOCATION | QUANTITY | CONDITION")
    for item in items:
        print(f"{item.id} | {item.name} | {item.category or '-'} | {item.location or '-'} | {item.quantity} | {item.condition}")
    return 0


def handle_show(args: argparse.Namespace, service: InventoryService | None = None) -> int:
    active_service = service or InventoryService(settings.database_path)
    try:
        item_id = int(args.item_id)
    except ValueError:
        return _error("Item ID must be an integer.")

    item = active_service.get_item(item_id)
    if item is None:
        print(f"Item #{item_id} not found.")
        return 1

    print(f"ID: {item.id}")
    print(f"Name: {item.name}")
    print(f"Category: {item.category or '-'}")
    print(f"Location: {item.location or '-'}")
    print(f"Quantity: {item.quantity}")
    print(f"Condition: {item.condition}")
    print(f"Created: {item.created_at}")
    print(f"Updated: {item.updated_at}")
    return 0


def handle_update(args: argparse.Namespace, service: InventoryService | None = None) -> int:
    active_service = service or InventoryService(settings.database_path)
    try:
        item_id = int(args.item_id)
    except ValueError:
        return _error("Item ID must be an integer.")

    update_fields: dict[str, object] = {}
    if args.name is not None:
        update_fields["name"] = args.name
    if args.category is not None:
        update_fields["category"] = args.category
    if args.location is not None:
        update_fields["location"] = args.location
    if args.quantity is not None:
        update_fields["quantity"] = args.quantity
    if args.condition is not None:
        update_fields["condition"] = args.condition

    if not update_fields:
        return _error("At least one field must be provided to update.")

    try:
        item = active_service.update_item(item_id, **update_fields)
    except KeyError:
        print(f"Item #{item_id} not found.")
        return 1
    except ValueError as exc:
        return _error(str(exc))
    except Exception as exc:  # pragma: no cover - safety net for unexpected DB issues
        return _error(f"Unable to update item: {exc}")

    print(f"Updated item #{item.id}: {item.name}")
    return 0


def handle_remove(args: argparse.Namespace, service: InventoryService | None = None) -> int:
    active_service = service or InventoryService(settings.database_path)
    try:
        item_id = int(args.item_id)
    except ValueError:
        return _error("Item ID must be an integer.")

    item = active_service.get_item(item_id)
    if item is None:
        print(f"Item #{item_id} not found.")
        return 1

    try:
        deleted = active_service.delete_item(item_id)
    except Exception as exc:  # pragma: no cover - safety net for unexpected DB issues
        return _error(f"Unable to remove item: {exc}")

    if not deleted:
        print(f"Item #{item_id} not found.")
        return 1

    print(f"Removed item #{item.id}: {item.name}")
    return 0


def build_parser(service_factory: Callable[[], InventoryService] | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="home-inventory",
        description="Local-first home inventory CLI.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command")

    status_parser = subparsers.add_parser("status", help="Show the current local configuration.")
    status_parser.set_defaults(handler=lambda args: handle_status(args, service_factory())) if service_factory is not None else status_parser.set_defaults(handler=lambda args: handle_status(args))

    init_db_parser = subparsers.add_parser("init-db", help="Create the local SQLite database and base schema.")
    init_db_parser.set_defaults(handler=lambda args: handle_init_db(args, service_factory())) if service_factory is not None else init_db_parser.set_defaults(handler=lambda args: handle_init_db(args))

    add_parser = subparsers.add_parser("add", help="Add a new item.")
    add_parser.add_argument("name", nargs="?", help="Item name")
    add_parser.add_argument("--name", dest="name_option", help="Item name")
    add_parser.add_argument("--category")
    add_parser.add_argument("--location")
    add_parser.add_argument("--quantity", type=int, default=1)
    add_parser.add_argument("--condition", default="new")
    add_parser.set_defaults(handler=lambda args: handle_add(args, service_factory())) if service_factory is not None else add_parser.set_defaults(handler=lambda args: handle_add(args))

    find_parser = subparsers.add_parser("find", help="Search items by name.")
    find_parser.add_argument("query", help="Search term")
    find_parser.set_defaults(handler=lambda args: handle_find(args, service_factory())) if service_factory is not None else find_parser.set_defaults(handler=lambda args: handle_find(args))

    list_parser = subparsers.add_parser("list", help="List all items.")
    list_parser.set_defaults(handler=lambda args: handle_list(args, service_factory())) if service_factory is not None else list_parser.set_defaults(handler=lambda args: handle_list(args))

    show_parser = subparsers.add_parser("show", help="Show a single item.")
    show_parser.add_argument("item_id", help="Item ID")
    show_parser.set_defaults(handler=lambda args: handle_show(args, service_factory())) if service_factory is not None else show_parser.set_defaults(handler=lambda args: handle_show(args))

    update_parser = subparsers.add_parser("update", help="Update an item.")
    update_parser.add_argument("item_id", help="Item ID")
    update_parser.add_argument("--name")
    update_parser.add_argument("--category")
    update_parser.add_argument("--location")
    update_parser.add_argument("--quantity", type=int)
    update_parser.add_argument("--condition")
    update_parser.set_defaults(handler=lambda args: handle_update(args, service_factory())) if service_factory is not None else update_parser.set_defaults(handler=lambda args: handle_update(args))

    remove_parser = subparsers.add_parser("remove", help="Remove an item.")
    remove_parser.add_argument("item_id", help="Item ID")
    remove_parser.set_defaults(handler=lambda args: handle_remove(args, service_factory())) if service_factory is not None else remove_parser.set_defaults(handler=lambda args: handle_remove(args))

    return parser


def main(argv: list[str] | None = None, service_factory: Callable[[], InventoryService] | None = None) -> int:
    parser = build_parser(service_factory=service_factory)
    args = parser.parse_args(argv)

    if not hasattr(args, "handler"):
        parser.print_help()
        return 0

    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
