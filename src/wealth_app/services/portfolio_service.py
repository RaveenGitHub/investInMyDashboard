from __future__ import annotations

import pandas as pd

from wealth_app.repositories.portfolio_repository import PortfolioRepository


class PortfolioService:
    def __init__(self, repository: PortfolioRepository | None = None):
        self.repository = repository or PortfolioRepository()

    def get_portfolio_dataframe(self, file_bytes=None, file_name: str = "", search_term: str = "", saved_view: str = "All values") -> pd.DataFrame:
        return self.repository.get_portfolio_dataframe(file_bytes=file_bytes, file_name=file_name, search_term=search_term, saved_view=saved_view)

    def get_available_filters(self, df: pd.DataFrame) -> tuple[list[str], list[str]]:
        return sorted(df["asset_class"].dropna().unique()), sorted(df["risk_level"].dropna().unique())

    def get_kpis(self, df: pd.DataFrame) -> dict:
        total_invested = float(df["amount_invested"].sum()) if not df.empty else 0.0
        total_value = float(df["current_value"].sum()) if not df.empty else 0.0
        overall_return_pct = ((total_value - total_invested) / total_invested * 100) if total_invested else 0.0
        return {
            "total_invested": total_invested,
            "total_value": total_value,
            "overall_return_pct": overall_return_pct,
        }

    def get_filtered_frame(self, df: pd.DataFrame, selected_assets: list[str], start_date, end_date, selected_risks: list[str]) -> pd.DataFrame:
        filtered = df[
            (df["asset_class"].isin(selected_assets))
            & (df["date"] >= pd.Timestamp(start_date))
            & (df["date"] <= pd.Timestamp(end_date))
            & (df["risk_level"].isin(selected_risks))
        ].copy()
        return filtered


def filter_portfolio_view(df: pd.DataFrame, search_term: str = "", saved_view: str = "All values") -> pd.DataFrame:
    service = PortfolioService()
    return service.get_portfolio_dataframe(search_term=search_term, saved_view=saved_view, file_bytes=None, file_name="") if df is None else df


def build_portfolio_kpis(df: pd.DataFrame) -> dict:
    return PortfolioService().get_kpis(df)
