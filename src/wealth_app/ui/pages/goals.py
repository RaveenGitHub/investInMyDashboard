from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from database import insert_goal_record
from wealth_app.services.goals_service import GoalsService
from wealth_app.ui.components.cards import goal_progress_card, metric_card, page_header, panel, section_toolbar, status_badge
from wealth_app.utils.formatting import money, percent


def render_goals_dashboard(goal_upload=None):
    page_header(
        "Goals & Progress",
        "Monitor progress against each life goal and find where action is needed.",
        badge="Goals",
    )

    service = GoalsService()
    goal_rows = service.get_goals_dataframe(
        file_bytes=goal_upload.getvalue() if goal_upload is not None else None,
        file_name=goal_upload.name if goal_upload is not None else "",
        search_term=str(st.session_state.get("global_search", "")).strip(),
        saved_view=st.session_state.get("saved_view", "All values"),
    )

    if goal_rows.empty:
        st.info("Missing data/goals.csv. Add your goal data to track progress.")
        return

    summary = service.get_goal_summary(goal_rows)
    currency_code = st.session_state.get("currency_Goals & Progress", "USD")
    compact_mode = st.session_state.get("compact_Goals & Progress", False)

    with st.form("goal-form", clear_on_submit=True):
        section_toolbar("Add goal", right_html=status_badge("New target", "success"))
        col1, col2 = st.columns(2)
        with col1:
            goal_name = st.text_input("Goal name", value="Emergency Fund")
            category = st.text_input("Category", value="Protection")
            target_amount = st.number_input("Target amount", min_value=0.0, value=50000.0, step=1000.0)
        with col2:
            target_date = st.date_input("Target date", value=pd.Timestamp.today().date())
            priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=1)
            current_savings = st.number_input("Current savings", min_value=0.0, value=20000.0, step=1000.0)
        submitted = st.form_submit_button("Save goal")
        if submitted:
            insert_goal_record(goal_name, category, target_amount, target_date, priority, "active")
            st.success("Goal saved to the local database.")

    export_csv = goal_rows[["goal_name", "category", "target_amount", "target_date", "current_savings", "priority", "progress_pct", "remaining_amount"]].to_csv(index=False).encode()
    st.download_button("Export goals progress", export_csv, file_name="goals_progress.csv", mime="text/csv")

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Number of goals", str(summary["count"]), caption="Active planning items")
    with col2:
        metric_card("Average progress", percent(summary["avg_progress"]), caption="Across the current goal set")
    with col3:
        metric_card("Saved vs target", f"{money(summary['total_savings'], currency_code, compact=compact_mode)} / {money(summary['total_target'], currency_code, compact=compact_mode)}", caption="Total committed capital")

    panel("Goal completion", "Progress across tracked objectives")
    progress_fig = px.bar(goal_rows, x="goal_name", y="progress_pct", color="category", title="Goal completion (%)", text_auto=".1f")
    progress_fig.update_layout(xaxis_title="Goal", yaxis_title="Progress %")
    st.plotly_chart(progress_fig, use_container_width=True)

    panel("Goal details", "Current savings, target progress, and health status")
    for _, row in goal_rows.iterrows():
        progress = float(row["progress_pct"])
        status = service.get_status(progress)
        badge = status_badge(status, "success" if status == "On track" else "warning" if status == "Needs attention" else "danger")
        goal_progress_card(row["goal_name"], progress, float(row["current_savings"]), float(row["target_amount"]), status)
        st.caption(
            f"Current savings: {money(row['current_savings'], currency_code, compact=compact_mode)} | "
            f"Target: {money(row['target_amount'], currency_code, compact=compact_mode)} | "
            f"Progress: {percent(progress)} | "
            f"Remaining: {money(row['remaining_amount'], currency_code, compact=compact_mode)} | "
            f"Status: {status}"
        )

    target_vs_saved = goal_rows[["goal_name", "current_savings", "target_amount"]].copy()
    panel("Savings vs target", "Actual savings compared with milestone objectives")
    st.bar_chart(target_vs_saved.set_index("goal_name"))

    panel("Insights", "Priority notes from the current goal set")
    for _, row in goal_rows.iterrows():
        progress = float(row["progress_pct"])
        insight = service.get_status(progress)
        if insight == "On track":
            st.success(f"{row['goal_name']}: {insight} ({percent(progress)} complete).")
        elif insight == "Needs attention":
            st.warning(f"{row['goal_name']}: {insight} ({percent(progress)} complete).")
        else:
            st.error(f"{row['goal_name']}: {insight} ({percent(progress)} complete).")
