"""
utils/constants.py
Shared, non-logic configuration used across model / optimizer / database /
pages. Keep this file to plain values only — no business logic here.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "model"

SAMPLE_DATA_PATH = DATA_DIR / "sample_data.csv"
DB_PATH = DATA_DIR / "smartmess.db"
MODEL_ARTIFACT_PATH = MODEL_DIR / "demand_model.pkl"

# ---------------------------------------------------------------------------
# Domain config
# ---------------------------------------------------------------------------
DAYS_OF_WEEK = (
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
)

MENU_OPTIONS = (
    "Veg Thali",
    "Rice & Sambar",
    "Pulao",
    "Idli & Chutney",
    "Dosa",
    "Chapati & Curry",
    "Biryani",
)

RISK_LEVELS = ("LOW", "MEDIUM", "HIGH")

# ---------------------------------------------------------------------------
# Validation bounds
# ---------------------------------------------------------------------------
MIN_ATTENDANCE = 0
MAX_ATTENDANCE = 5000
MIN_QUANTITY = 0
BUFFER_PERCENT_DEFAULT = 0.10  # 10% planned buffer over predicted demand
