from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
SAMPLE_DIR = PROJECT_DIR / "sample"
INVESTMENTS_PATH = DATA_DIR / "investments.csv"
GOALS_PATH = DATA_DIR / "goals.csv"
SAMPLE_ASSET_PATH = SAMPLE_DIR / "Asset.xlsx"
SAMPLE_GOALS_PATH = SAMPLE_DIR / "Goals.xlsx"

RISK_MAP = {"Low": 1, "Medium": 2, "High": 3, "Very High": 4}
CURRENCY_META = {
    "USD": {"symbol": "$", "code": "USD"},
    "EUR": {"symbol": "€", "code": "EUR"},
    "GBP": {"symbol": "£", "code": "GBP"},
    "INR": {"symbol": "₹", "code": "INR"},
    "JPY": {"symbol": "¥", "code": "JPY"},
}


def get_currency_config(currency_code="USD"):
    normalized = str(currency_code or "USD").upper()
    return CURRENCY_META.get(normalized, {"symbol": "$", "code": "USD"})


def format_currency(value, currency_code="USD", compact=False):
    config = get_currency_config(currency_code)
    symbol = config["symbol"]
    numeric = float(value) if not pd.isna(value) else 0.0
    if compact:
        abs_value = abs(numeric)
        if abs_value >= 1_000_000_000:
            return f"{symbol}{numeric / 1_000_000_000:,.2f}B"
        if abs_value >= 1_000_000:
            return f"{symbol}{numeric / 1_000_000:,.2f}M"
        if abs_value >= 1_000:
            return f"{symbol}{numeric / 1_000:,.2f}K"
    if pd.isna(value):
        return f"{symbol}0"
    return f"{symbol}{numeric:,.0f}"


def money(value, currency="USD", compact=False):
    return format_currency(value, currency, compact=compact)


def percent(value):
    if pd.isna(value):
        return "0%"
    return f"{value:.1f}%"


def build_sample_bundle():
    import io
    import zipfile

    bundle = io.BytesIO()
    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in [SAMPLE_ASSET_PATH, SAMPLE_GOALS_PATH]:
            if file_path.exists():
                archive.write(file_path, arcname=file_path.name)
    return bundle.getvalue()
