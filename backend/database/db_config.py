"""
database/db_config.py
─────────────────────
Handles SQLite connection management and schema initialisation.

Design decisions:
- Uses thread-local connections (g) so Flask's dev-server threads stay safe.
- WAL mode enables concurrent reads while a write is in progress.
- PRAGMA foreign_keys = ON enforced on every new connection.
"""

import os
import sqlite3
from flask import g

# Resolve the path to the DB file relative to this file's location
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DB_PATH   = os.path.join(BASE_DIR, "student_manager.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")


def get_db() -> sqlite3.Connection:
    """Return the per-request SQLite connection, creating it if necessary."""
    if "db" not in g:
        conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row          # dict-like access
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.commit()
        g.db = conn
    return g.db


def close_db(e=None):
    """Close the connection at the end of each request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def _migrate(db: sqlite3.Connection) -> None:
    """
    Add any new columns to existing databases (non-destructive migration).
    SQLite doesn't support ADD COLUMN IF NOT EXISTS, so we check existing cols first.
    """
    # Get current student columns
    existing = {row[1] for row in db.execute("PRAGMA table_info(students)")}

    new_columns = [
        ("roll_no",          "TEXT"),
        ("department",       "TEXT"),
        ("marks",            "REAL"),
        ("grade",            "TEXT"),
        ("blood_group",      "TEXT"),
        ("guardian_name",    "TEXT"),
        ("guardian_contact", "TEXT"),
        ("join_date",        "DATE"),
        ("created_at",       "TIMESTAMP"),  # DEFAULT not allowed in ALTER TABLE
        ("updated_at",       "TIMESTAMP"),
    ]
    for col_name, col_def in new_columns:
        if col_name not in existing:
            db.execute(f"ALTER TABLE students ADD COLUMN {col_name} {col_def}")

    db.commit()


def init_db(app):
    """
    Register teardown and create/migrate all tables from schema.sql.
    Safe to call on every restart — CREATE TABLE IF NOT EXISTS is idempotent.
    """
    app.teardown_appcontext(close_db)

    with app.app_context():
        db = get_db()
        with open(SCHEMA_PATH, "r") as f:
            db.executescript(f.read())
        db.commit()
        # Migrate any existing DB to add new columns
        _migrate(db)

