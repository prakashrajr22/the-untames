"""
tests/test_database.py
Covers: init, idempotent seeding, validation rejections, actuals/waste math,
history filtering. Uses a temp DB file per test — never touches the real
data/smartmess.db.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database import db as dbmod  # noqa: E402


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    """Point the module at a throwaway sqlite file for every test."""
    monkeypatch.setattr(dbmod, "DB_PATH", tmp_path / "test.db")
    dbmod.init_db()
    yield
    # tmp_path is auto-cleaned by pytest


def sample_df(n=5):
    rows = []
    for i in range(n):
        rows.append({
            "date": f"2026-01-{i+1:02d}",
            "day": "Monday",
            "menu": "Veg Thali",
            "attendance": 100 + i,
            "predicted_demand": 90 + i,
            "recommended_quantity": 95 + i,
            "prepared_quantity": 95 + i,
            "consumed_quantity": 88 + i,
            "waste_quantity": 7,
            "prediction_error": -2 + i,
            "risk_level": "LOW",
        })
    return pd.DataFrame(rows)


# --------------------------- init ---------------------------

def test_init_creates_table():
    assert dbmod.record_count() == 0


def test_init_is_safe_to_call_repeatedly():
    dbmod.init_db()
    dbmod.init_db()
    assert dbmod.record_count() == 0


# --------------------------- seeding ---------------------------

def test_seed_from_dataframe_inserts_rows():
    inserted = dbmod.seed_from_dataframe(sample_df(5))
    assert inserted == 5
    assert dbmod.record_count() == 5


def test_seed_is_idempotent():
    dbmod.seed_from_dataframe(sample_df(5))
    second = dbmod.seed_from_dataframe(sample_df(5))
    assert second == 0
    assert dbmod.record_count() == 5


def test_seed_different_key_allows_second_batch():
    dbmod.seed_from_dataframe(sample_df(3), seed_key="batch_a")
    dbmod.seed_from_dataframe(sample_df(3), seed_key="batch_b")
    assert dbmod.record_count() == 6


def test_seed_rejects_missing_required_columns():
    bad = sample_df(1).drop(columns=["predicted_demand"])
    with pytest.raises(dbmod.ValidationError):
        dbmod.seed_from_dataframe(bad, seed_key="bad_cols")


def test_seed_rejects_consumed_exceeds_prepared():
    bad = sample_df(1)
    bad.loc[0, "consumed_quantity"] = bad.loc[0, "prepared_quantity"] + 10
    with pytest.raises(dbmod.ValidationError):
        dbmod.seed_from_dataframe(bad, seed_key="bad_math")


# --------------------------- prediction inserts ---------------------------

def test_insert_prediction_record():
    rid = dbmod.insert_prediction_record(
        date="2026-02-01", day="Sunday", menu="Rice & Sambar",
        attendance=150, predicted_demand=140, recommended_quantity=145,
        risk_level="MEDIUM",
    )
    rec = dbmod.get_record(rid)
    assert rec.attendance == 150
    assert rec.consumed_quantity is None
    assert rec.risk_level == "MEDIUM"


def test_insert_prediction_rejects_negative_attendance():
    with pytest.raises(dbmod.ValidationError):
        dbmod.insert_prediction_record(
            date="2026-02-01", day="Sunday", menu="X",
            attendance=-1, predicted_demand=10, recommended_quantity=10,
            risk_level="LOW",
        )


def test_insert_prediction_rejects_invalid_risk_level():
    with pytest.raises(dbmod.ValidationError):
        dbmod.insert_prediction_record(
            date="2026-02-01", day="Sunday", menu="X",
            attendance=10, predicted_demand=10, recommended_quantity=10,
            risk_level="EXTREME",
        )


# --------------------------- actuals / waste math ---------------------------

def test_record_actuals_computes_waste_and_error():
    rid = dbmod.insert_prediction_record(
        date="2026-02-02", day="Monday", menu="Pulao",
        attendance=100, predicted_demand=90, recommended_quantity=95,
        risk_level="LOW",
    )
    dbmod.record_actuals(rid, prepared_quantity=95, consumed_quantity=80)
    rec = dbmod.get_record(rid)
    assert rec.waste_quantity == 15
    assert rec.prediction_error == pytest.approx(-10)  # 80 consumed - 90 predicted


def test_record_actuals_rejects_consumed_over_prepared():
    rid = dbmod.insert_prediction_record(
        date="2026-02-03", day="Tuesday", menu="Idli",
        attendance=50, predicted_demand=45, recommended_quantity=48,
        risk_level="LOW",
    )
    with pytest.raises(dbmod.ValidationError):
        dbmod.record_actuals(rid, prepared_quantity=40, consumed_quantity=50)


def test_record_actuals_rejects_negative_quantities():
    rid = dbmod.insert_prediction_record(
        date="2026-02-04", day="Wednesday", menu="Dosa",
        attendance=50, predicted_demand=45, recommended_quantity=48,
        risk_level="LOW",
    )
    with pytest.raises(dbmod.ValidationError):
        dbmod.record_actuals(rid, prepared_quantity=-1, consumed_quantity=0)


def test_record_actuals_unknown_id_raises():
    with pytest.raises(dbmod.ValidationError):
        dbmod.record_actuals(9999, prepared_quantity=10, consumed_quantity=5)


# --------------------------- reads ---------------------------

def test_get_history_df_only_returns_completed_records():
    seeded = dbmod.seed_from_dataframe(sample_df(3))
    rid = dbmod.insert_prediction_record(
        date="2026-03-01", day="Sunday", menu="X",
        attendance=10, predicted_demand=10, recommended_quantity=10,
        risk_level="LOW",
    )
    assert seeded == 3
    history = dbmod.get_history_df()
    all_records = dbmod.get_all_records_df()
    assert len(history) == 3          # the un-completed insert is excluded
    assert len(all_records) == 4      # but shows up in the full table
    assert rid not in history["id"].tolist()


def test_history_ordered_by_date_ascending():
    df = sample_df(5)
    dbmod.seed_from_dataframe(df.sample(frac=1, random_state=1))  # shuffled insert
    history = dbmod.get_history_df()
    assert list(history["date"]) == sorted(history["date"].tolist())
