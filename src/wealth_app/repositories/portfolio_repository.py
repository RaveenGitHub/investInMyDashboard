from __future__ import annotations

import pandas as pd

from data_layer import filter_by_query, load_investments


class PortfolioRepository:
    def get_portfolio_dataframe(self, file_bytes=None, file_name: str = "", search_term: str = "", saved_view: str = "All values") -> pd.DataFrame:
        df = load_investments(file_bytes=file_bytes, file_name=file_name)
        df = filter_by_query(df, ["asset_class", "instrument_name", "risk_level"], search_term)

        if saved_view == "High risk":
            df = df[df["risk_level"].isin(["High", "Very High"])].copy()
        elif saved_view == "Needs attention":
            df = df[df["returns_pct"] < 0].copy()

        return df
