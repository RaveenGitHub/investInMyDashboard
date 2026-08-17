from typing import Any

import pandas as pd

from wealth_app.config.constants import CURRENCY_META


def money(value: Any, currency: str = "USD", compact: bool = False) -> str:
    config = CURRENCY_META.get(str(currency).upper(), CURRENCY_META["USD"])
    symbol = config["symbol"]
    numeric = float(value) if value is not None and not pd.isna(value) else 0.0
    if compact:
        abs_value = abs(numeric)
        if abs_value >= 1_000_000_000:
            return f"{symbol}{numeric / 1_000_000_000:,.2f}B"
        if abs_value >= 1_000_000:
            return f"{symbol}{numeric / 1_000_000:,.2f}M"
        if abs_value >= 1_000:
            return f"{symbol}{numeric / 1_000:,.2f}K"
    return f"{symbol}{numeric:,.0f}"


def percent(value: Any) -> str:
    if value is None or pd.isna(value):
        return "0%"
    return f"{float(value):.1f}%"
