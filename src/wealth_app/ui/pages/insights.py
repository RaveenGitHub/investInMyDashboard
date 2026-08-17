from __future__ import annotations

import pandas as pd
import streamlit as st

from data_layer import compute_quality_score, filter_by_query, load_goals, load_investments
from wealth_app.ui.components.cards import metric_card, page_header, panel, section_toolbar, status_badge
from wealth_app.utils.formatting import money, percent


def render_insights_dashboard():
    page_header(
        "Insights",
        "Priority recommendations, portfolio pressure points, and explicit rebalance actions.",
        badge="Insights",
    )

    investments = load_investments()
    goals = load_goals()
    search_term = str(st.session_state.get("global_search", "")).strip()
    investments = filter_by_query(investments, ["asset_class", "instrument_name", "risk_level"], search_term)
    goals = filter_by_query(goals, ["goal_name", "category", "priority"], search_term)

    if investments.empty and goals.empty:
        st.info("No portfolio data is available for insights yet. Load sample data or upload a workbook.")
        return

    quality_df = compute_quality_score(investments)
    if not quality_df.empty:
        quality_df["quality_score"] = quality_df["quality_score"].round(1)
        risk_rank = quality_df.sort_values("quality_score", ascending=True).copy()
        risk_rank["rank"] = range(1, len(risk_rank) + 1)
        panel("Risk-adjusted ranking", "Assets sorted by quality score and prioritized recommendation")
        st.dataframe(risk_rank[["rank", "instrument_name", "asset_class", "quality_score", "recommendation"]], use_container_width=True, hide_index=True)

    panel("Rebalance suggestions", "Actions based on concentration, risk trend, and goal pressure")
    actions = []
    if not investments.empty:
        total_value = float(investments["current_value"].sum())
        allocation = investments.groupby("asset_class")["current_value"].sum().sort_values(ascending=False)
        for asset_class, value in allocation.items():
            share = (value / total_value) * 100 if total_value else 0
            if share > 45:
                actions.append(f"Reduce concentration in {asset_class} ({share:.1f}% of portfolio). Consider trimming into underweight diversified assets.")
            if share > 30 and asset_class.lower() in {"crypto", "alternative asset classes", "private equity"}:
                actions.append(f"Review {asset_class} exposure. It is above target and may need rebalancing to maintain a more stable risk profile.")
        if investments["returns_pct"].fillna(0).mean() < 0:
            actions.append("Portfolio return trend is weak. Reassess the lowest-return positions and consider rebalancing toward more resilient categories.")

    if not goals.empty:
        goal_rows = goals.copy()
        goal_rows["progress_pct"] = (goal_rows["current_savings"] / goal_rows["target_amount"]) * 100
        at_risk = goal_rows[goal_rows["progress_pct"] < 40]
        if not at_risk.empty:
            for _, row in at_risk.iterrows():
                actions.append(f"{row['goal_name']} is behind schedule ({percent(row['progress_pct'])} complete). Consider increasing monthly savings or reducing the target gap.")

    if actions:
        for action in actions:
            st.warning(action)
    else:
        st.success("No rebalance actions are currently required. Your portfolio and goals remain in a healthy range.")

    panel("Priority goals", "Most urgent milestones requiring resource attention")
    if not goals.empty:
        goal_rows = goals.copy()
        goal_rows["progress_pct"] = (goal_rows["current_savings"] / goal_rows["target_amount"]) * 100
        goal_rows["remaining_amount"] = goal_rows["target_amount"] - goal_rows["current_savings"]
        priority_view = goal_rows.sort_values(["priority", "progress_pct"], ascending=[True, True]).head(10)
        priority_view["priority"] = priority_view["priority"].fillna("Medium")
        st.dataframe(
            priority_view[["goal_name", "category", "priority", "target_amount", "current_savings", "progress_pct", "remaining_amount"]],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No goals are available for priority review.")
