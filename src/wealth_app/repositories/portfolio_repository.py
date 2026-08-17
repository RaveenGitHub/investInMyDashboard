from __future__ import annotations

import pandas as pd

from data_layer import filter_by_query, load_investments


class PortfolioRepository:
    @staticmethod
    def _empty_dataframe() -> pd.DataFrame:
        return pd.DataFrame(columns=["date", "asset_class", "instrument_name", "amount_invested", "current_value", "returns_pct", "risk_level"])

    def get_portfolio_dataframe(self, file_bytes=None, file_name: str = "", search_term: str = "", saved_view: str = "All values") -> pd.DataFrame:
        df = load_investments(file_bytes=file_bytes, file_name=file_name)
        if df is None or df.empty:
            return self._empty_dataframe()

        df = df.copy()
        if not isinstance(df, pd.DataFrame):
            return self._empty_dataframe()

        search_columns = ["asset_class", "instrument_name", "risk_level"]
        available = [column for column in search_columns if column in df.columns]
        if available:
            df = filter_by_query(df, available, search_term)

        if saved_view == "High risk" and "risk_level" in df.columns:
            normalized = df["risk_level"].fillna("").astype(str).str.strip().str.lower()
            df = df[normalized.isin({"high", "very high"})].copy()
        elif saved_view == "Needs attention" and "returns_pct" in df.columns:
            returns = pd.to_numeric(df["returns_pct"], errors="coerce").fillna(0)
            df = df[returns < 0].copy()

        return df.reset_index(drop=True)
