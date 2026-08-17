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


def test_calculate_roi_pct_handles_zero_or_invalid_investment():
    assert calculate_roi_pct(100000, 0) == 0.0
    assert calculate_roi_pct("N/A", "bad") == 0.0
    assert calculate_roi_pct(-5000, 10000) == -150.0


def test_calculate_goal_progress_for_target_gap():
    value = calculate_goal_progress(40000, 100000)
    assert value == 40.0


def test_calculate_goal_progress_handles_invalid_or_zero_targets():
    assert calculate_goal_progress(25000, 0) == 0.0
    assert calculate_goal_progress("invalid", "bad") == 0.0
    assert calculate_goal_progress(120000, 100000) == 120.0


def test_validate_required_columns_detects_missing_fields():
    missing = validate_required_columns(["date", "asset_class"], ["date", "asset_class", "instrument_name"])
    assert missing == ["instrument_name"]


def test_validate_required_columns_handles_case_and_spacing_variants():
    missing = validate_required_columns(["Date", "Asset Class"], ["date", "asset class", "instrument_name"])
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


def test_portfolio_health_handles_empty_and_zero_value_data():
    assert calculate_portfolio_health(pd.DataFrame()) == {"score": 0.0, "risk": "N/A", "top_class": "N/A", "top_share": 0.0}
    assert calculate_portfolio_health(pd.DataFrame([{"asset_class": "Stocks", "current_value": 0, "returns_pct": 0, "risk_level": "Low"}]))["risk"] == "Very weak"


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


def test_quality_score_fills_missing_values_safely():
    df = pd.DataFrame(
        [{"instrument_name": "Fallback FT", "current_value": 1200, "amount_invested": 1000, "risk_level": "very high"}]
    )
    scored = calculate_quality_score(df)
    assert scored.iloc[0]["roi_pct"] == 20.0
    assert scored.iloc[0]["risk_numeric"] == 4
    assert scored.iloc[0]["recommendation"] in {"Strong Buy", "Buy", "Hold", "Consider Sell"}


def test_calculate_quality_score_handles_missing_columns_and_empty_frame():
    empty = calculate_quality_score(pd.DataFrame())
    assert empty.empty

    partial = pd.DataFrame([{"current_value": 5000, "amount_invested": 4000}])
    scored = calculate_quality_score(partial)
    assert list(scored.columns) == ["instrument_name", "asset_class", "roi_pct", "risk_numeric", "quality_score", "recommendation"]
    assert scored.iloc[0]["roi_pct"] == 25.0
