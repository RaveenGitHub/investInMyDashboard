import io
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from app_config import GOALS_PATH, INVESTMENTS_PATH, PROJECT_DIR, RISK_MAP, SAMPLE_ASSET_PATH, SAMPLE_GOALS_PATH


def read_uploaded_file(file_obj):
    if file_obj is None:
        return None

    file_name = file_obj.name.lower()
    buffer = io.BytesIO(file_obj.getvalue())

    if file_name.endswith(".csv"):
        return pd.read_csv(buffer)
    if file_name.endswith(".xlsx") or file_name.endswith(".xlsm"):
        return pd.read_excel(buffer, engine="openpyxl")
    if file_name.endswith(".xls"):
        return pd.read_excel(buffer, engine="xlrd")
    return pd.read_csv(buffer)


def read_uploaded_bytes(file_bytes, file_name):
    if file_bytes is None:
        return None

    file_name = (file_name or "").lower()
    buffer = io.BytesIO(file_bytes)

    if file_name.endswith(".csv"):
        return pd.read_csv(buffer)
    if file_name.endswith(".xlsx") or file_name.endswith(".xlsm"):
        return pd.read_excel(buffer, engine="openpyxl")
    if file_name.endswith(".xls"):
        return pd.read_excel(buffer, engine="xlrd")
    return pd.read_csv(buffer)


def normalize_column_name(column_name):
    if pd.isna(column_name):
        return ""
    normal = str(column_name).strip().lower().replace("\t", " ").replace("-", " ").replace("_", " ")
    return " ".join(normal.split())


def normalize_investments_frame(df):
    if df is None or df.empty:
        return pd.DataFrame(columns=["date", "asset_class", "instrument_name", "amount_invested", "current_value", "returns_pct", "risk_level"])

    df = df.copy()
    df.columns = [normalize_column_name(col) for col in df.columns]

    field_map = {
        "date": ["date", "investment date", "purchase date"],
        "asset_class": ["asset type", "asset category", "asset catogry", "asset catagory", "asset class"],
        "instrument_name": ["asset name", "instrument name", "name"],
        "amount_invested": ["amount invested", "amount invested inr", "amount invested in", "amount_invested", "investment amount"],
        "current_value": ["current asset value", "current value", "current_value", "market value"],
        "returns_pct": ["returns pct", "return pct", "returns_pct", "roi", "return %"],
        "risk_level": ["risk level", "risk_level", "risk"],
    }

    normalized = {}
    for expected, aliases in field_map.items():
        matching = next((col for col in df.columns if col in aliases), None)
        if matching is not None:
            normalized[expected] = df[matching]

    if not normalized:
        return pd.DataFrame(columns=["date", "asset_class", "instrument_name", "amount_invested", "current_value", "returns_pct", "risk_level"])

    result = pd.DataFrame(normalized)

    if "asset_class" not in result.columns:
        result["asset_class"] = "Uncategorized"
    if "instrument_name" not in result.columns:
        result["instrument_name"] = "Unknown Instrument"
    if "amount_invested" not in result.columns:
        result["amount_invested"] = 0
    if "current_value" not in result.columns:
        result["current_value"] = 0

    if "date" in result.columns:
        result["date"] = pd.to_datetime(result["date"], errors="coerce")
        if result["date"].isna().any():
            valid_dates = result["date"].notna()
            if valid_dates.any():
                last_valid_date = result.loc[valid_dates, "date"].iloc[-1]
                missing_mask = result["date"].isna()
                result.loc[missing_mask, "date"] = pd.date_range(start=last_valid_date + pd.Timedelta(days=1), periods=missing_mask.sum(), freq="D")
            else:
                result["date"] = pd.date_range(end=pd.Timestamp.today(), periods=len(result), freq="D")
    else:
        result["date"] = pd.date_range(end=pd.Timestamp.today(), periods=len(result), freq="D")

    asset_type_col = next((col for col in df.columns if col == "asset type"), None)
    asset_category_col = next((col for col in df.columns if col in {"asset category", "asset catogry", "asset catagory"}), None)
    if asset_type_col and asset_category_col and "asset_class" in result.columns:
        result["asset_class"] = result["asset_class"].fillna(df[asset_type_col].astype(str))
        result["asset_class"] = result["asset_class"].astype(str).str.strip()

    result["asset_class"] = result["asset_class"].fillna("Uncategorized").astype(str).str.strip()
    result["instrument_name"] = result["instrument_name"].fillna("Unknown Instrument").astype(str).str.strip()
    result["amount_invested"] = pd.to_numeric(result["amount_invested"], errors="coerce").fillna(0)
    result["current_value"] = pd.to_numeric(result["current_value"], errors="coerce").fillna(0)
    result["risk_level"] = result["risk_level"].fillna("Medium") if "risk_level" in result.columns else "Medium"
    result["risk_level"] = result["risk_level"].astype(str).str.title().str.strip()

    if "returns_pct" not in result.columns or result["returns_pct"].isna().all():
        result["returns_pct"] = ((result["current_value"] / result["amount_invested"]) - 1) * 100
        result["returns_pct"] = result["returns_pct"].replace([np.inf, -np.inf], 0)
    else:
        result["returns_pct"] = pd.to_numeric(result["returns_pct"], errors="coerce").fillna(0)

    required_columns = ["date", "asset_class", "instrument_name", "amount_invested", "current_value", "returns_pct", "risk_level"]
    return result[required_columns].dropna(subset=["date", "asset_class", "instrument_name", "amount_invested", "current_value"]).reset_index(drop=True)


