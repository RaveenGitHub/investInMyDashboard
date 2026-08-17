from __future__ import annotations

import pandas as pd

from wealth_app.repositories.goals_repository import GoalsRepository


class GoalsService:
    def __init__(self, repository: GoalsRepository | None = None):
        self.repository = repository or GoalsRepository()

    def get_goals_dataframe(self, file_bytes=None, file_name: str = "", search_term: str = "", saved_view: str = "All values") -> pd.DataFrame:
        return self.repository.get_goals_dataframe(file_bytes=file_bytes, file_name=file_name, search_term=search_term, saved_view=saved_view)

    def get_goal_summary(self, df: pd.DataFrame) -> dict:
        if df is None or df.empty:
            return {"count": 0, "avg_progress": 0.0, "total_target": 0.0, "total_savings": 0.0}

        total_target = float(df["target_amount"].sum())
        total_savings = float(df["current_savings"].sum())
        avg_progress = float(df["progress_pct"].mean()) if "progress_pct" in df.columns else 0.0
        return {
            "count": len(df),
            "avg_progress": avg_progress,
            "total_target": total_target,
            "total_savings": total_savings,
        }

    def get_status(self, progress_pct: float) -> str:
        if progress_pct >= 80:
            return "On track"
        if progress_pct >= 40:
            return "Needs attention"
        return "Behind schedule"
