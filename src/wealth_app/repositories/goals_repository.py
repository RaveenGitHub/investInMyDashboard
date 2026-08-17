from __future__ import annotations

import pandas as pd

from data_layer import filter_by_query, load_goals


class GoalsRepository:
    def get_goals_dataframe(self, file_bytes=None, file_name: str = "", search_term: str = "", saved_view: str = "All values") -> pd.DataFrame:
        df = load_goals(file_bytes=file_bytes, file_name=file_name)
        if df is None or df.empty:
            return df.copy() if df is not None else pd.DataFrame(columns=["goal_name", "category", "target_amount", "target_date", "current_savings", "priority"])

        df = df.copy()
        df["progress_pct"] = ((df["current_savings"] / df["target_amount"]) * 100).fillna(0)
        df["remaining_amount"] = (df["target_amount"] - df["current_savings"]).fillna(0)
        df = filter_by_query(df, ["goal_name", "category", "priority"], search_term)

        if saved_view == "Goal at risk":
            df = df[df["progress_pct"] < 40].copy()
        elif saved_view == "Needs attention":
            df = df[df["progress_pct"] < 80].copy()

        return df
