"""
database/db.py
==============
SQLite persistence layer for SmartMess AI.

Responsibilities (and only these — no ML, no optimizer, no UI logic here):
  - Create/own the `meal_records` table schema.
  - Provide safe, parameterized read/write functions used by the rest
    of the app (model, optimizer, and pages all go through this module,
    never raw SQL of their own).
  - Enforce the hard data-integrity rules from the spec:
        consumed_quantity <= prepared_quantity
        all quantities >= 0
  - Idempotent init/seed so the app "just works" on a fresh machine
    and re-running setup never double-inserts data.

Schema (meal_records):
    id                  INTEGER PRIMARY KEY AUTOINCREMENT
    date                TEXT    (ISO 'YYYY-MM-DD')
    day                 TEXT    (e.g. 'Monday')
    menu                TEXT
    attendance           INTEGER
    predicted_demand     REAL
    recommended_quantity REAL
    prepared_quantity    REAL    (NULL until prep happens)
    consumed_quantity    REAL    (NULL until actuals are logged)
    waste_quantity        REAL    (NULL until actuals are logged)
    prediction_error      REAL    (NULL until actuals are logged)
    risk_level             TEXT    ('LOW' | 'MEDIUM' | 'HIGH')
    created_at             TEXT    (ISO timestamp, set by SQLite)
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional

import pandas as pd

# ---------------------------------------------------------------------------
# Config — falls back to sane local defaults if utils.constants isn't wired
# up yet, but will use the shared config the moment it exists.
# ---------------------------------------------------------------------------
try:
    from utils.constants import DB_PATH, RISK_LEVELS  # type: ignore
except ImportError:
    DB_PATH = Path(__file__).resolve().parent.parent / "data" / "smartmess.db"
    RISK_LEVELS = ("LOW", "MEDIUM", "HIGH")

DB_PATH = Path(DB_PATH)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS meal_records (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    date                  TEXT    NOT NULL,
    day                   TEXT    NOT NULL,
    menu                  TEXT    NOT NULL,
    attendance            INTEGER NOT NULL CHECK (attendance >= 0),
    predicted_demand      REAL    NOT NULL CHECK (predicted_demand >= 0),
    recommended_quantity  REAL    NOT NULL CHECK (recommended_quantity >= 0),
    prepared_quantity     REAL    CHECK (prepared_quantity IS NULL OR prepared_quantity >= 0),
    consumed_quantity     REAL    CHECK (consumed_quantity IS NULL OR consumed_quantity >= 0),
    waste_quantity        REAL    CHECK (waste_quantity IS NULL OR waste_quantity >= 0),
    prediction_error       REAL,
    risk_level             TEXT    NOT NULL,
    created_at             TEXT    NOT NULL DEFAULT (datetime('now')),
    CHECK (
        consumed_quantity IS NULL
        OR prepared_quantity IS NULL
        OR consumed_quantity <= prepared_quantity
    )
);
"""

_SEED_MARKER_TABLE = """
CREATE TABLE IF NOT EXISTS _seed_state (
    seed_key TEXT PRIMARY KEY,
    seeded_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


class ValidationError(ValueError):
    """Raised when a caller tries to write data that violates the
    hard integrity rules (negative quantities, consumed > prepared)."""


@dataclass
class MealRecord:
    id: int
    date: str
    day: str
    menu: str
    attendance: int
    predicted_demand: float
    recommended_quantity: float
    prepared_quantity: Optional[float]
    consumed_quantity: Optional[float]
    waste_quantity: Optional[float]
    prediction_error: Optional[float]
    risk_level: str
    created_at: str


# ---------------------------------------------------------------------------
# Connection handling
# ---------------------------------------------------------------------------
@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Context-managed connection with FK/consistency pragmas on."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Create the schema if it doesn't exist yet. Safe to call every boot."""
    with get_connection() as conn:
        conn.execute(_SCHEMA)
        conn.execute(_SEED_MARKER_TABLE)


# ---------------------------------------------------------------------------
# Seeding (idempotent)
# ---------------------------------------------------------------------------
def is_seeded(seed_key: str = "synthetic_v1") -> bool:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM _seed_state WHERE seed_key = ?", (seed_key,)
        ).fetchone()
        return row is not None


