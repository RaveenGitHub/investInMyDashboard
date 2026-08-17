from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from wealth_app.repositories.portfolio_repository import PortfolioRepository
from wealth_app.services.calculations import calculate_quality_score
from wealth_app.ui.components.cards import metric_card, page_header, panel, section_toolbar, status_badge
from wealth_app.utils.formatting import percent


def render_quality_dashboard(investment_upload=None):
    page_header(
        "Investment Quality & Decisions",
        "Assess return quality, risk, and simple buy/hold/sell signals.",
        badge="Quality",
    )

    repo = PortfolioRepository()
    df = repo.get_portfolio_dataframe(
        file_bytes=investment_upload.getvalue() if investment_upload is not None else None,
        file_name=investment_upload.name if investment_upload is not None else "",
        search_term=str(st.session_state.get("global_search", "")).strip(),
    )

    if df.empty:
        st.info("Missing data/investments.csv. Add your investment data to enable decision analysis.")
        return

    df = df.copy()
    df["roi_pct"] = ((df["current_value"] / df["amount_invested"]) - 1) * 100
    df["risk_numeric"] = df["risk_level"].map({"Low": 1, "Medium": 2, "High": 3, "Very High": 4}).fillna(2)

    total_value = float(df["current_value"].sum()) if not df.empty else 0.0
    if total_value:
        asset_allocation = df.groupby("asset_class")["current_value"].sum() / total_value * 100
        df["asset_class_allocation_pct"] = df["asset_class"].map(asset_allocation)
    else:
        df["asset_class_allocation_pct"] = 0.0

    df["risk_adjusted_score"] = (((df["roi_pct"] / 100) + 1) / df["risk_numeric"]) * 100
    conditions = [
        (df["roi_pct"] < 0) & (df["risk_numeric"] >= 3),
        (df["roi_pct"] > 0) & (df["asset_class_allocation_pct"] < 10),
    ]
    choices = ["Consider Sell", "Consider Buy"]
    df["decision"] = np.select(conditions, choices, default="Hold")

    export_csv = df[["instrument_name", "asset_class", "roi_pct", "risk_level", "decision", "risk_adjusted_score"]].to_csv(index=False).encode()
    st.download_button("Export decision analysis", export_csv, file_name="investment_decisions.csv", mime="text/csv")

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Average ROI", percent(df["roi_pct"].mean()), caption="Across the filtered portfolio")
    with col2:
        metric_card("Highest risk-adjusted score", percent(df["risk_adjusted_score"].max()), caption="Best relative return efficiency")
    with col3:
        metric_card("Decision mix", str(df["decision"].value_counts().to_dict()), caption="Buy / Hold / Sell signals")

    section_toolbar("Risk vs return", right_html=status_badge("Decision signals", "warning"))
    scatter_fig = px.scatter(
        df,
        x="risk_numeric",
        y="roi_pct",
        color="decision",
        size="current_value",
        hover_name="instrument_name",
        title="Risk vs. return",
        labels={"risk_numeric": "Risk level (1-4)", "roi_pct": "ROI (%)"},
    )
    scatter_fig.update_layout(legend_title_text="Decision")
    st.plotly_chart(scatter_fig, use_container_width=True)

    decision_table = df[["instrument_name", "asset_class", "roi_pct", "risk_level", "decision", "risk_adjusted_score"]].copy()
    decision_table["roi_pct"] = decision_table["roi_pct"].map(lambda x: round(float(x), 2))
    decision_table["risk_adjusted_score"] = decision_table["risk_adjusted_score"].map(lambda x: round(float(x), 2))

    def highlight_decision(value):
        if value == "Consider Sell":
            return "background-color: rgba(255,107,107,0.18); color: #ffc2c2"
        if value == "Consider Buy":
            return "background-color: rgba(139,195,74,0.12); color: #dff7b3"
        return "background-color: rgba(255,200,87,0.12); color: #ffe9b8"

    styled_table = decision_table.style.applymap(highlight_decision, subset=["decision"])
    section_toolbar("Investment decision table", right_html=status_badge("Action queue", "success"))
    st.dataframe(styled_table, use_container_width=True, hide_index=True)

    panel("Quality scorecard", "Portfolio quality view by instrument")
    quality_scores = calculate_quality_score(df)
    if not quality_scores.empty:
        st.dataframe(quality_scores, use_container_width=True, hide_index=True)
