from __future__ import annotations

import pandas as pd

from wealth_app.config.constants import RISK_MAP


def _coerce_float(value, default: float = 0.0) -> float:
    if value is None or (isinstance(value, str) and not value.strip()):
        return float(default)
    if isinstance(value, (int, float)) and pd.isna(value):
        return float(default)

    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return float(default)

    if pd.isna(numeric):
        return float(default)
    return float(numeric)


def _normalize_risk_level(value) -> str:
    if value is None:
        return "Medium"

    text = str(value).strip()
    if not text:
        return "Medium"

    cleaned = " ".join(text.replace("_", " ").split())
    for risk_name, numeric_value in RISK_MAP.items():
        if risk_name.lower() == cleaned.lower():
            return risk_name
        if risk_name.lower().replace(" ", "") == cleaned.lower().replace(" ", ""):
            return risk_name

    lowered = cleaned.lower()
    if lowered in {"veryhigh", "very_high", "very high"}:
        return "Very High"
    if lowered in {"low", "medium", "high"}:
        return cleaned.title()
    return "Medium"


def calculate_roi_pct(current_value: float, amount_invested: float) -> float:
    current = _coerce_float(current_value)
    invested = _coerce_float(amount_invested)
    if invested <= 0:
        return 0.0
    return round(((current / invested) - 1) * 100, 2)


def calculate_goal_progress(current_savings: float, target_amount: float) -> float:
    saved = _coerce_float(current_savings)
    target = _coerce_float(target_amount)
    if target <= 0:
        return 0.0
    return round((saved / target) * 100, 2)


def calculate_portfolio_health(investments_df: pd.DataFrame) -> dict:
    if investments_df is None or investments_df.empty:
        return {"score": 0.0, "risk": "N/A", "top_class": "N/A", "top_share": 0.0}

    required_columns = ["asset_class", "current_value", "returns_pct", "risk_level"]
    missing = [column for column in required_columns if column not in investments_df.columns]
    if missing:
        return {"score": 0.0, "risk": "N/A", "top_class": "N/A", "top_share": 0.0}

    normalized = investments_df.copy()
    normalized["asset_class"] = normalized["asset_class"].fillna("Uncategorized").astype(str).str.strip()
    normalized["current_value"] = pd.to_numeric(normalized["current_value"], errors="coerce").fillna(0.0)
    normalized["returns_pct"] = pd.to_numeric(normalized["returns_pct"], errors="coerce").fillna(0.0)
    normalized["risk_level"] = normalized["risk_level"].apply(_normalize_risk_level)

    total_value = float(normalized["current_value"].sum())
    if total_value <= 0:
        return {"score": 0.0, "risk": "Very weak", "top_class": "N/A", "top_share": 0.0}

    allocation = normalized.groupby("asset_class")["current_value"].sum().sort_values(ascending=False)
    top_class = allocation.index[0]
    top_share = float(allocation.iloc[0] / total_value * 100)

    returns = normalized["returns_pct"].fillna(0)
    avg_return = float(returns.mean())
    negative_count = float((returns < 0).sum())
    weighted_risk = normalized["risk_level"].map(RISK_MAP).fillna(2).mean()

    score = 100
    score -= max(0, top_share - 45) * 0.8
    score -= max(0, weighted_risk - 2.2) * 12
    score -= negative_count / max(len(normalized), 1) * 30
    score += min(max(avg_return, -30), 40) * 0.5
    score = max(0, min(100, score))

    if score >= 75:
        risk = "Healthy"
    elif score >= 55:
        risk = "Watchlist"
    elif score >= 35:
        risk = "At risk"
    else:
        risk = "Critical"

    return {
        "score": round(score, 1),
        "risk": risk,
        "top_class": top_class,
        "top_share": round(top_share, 1),
    }


def calculate_quality_score(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=["instrument_name", "asset_class", "roi_pct", "risk_numeric", "quality_score", "recommendation"])

    scored = df.copy()
    if "instrument_name" not in scored.columns:
        scored["instrument_name"] = "Unknown Instrument"
    if "asset_class" not in scored.columns:
        scored["asset_class"] = "Uncategorized"
    if "risk_level" not in scored.columns:
        scored["risk_level"] = "Medium"

    scored["instrument_name"] = scored["instrument_name"].fillna("Unknown Instrument").astype(str)
    scored["asset_class"] = scored["asset_class"].fillna("Uncategorized").astype(str)
    scored["risk_level"] = scored["risk_level"].apply(_normalize_risk_level)

    if "roi_pct" not in scored.columns:
        if "returns_pct" in scored.columns:
            scored["roi_pct"] = pd.to_numeric(scored["returns_pct"], errors="coerce").fillna(0)
        else:
            amount = pd.to_numeric(scored.get("amount_invested", 0), errors="coerce").fillna(0)
            value = pd.to_numeric(scored.get("current_value", 0), errors="coerce").fillna(0)
            scored["roi_pct"] = ((value / amount) - 1) * 100
            scored["roi_pct"] = scored["roi_pct"].where(amount > 0, 0)

    scored["roi_pct"] = pd.to_numeric(scored["roi_pct"], errors="coerce").fillna(0).round(2)
    scored["risk_numeric"] = scored["risk_level"].map(RISK_MAP).fillna(2)
    scored["quality_score"] = 100 + (scored["roi_pct"] * 1.2) - (scored["risk_numeric"] * 12)
    scored["quality_score"] = scored["quality_score"].clip(lower=0, upper=100)

    scored["recommendation"] = "Hold"
    scored.loc[(scored["roi_pct"] < 0) & (scored["risk_numeric"] >= 3), "recommendation"] = "Consider Sell"
    scored.loc[(scored["roi_pct"] > 0) & (scored["quality_score"] >= 65), "recommendation"] = "Strong Buy"
    scored.loc[(scored["quality_score"] >= 70) & (scored["recommendation"] == "Hold"), "recommendation"] = "Buy"

    return scored[["instrument_name", "asset_class", "roi_pct", "risk_numeric", "quality_score", "recommendation"]].sort_values("quality_score", ascending=False)
