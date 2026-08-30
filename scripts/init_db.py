#!/usr/bin/env python3

import argparse
import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATABASE = PROJECT_ROOT / "data" / "ll.db"
SCHEMA_FILE = PROJECT_ROOT / "db" / "schema.sql"

EXPECTED_TABLES = {
    "c_dict",
    "c_dict_pron",
    "dictionary_links",
    "maintenance_data",
    "training_cards",
    "user_notifications",
    "users",
    "word_set",
    "words",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create an empty LLBot SQLite database."
    )
    parser.add_argument(
        "database",
        nargs="?",
        type=Path,
        default=DEFAULT_DATABASE,
        help=f"database path (default: {DEFAULT_DATABASE})",
    )
    return parser.parse_args()


def initialize_database(database: Path) -> None:
    database = database.expanduser().resolve()
    if database.exists():
        raise FileExistsError(
            f"Refusing to overwrite existing database: {database}"
        )

    database.parent.mkdir(parents=True, exist_ok=True)
    schema = SCHEMA_FILE.read_text(encoding="utf-8")

    try:
        with sqlite3.connect(database) as connection:
            connection.executescript(schema)
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
            missing_tables = EXPECTED_TABLES - tables
            if missing_tables:
                missing = ", ".join(sorted(missing_tables))
                raise RuntimeError(f"Schema is missing tables: {missing}")
    except Exception:
        database.unlink(missing_ok=True)
        raise

    print(f"Created empty LLBot database: {database}")


if __name__ == "__main__":
    try:
        initialize_database(parse_args().database)
    except FileExistsError as exc:
        raise SystemExit(str(exc)) from None
