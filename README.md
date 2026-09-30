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

The default SQLite file is intentionally kept local to the project data directory and is ignored by Git:

```text
~/projects/home-inventory/data/home_inventory.db
```

This keeps the database out of version control while preserving a simple, reproducible developer workflow.

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
