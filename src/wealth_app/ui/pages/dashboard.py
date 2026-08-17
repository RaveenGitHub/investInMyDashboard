import pandas as pd
import plotly.express as px
import streamlit as st

from data_layer import (
    build_forecast_summary,
    build_goal_gap_alerts,
    compute_portfolio_health,
    compute_quality_score,
    filter_by_query,
    load_goals,
    load_investments,
)
from wealth_app.ui.components.cards import goal_progress_card, metric_card, page_header, section_toolbar, status_badge
from wealth_app.utils.formatting import money, percent


def render_dashboard_page():
    page_header(
        "Dashboard",
        "Executive overview of portfolio health, recurring contributions, and goal progress.",
        badge="Live",
    )

    investments = load_investments()
    goals = load_goals()
    search_term = str(st.session_state.get("global_search", "")).strip()
    investments = filter_by_query(investments, ["asset_class", "instrument_name", "risk_level"], search_term)
    goals = filter_by_query(goals, ["goal_name", "category", "priority"], search_term)

    if investments.empty and goals.empty:
        st.info("No dashboard data matches the current search. Try clearing the search or loading sample data.")
        return

    total_invested = float(investments["amount_invested"].sum()) if not investments.empty else 0.0
    total_value = float(investments["current_value"].sum()) if not investments.empty else 0.0
    overall_return_pct = ((total_value - total_invested) / total_invested * 100) if total_invested else 0.0
    goal_total = float(goals["target_amount"].sum()) if not goals.empty else 0.0
    goal_saved = float(goals["current_savings"].sum()) if not goals.empty else 0.0
    goal_progress = ((goal_saved / goal_total) * 100) if goal_total else 0.0

    portfolio_health = compute_portfolio_health(investments)
    goal_alerts = build_goal_gap_alerts(goals)
    forecast_summary = build_forecast_summary(investments, goals)

    currency_code = st.session_state.get("currency_Dashboard", "USD")
    compact_mode = st.session_state.get("compact_Dashboard", False)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Portfolio value", money(total_value, currency_code, compact=compact_mode), delta=f"{percent(overall_return_pct)} net", delta_positive=overall_return_pct >= 0)
    with col2:
        metric_card("Invested", money(total_invested, currency_code, compact=compact_mode), caption="Total capital committed")
    with col3:
        metric_card("Return", percent(overall_return_pct), delta_positive=overall_return_pct >= 0, caption="Return on current invested capital")
    with col4:
        metric_card("Goal progress", percent(goal_progress), caption="Across active goals")

    section_toolbar("Portfolio health", right_html=status_badge("Key risk & exposure", "warning"))
    health_col1, health_col2, health_col3 = st.columns(3)
    with health_col1:
        metric_card("Health score", f"{portfolio_health['score']}/100", caption="Composite score")
    with health_col2:
        metric_card("Risk signal", portfolio_health["risk"], caption="Current risk posture")
    with health_col3:
        metric_card("Top concentration", f"{portfolio_health['top_class']} ({portfolio_health['top_share']}%)", caption="Largest allocation")

    section_toolbar("Goal gap alerts", right_html=status_badge("Priority watchlist", "warning"))
    if goal_alerts:
        for alert in goal_alerts[:5]:
            st.warning(
                f"{alert['goal_name']}: {alert['status']} — "
                f"{money(alert['remaining_amount'], currency_code, compact=True)} remaining. "
                f"Suggested monthly need: {money(alert['monthly_need'], currency_code, compact=True)}."
            )
    else:
        st.success("All goals are tracking above the warning threshold.")

    section_toolbar("Annual forecast summary", right_html=status_badge("Forecast", "success"))
    forecast_df = pd.DataFrame(forecast_summary)
    if not forecast_df.empty:
        forecast_df["value"] = pd.to_numeric(forecast_df["value"], errors="coerce").fillna(0)
        st.dataframe(forecast_df, use_container_width=True, hide_index=True)

    if not investments.empty:
        allocation = investments.groupby("asset_class", as_index=False)["current_value"].sum().sort_values("current_value", ascending=False)
        pie_fig = px.pie(allocation, values="current_value", names="asset_class", title="Current allocation")
        st.plotly_chart(pie_fig, use_container_width=True)

        portfolio_by_date = investments.groupby("date", as_index=False)["current_value"].sum()
        line_fig = px.line(portfolio_by_date, x="date", y="current_value", markers=True, title="Portfolio value over time")
        st.plotly_chart(line_fig, use_container_width=True)

    if not goals.empty:
        goals_summary = goals[["goal_name", "target_amount", "current_savings"]].copy()
        goals_summary["progress_pct"] = (goals_summary["current_savings"] / goals_summary["target_amount"]) * 100
        goal_bar = px.bar(goals_summary, x="goal_name", y="progress_pct", title="Goal completion")
        st.plotly_chart(goal_bar, use_container_width=True)

    section_toolbar("Investment quality scorecard", right_html=status_badge("Score", "warning"))
    quality_df = compute_quality_score(investments)
    if not quality_df.empty:
        quality_df["quality_score"] = quality_df["quality_score"].round(1)
        st.dataframe(quality_df.head(10), use_container_width=True, hide_index=True)

    section_toolbar("Insights & actions", right_html=status_badge("Priority", "warning"))
    insight_items = []
    if not investments.empty:
        top_risk = investments.sort_values("returns_pct", ascending=True).head(1)
        if not top_risk.empty:
            insight_items.append(f"Lowest performer: {top_risk.iloc[0]['instrument_name']} at {percent(top_risk.iloc[0]['returns_pct'])} return.")
    if not goals.empty:
        worst_goal = goals.sort_values("current_savings", ascending=True).head(1)
        if not worst_goal.empty:
            insight_items.append(
                f"Goal needing attention: {worst_goal.iloc[0]['goal_name']} is at {percent((worst_goal.iloc[0]['current_savings'] / worst_goal.iloc[0]['target_amount']) * 100)} progress."
            )
    if not insight_items:
        insight_items.append("No immediate action items. Portfolio is stable and goals remain in a healthy range.")
    for insight in insight_items:
        st.info(insight)
