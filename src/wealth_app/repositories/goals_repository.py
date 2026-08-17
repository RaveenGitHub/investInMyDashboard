from __future__ import annotations

import pandas as pd

from data_layer import filter_by_query, load_goals


class GoalsRepository:
    @staticmethod
    def _empty_dataframe() -> pd.DataFrame:
        return pd.DataFrame(columns=["goal_name", "category", "target_amount", "target_date", "current_savings", "priority", "progress_pct", "remaining_amount"])

    def get_goals_dataframe(self, file_bytes=None, file_name: str = "", search_term: str = "", saved_view: str = "All values") -> pd.DataFrame:
        df = load_goals(file_bytes=file_bytes, file_name=file_name)
        if df is None or df.empty:
            return self._empty_dataframe()

        df = df.copy()
        required_columns = ["goal_name", "category", "target_amount", "target_date", "current_savings", "priority"]
        missing = [column for column in required_columns if column not in df.columns]
        if missing:
            return self._empty_dataframe()

        df["target_amount"] = pd.to_numeric(df["target_amount"], errors="coerce").fillna(0)
        df["current_savings"] = pd.to_numeric(df["current_savings"], errors="coerce").fillna(0)
        df["progress_pct"] = ((df["current_savings"] / df["target_amount"]).replace([float("inf"), -float("inf")], 0) * 100).fillna(0)
        df["progress_pct"] = df["progress_pct"].where(df["target_amount"] > 0, 0)
        df["remaining_amount"] = (df["target_amount"] - df["current_savings"]).fillna(0)

        search_columns = ["goal_name", "category", "priority"]
        available = [column for column in search_columns if column in df.columns]
        if available:
            df = filter_by_query(df, available, search_term)

        if saved_view == "Goal at risk" and "progress_pct" in df.columns:
            df = df[df["progress_pct"] < 40].copy()
        elif saved_view == "Needs attention" and "progress_pct" in df.columns:
            df = df[df["progress_pct"] < 80].copy()

        return df.reset_index(drop=True)