def apply_dark_theme():
    st.markdown(
        """
        <style>
        :root {
            --bg-base: #050505;
            --bg-surface: #111111;
            --bg-panel: #1A1A1A;
            --bg-panel-2: #212121;
            --border-soft: rgba(255, 215, 0, 0.18);
            --text-primary: #F5F5F5;
            --text-muted: #B8B8B8;
            --gold-1: #FFF2B2;
            --gold-2: #FFD700;
            --gold-3: #D4A100;
            --success: #8BC34A;
            --warning: #FFC857;
            --danger: #FF6B6B;
        }

        html, body, [data-testid="stAppViewContainer"], .stApp {
            background: linear-gradient(180deg, #050505 0%, #111111 100%);
            color: var(--text-primary);
            font-family: "Inter", "Segoe UI", Arial, sans-serif;
        }

        .stApp {
            background-image: radial-gradient(circle at top left, rgba(255, 215, 0, 0.12), transparent 22%),
                radial-gradient(circle at top right, rgba(255, 215, 0, 0.08), transparent 18%);
        }

        .stSidebar {
            background: rgba(12, 12, 12, 0.96);
            border-right: 1px solid var(--border-soft);
        }

        .stSidebar .block-container {
            padding-top: 1.25rem;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1600px;
        }

        .stMetric {
            background: linear-gradient(180deg, rgba(26, 26, 26, 0.96), rgba(17, 17, 17, 0.96));
            border: 1px solid var(--border-soft);
            border-radius: 18px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.24);
            padding: 1.1rem 1rem;
        }

        .stMetric [data-testid="stMetricLabel"] {
            color: var(--text-muted) !important;
            font-weight: 600;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            font-size: 0.72rem;
        }

        .stMetric [data-testid="stMetricValue"] {
            color: var(--text-primary) !important;
            font-weight: 700;
            font-size: clamp(1.2rem, 2vw, 2rem) !important;
        }

        h1, h2, h3, h4, .stTabs [role="tablist"] button, .stSelectbox, .stMultiSelect, .stTextInput, .stSlider, .stCheckbox {
            color: var(--text-primary) !important;
        }

        h1 {
            font-size: clamp(2rem, 2.7vw, 3rem) !important;
            letter-spacing: -0.04em;
            font-weight: 800 !important;
            margin-bottom: 0.2rem !important;
        }

        h2 {
            font-size: clamp(1.35rem, 1.7vw, 1.9rem) !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
        }

        h3 {
            font-size: 1.05rem !important;
            font-weight: 700 !important;
            letter-spacing: -0.01em;
        }

        p, label, .stDataFrame, .stTable {
            color: var(--text-primary) !important;
        }

        .stDataFrame, .stTable {
            background: rgba(17, 17, 17, 0.86);
            border: 1px solid var(--border-soft);
            border-radius: 16px;
            overflow: hidden;
        }

        .stButton > button,
        .stDownloadButton > button {
            border: 1px solid rgba(255, 215, 0, 0.5);
            border-radius: 12px;
            font-weight: 700;
            transition: all 180ms ease;
            box-shadow: 0 0 0 rgba(0, 0, 0, 0);
        }

        .stButton > button {
            background: linear-gradient(180deg, rgba(255, 215, 0, 0.14), rgba(212, 161, 0, 0.18));
            color: var(--text-primary);
        }

        .stDownloadButton > button {
            background: linear-gradient(180deg, rgba(255, 215, 0, 0.28), rgba(212, 161, 0, 0.35));
            color: #0A0A0A;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 8px 18px rgba(255, 215, 0, 0.12);
        }

        .stTabs [role="tablist"] button {
            border-radius: 12px 12px 0 0;
            padding: 0.6rem 1rem;
            border: 1px solid transparent;
        }

        .stTabs [role="tablist"] .st-bx {
            background: rgba(26, 26, 26, 0.85);
        }

        .stTabs [role="tablist"] button[aria-selected="true"] {
            background: linear-gradient(180deg, rgba(255, 215, 0, 0.12), rgba(17, 17, 17, 0.95));
            border-color: var(--border-soft);
            color: var(--gold-1) !important;
        }

        .stPlotlyChart, .element-container .stPlotlyChart {
            background: rgba(17, 17, 17, 0.7);
            border-radius: 18px;
            border: 1px solid var(--border-soft);
        }

        .stProgress > div > div {
            background: linear-gradient(90deg, var(--gold-2), var(--gold-3));
        }

        .stSuccess {
            background: rgba(139, 195, 74, 0.1);
            border: 1px solid rgba(139, 195, 74, 0.3);
            color: #dff7b3 !important;
        }

        .stWarning {
            background: rgba(255, 200, 87, 0.1);
            border: 1px solid rgba(255, 200, 87, 0.3);
            color: #ffe4a3 !important;
        }

        .stInfo {
            background: rgba(255, 215, 0, 0.08);
            border: 1px solid rgba(255, 215, 0, 0.22);
            color: #f5e8a2 !important;
        }

        .stSidebar .stSelectbox div[role="button"],
        .stSidebar .stTextInput input,
        .stSidebar .stNumberInput input,
        .stSidebar .stDateInput input {
            background: rgba(26, 26, 26, 0.94);
            border: 1px solid var(--border-soft);
            border-radius: 10px;
            color: var(--text-primary);
        }

        .stSidebar .stDownloadButton > button {
            width: 100%;
            justify-content: center;
        }

        .brand-header {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.4rem 0.3rem 1rem;
            border-bottom: 1px solid var(--border-soft);
            margin-bottom: 0.9rem;
        }

        .brand-mark {
            width: 36px;
            height: 36px;
            border-radius: 12px;
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.18);
        }

        .brand-name {
            font-weight: 800;
            color: var(--gold-1);
            letter-spacing: 0.04em;
            font-size: 0.92rem;
            text-transform: uppercase;
        }

        .brand-tag {
            color: var(--text-muted);
            font-size: 0.7rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_investments(file_bytes=None, file_name=""):
    if file_bytes is not None:
        df = read_uploaded_bytes(file_bytes, file_name)
    elif SAMPLE_ASSET_PATH.exists():
        df = pd.read_excel(SAMPLE_ASSET_PATH, engine="openpyxl")
    elif INVESTMENTS_PATH.exists():
        df = pd.read_csv(INVESTMENTS_PATH)
    else:
        return pd.DataFrame(columns=["date", "asset_class", "instrument_name", "amount_invested", "current_value", "returns_pct", "risk_level"])

    df = normalize_investments_frame(df)
    return df


@st.cache_data
def load_goals(file_bytes=None, file_name=""):
    if file_bytes is not None:
        df = read_uploaded_bytes(file_bytes, file_name)
    elif SAMPLE_GOALS_PATH.exists():
        df = pd.read_excel(SAMPLE_GOALS_PATH, engine="openpyxl")
    elif GOALS_PATH.exists():
        df = pd.read_csv(GOALS_PATH)
    else:
        return pd.DataFrame(columns=["goal_name", "category", "target_amount", "target_date", "current_savings", "priority"])

    required_columns = ["goal_name", "category", "target_amount", "target_date", "current_savings", "priority"]
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        return pd.DataFrame(columns=required_columns)

    df = df.copy()
    df["target_date"] = pd.to_datetime(df["target_date"], errors="coerce")
    df["target_amount"] = pd.to_numeric(df["target_amount"], errors="coerce")
    df["current_savings"] = pd.to_numeric(df["current_savings"], errors="coerce")
    df["goal_name"] = df["goal_name"].astype(str).str.strip()
    df["category"] = df["category"].astype(str).str.strip()
    df["priority"] = df["priority"].astype(str).str.title().str.strip()
    return df.dropna(subset=["goal_name", "target_amount", "current_savings", "target_date"]).reset_index(drop=True)


def filter_by_query(df, search_columns, query):
    if df is None or df.empty or not query:
        return df
    needle = str(query).strip().lower()
    if not needle:
        return df
    mask = pd.Series(False, index=df.index)
    for column in search_columns:
        if column in df.columns:
            mask |= df[column].astype(str).str.lower().str.contains(needle, na=False)
    return df[mask]


def compute_portfolio_health(investments_df):
    if investments_df is None or investments_df.empty:
        return {"score": 0, "risk": "N/A", "top_class": "N/A", "top_share": 0}

    total_value = float(investments_df["current_value"].sum())
    if total_value <= 0:
        return {"score": 0, "risk": "Very weak", "top_class": "N/A", "top_share": 0}

    allocation = investments_df.groupby("asset_class")["current_value"].sum().sort_values(ascending=False)
    top_class = allocation.index[0]
    top_share = float(allocation.iloc[0] / total_value * 100)

    returns = investments_df["returns_pct"].fillna(0)
    avg_return = float(returns.mean())
    negative_count = float((returns < 0).sum())
    weighted_risk = investments_df["risk_level"].map(RISK_MAP).fillna(2).mean()

    score = 100
    score -= max(0, top_share - 45) * 0.8
    score -= max(0, weighted_risk - 2.2) * 12
    score -= negative_count / max(len(investments_df), 1) * 30
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

    return {"score": round(score, 1), "risk": risk, "top_class": top_class, "top_share": round(top_share, 1)}


def build_goal_gap_alerts(goals_df):
    if goals_df is None or goals_df.empty:
        return []

    alerts = []
    for _, row in goals_df.iterrows():
        target = float(row.get("target_amount", 0) or 0)
        saved = float(row.get("current_savings", 0) or 0)
        if target <= 0:
            continue
        progress_pct = (saved / target) * 100
        remaining = max(target - saved, 0)
        target_date = pd.to_datetime(row.get("target_date"), errors="coerce")
        months_remaining = 0
        if pd.notna(target_date):
            months_remaining = max((target_date.year - pd.Timestamp.today().year) * 12 + (target_date.month - pd.Timestamp.today().month), 1)
        monthly_need = remaining / months_remaining if months_remaining else remaining
        if progress_pct < 80 or remaining > 0:
            alerts.append({
                "goal_name": row.get("goal_name", "Goal"),
                "progress_pct": round(progress_pct, 1),
                "remaining_amount": remaining,
                "monthly_need": monthly_need,
                "status": "On track" if progress_pct >= 80 else "Needs attention" if progress_pct >= 40 else "Behind schedule",
            })
    return alerts


def build_forecast_summary(investments_df, goals_df):
    forecast = []
    if investments_df is not None and not investments_df.empty:
        portfolio_value = float(investments_df["current_value"].sum())
        expected_return = float((investments_df["returns_pct"].fillna(0).mean() / 100) * portfolio_value)
        forecast.append({"label": "Portfolio annual run rate", "value": expected_return})

    if goals_df is not None and not goals_df.empty:
        remaining_total = float(goals_df["target_amount"].sum() - goals_df["current_savings"].sum())
        forecast.append({"label": "Goal gap to close", "value": max(remaining_total, 0)})

    return forecast


def compute_quality_score(df):
    if df is None or df.empty:
        return pd.DataFrame(columns=["instrument_name", "asset_class", "roi_pct", "risk_numeric", "quality_score", "recommendation"])

    scored = df.copy()
    if "roi_pct" not in scored.columns:
        if "returns_pct" in scored.columns:
            scored["roi_pct"] = pd.to_numeric(scored["returns_pct"], errors="coerce").fillna(0)
        else:
            amount = pd.to_numeric(scored.get("amount_invested", 0), errors="coerce").fillna(0)
            value = pd.to_numeric(scored.get("current_value", 0), errors="coerce").fillna(0)
            scored["roi_pct"] = np.where(amount > 0, ((value / amount) - 1) * 100, 0)

    scored["roi_pct"] = pd.to_numeric(scored["roi_pct"], errors="coerce").fillna(0)
    scored["risk_numeric"] = scored["risk_level"].map(RISK_MAP).fillna(2)
    scored["quality_score"] = 100 + (scored["roi_pct"] * 1.2) - (scored["risk_numeric"] * 12)
    scored["quality_score"] = scored["quality_score"].clip(lower=0, upper=100)

    scored["recommendation"] = "Hold"
    scored.loc[(scored["roi_pct"] < 0) & (scored["risk_numeric"] >= 3), "recommendation"] = "Consider Sell"
    scored.loc[(scored["roi_pct"] > 0) & (scored["quality_score"] >= 65), "recommendation"] = "Strong Buy"
    scored.loc[(scored["quality_score"] >= 70) & (scored["recommendation"] == "Hold"), "recommendation"] = "Buy"

    return scored[["instrument_name", "asset_class", "roi_pct", "risk_numeric", "quality_score", "recommendation"]].sort_values("quality_score", ascending=False)
