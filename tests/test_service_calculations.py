import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from wealth_app.services.calculations import (
    calculate_goal_progress,
    calculate_portfolio_health,
    calculate_quality_score,
    calculate_roi_pct,
)
from wealth_app.services.validators import validate_required_columns


def test_calculate_roi_pct_for_positive_return():
    value = calculate_roi_pct(120000, 100000)
    assert value == 20.0


def test_calculate_goal_progress_for_target_gap():
    value = calculate_goal_progress(40000, 100000)
    assert value == 40.0


def test_validate_required_columns_detects_missing_fields():
    missing = validate_required_columns(["date", "asset_class"], ["date", "asset_class", "instrument_name"])
    assert missing == ["instrument_name"]


def test_portfolio_health_returns_expected_shape():
    df = pd.DataFrame(
        [
            {"asset_class": "Stocks", "current_value": 120000, "returns_pct": 15, "risk_level": "Medium"},
            {"asset_class": "Crypto", "current_value": 80000, "returns_pct": -10, "risk_level": "High"},
        ]
    )
    result = calculate_portfolio_health(df)
    assert result["score"] >= 0
    assert result["risk"] in {"Healthy", "Watchlist", "At risk", "Critical"}


def test_quality_score_marks_strong_sell_for_negative_roi_high_risk():
    df = pd.DataFrame(
        [
            {
                "instrument_name": "Speculative Fund",
                "asset_class": "Crypto",
                "roi_pct": -20,
                "risk_level": "High",
            }
        ]
    )
    scored = calculate_quality_score(df)
    assert scored.iloc[0]["recommendation"] == "Consider Sell"