def seed_from_dataframe(df: pd.DataFrame, seed_key: str = "synthetic_v1") -> int:
    """
    Bulk-load a synthetic/historical dataset into meal_records.
    Idempotent: if this seed_key has already been applied, this is a no-op
    and returns 0 (won't double-insert on repeated app boots).

    Expected columns (extra columns are ignored, missing optional ones
    default to NULL):
        date, day, menu, attendance, predicted_demand, recommended_quantity,
        prepared_quantity, consumed_quantity, waste_quantity,
        prediction_error, risk_level
    """
    init_db()
    if is_seeded(seed_key):
        return 0

    required = {"date", "day", "menu", "attendance",
                "predicted_demand", "recommended_quantity", "risk_level"}
    missing = required - set(df.columns)
    if missing:
        raise ValidationError(f"seed dataframe missing required columns: {missing}")

    optional_cols = ["prepared_quantity", "consumed_quantity",
                      "waste_quantity", "prediction_error"]
    rows = []
    for _, r in df.iterrows():
        prepared = r.get("prepared_quantity")
        consumed = r.get("consumed_quantity")
        if pd.notna(prepared) and pd.notna(consumed) and consumed > prepared:
            raise ValidationError(
                f"seed row violates consumed<=prepared: "
                f"consumed={consumed}, prepared={prepared}"
            )
        rows.append((
            str(r["date"]), str(r["day"]), str(r["menu"]), int(r["attendance"]),
            float(r["predicted_demand"]), float(r["recommended_quantity"]),
            _none_if_nan(prepared), _none_if_nan(consumed),
            _none_if_nan(r.get("waste_quantity")),
            _none_if_nan(r.get("prediction_error")),
            str(r["risk_level"]),
        ))

    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO meal_records
                (date, day, menu, attendance, predicted_demand, recommended_quantity,
                 prepared_quantity, consumed_quantity, waste_quantity,
                 prediction_error, risk_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.execute(
            "INSERT OR IGNORE INTO _seed_state (seed_key) VALUES (?)", (seed_key,)
        )
    return len(rows)


def seed_from_csv(csv_path: Path | str, seed_key: str = "synthetic_v1") -> int:
    df = pd.read_csv(csv_path)
    return seed_from_dataframe(df, seed_key=seed_key)


def _none_if_nan(value):
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


# ---------------------------------------------------------------------------
# Writes used by the live app (predictions + actuals)
# ---------------------------------------------------------------------------
def insert_prediction_record(
    date: str,
    day: str,
    menu: str,
    attendance: int,
    predicted_demand: float,
    recommended_quantity: float,
    risk_level: str,
) -> int:
    """Log a new preparation decision (before actuals are known)."""
    if attendance < 0:
        raise ValidationError("attendance must be >= 0")
    if predicted_demand < 0 or recommended_quantity < 0:
        raise ValidationError("predicted_demand/recommended_quantity must be >= 0")
    if risk_level not in RISK_LEVELS:
        raise ValidationError(f"risk_level must be one of {RISK_LEVELS}")

    init_db()
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO meal_records
                (date, day, menu, attendance, predicted_demand,
                 recommended_quantity, risk_level)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (date, day, menu, attendance, predicted_demand,
             recommended_quantity, risk_level),
        )
        return cur.lastrowid


def record_actuals(record_id: int, prepared_quantity: float, consumed_quantity: float) -> None:
    """
    Log what actually happened for a given record: how much was prepared
    and how much was consumed. Computes waste_quantity and prediction_error.

    Hard rules enforced here (raises ValidationError, never silently clamps):
      - prepared_quantity >= 0
      - consumed_quantity >= 0
      - consumed_quantity <= prepared_quantity
    """
    if prepared_quantity < 0 or consumed_quantity < 0:
        raise ValidationError("quantities must be >= 0")
    if consumed_quantity > prepared_quantity:
        raise ValidationError(
            f"consumed_quantity ({consumed_quantity}) cannot exceed "
            f"prepared_quantity ({prepared_quantity})"
        )

    init_db()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT predicted_demand FROM meal_records WHERE id = ?", (record_id,)
        ).fetchone()
        if row is None:
            raise ValidationError(f"no meal_record with id={record_id}")

        waste_quantity = prepared_quantity - consumed_quantity
        prediction_error = consumed_quantity - row["predicted_demand"]

        conn.execute(
            """
            UPDATE meal_records
            SET prepared_quantity = ?,
                consumed_quantity = ?,
                waste_quantity = ?,
                prediction_error = ?
            WHERE id = ?
            """,
            (prepared_quantity, consumed_quantity, waste_quantity,
             prediction_error, record_id),
        )


# ---------------------------------------------------------------------------
# Reads
# ---------------------------------------------------------------------------
def get_history_df() -> pd.DataFrame:
    """Only *completed* records (actuals logged) — ready to feed straight
    into utils/preprocessing.py for retraining or trend charts."""
    init_db()
    with get_connection() as conn:
        df = pd.read_sql_query(
            """
            SELECT * FROM meal_records
            WHERE consumed_quantity IS NOT NULL
            ORDER BY date ASC, id ASC
            """,
            conn,
        )
    return df


def get_all_records_df() -> pd.DataFrame:
    """Every record, completed or not (e.g. for the dashboard's
    'today' row before actuals exist)."""
    init_db()
    with get_connection() as conn:
        df = pd.read_sql_query(
            "SELECT * FROM meal_records ORDER BY date ASC, id ASC", conn
        )
    return df


def get_record(record_id: int) -> Optional[MealRecord]:
    init_db()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM meal_records WHERE id = ?", (record_id,)
        ).fetchone()
    return MealRecord(**dict(row)) if row else None


def record_count() -> int:
    init_db()
    with get_connection() as conn:
        return conn.execute("SELECT COUNT(*) AS c FROM meal_records").fetchone()["c"]
