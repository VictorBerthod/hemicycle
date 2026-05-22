"""Idempotent migration to add the new profile columns on `deputes`.

SQLAlchemy's create_all() does not ALTER existing tables. We add the columns
manually with SQLite's ALTER TABLE ADD COLUMN, skipping any that already exist.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect, text

from app.database import engine, init_db


COLUMNS_TO_ADD = [
    ("profession",          "VARCHAR"),
    ("mandats_anterieurs",  "TEXT"),
    ("bio_short",           "TEXT"),
]


def main() -> None:
    init_db()  # ensure tags + depute_tags exist
    insp = inspect(engine)
    existing = {c["name"] for c in insp.get_columns("deputes")}

    added = []
    with engine.begin() as conn:
        for name, sql_type in COLUMNS_TO_ADD:
            if name in existing:
                continue
            conn.execute(text(f"ALTER TABLE deputes ADD COLUMN {name} {sql_type}"))
            added.append(name)

    if added:
        print(f"Added columns: {', '.join(added)}")
    else:
        print("All profile columns already present — no migration needed.")


if __name__ == "__main__":
    main()
