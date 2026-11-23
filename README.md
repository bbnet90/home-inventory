# Home Inventory

Home Inventory is a local-first Python CLI for tracking household items and inventory data without any cloud or remote service dependency.

## Current repository state

This repository was still effectively empty at the start of the project. The skeleton below establishes the initial structure needed for a clean, layered Python application that can evolve into a larger personal management system later.

## Target architecture

- Python CLI application
- Local-first storage
- SQLite database only
- No internet, cloud, Firebase, auth, or remote server
- Layered design: CLI -> Core/Service -> SQLite
- User data kept outside source control under the local project `data/` directory
- Future-friendly boundaries that can be reused in a broader personal management system

## Recommended project structure

```text
home-inventory/
├── src/
│   └── home_inventory/
│       ├── __init__.py
│       ├── config.py
│       ├── cli/
│       │   ├── __init__.py
│       │   └── main.py
│       ├── core/
│       │   ├── __init__.py
│       │   └── services.py
│       └── database/
│           ├── __init__.py
│           ├── connection.py
│           └── schema.py
├── tests/
│   └── test_config.py
├── data/
│   └── .gitkeep
├── .github/
│   └── workflows/
│       └── tests.yml
├── .gitignore
├── pyproject.toml
└── README.md
```

## Local database location

The SQLite file is always local and is ignored by Git. The location is chosen in this order:

1. `$HOME_INVENTORY_DB`, if set (full path to the `.db` file).
2. `<repo>/data/home_inventory.db` when running from a source checkout (for example `pip install -e .`).
3. `~/.local/share/home-inventory/home_inventory.db` (or `$XDG_DATA_HOME/home-inventory/`) for a regular `pip install .`, so data is never written next to `site-packages`.

Run `home-inventory status` to see which path is in use.

## Planned scope for v0.1

The project now includes a minimal but working local-first CLI for setup and CRUD operations around an `Item` model.

## CLI usage

```bash
home-inventory status
home-inventory init-db
home-inventory add "USB-C Cable" --category electronics --location "desk/drawer-1" --quantity 3 --condition new
home-inventory find "USB-C"
home-inventory list
home-inventory show 1
home-inventory update 1 --quantity 5 --location "desk/drawer-2"
home-inventory remove 1
```

Notes on behaviour:

- `find` matches names case-insensitively and is Turkish-aware: `istanbul`, `ISTANBUL` and `İstanbul` all match each other (the dotted/dotless i family is treated as `i`). Diacritics are kept, so `sem` does not match `Şemsiye`.
- `%` and `_` in a search term are matched literally, not as wildcards.
- `update` cleans values like `add` does: text is trimmed, a blank `--condition` becomes `new`, and a blank `--category ""` or `--location ""` clears that field.
- Give the item name either positionally or with `--name`, not both (unless they are identical).

## Architecture

The project remains intentionally small and layered:

```text
CLI
 ↓
Service
 ↓
Repository
 ↓
SQLite
```

The CLI only parses arguments and prints output. The service layer validates core rules and coordinates repository actions. The repository is the only layer that executes SQLite queries.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .[dev]
python -m home_inventory.cli.main status
```

## Notes

- This project is intentionally small and explicit.
- Business logic stays out of CLI code.
- SQLite access stays behind a database boundary.
- Users and real data are not committed to source control.
