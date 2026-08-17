from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from database import get_recurring_transactions, insert_recurring_transaction
from wealth_app.ui.components.cards import metric_card, page_header, panel, section_toolbar, status_badge
from wealth_app.utils.formatting import money


def render_recurring_dashboard():
    page_header(
        "Daily & Monthly Investments",
        "Track recurring contributions, planned cash flow, and monthly investment pacing.",
        badge="Planning",
    )

    with st.form("recurring-investment-form", clear_on_submit=True):
        section_toolbar("Add recurring investment plan", right_html=status_badge("New plan", "success"))
        col1, col2 = st.columns(2)
        with col1:
            template_name = st.text_input("Template name", value="Monthly SIP")
            instrument_name = st.text_input("Investment/instrument", value="Mutual Fund SIP")
            account_name = st.text_input("Account", value="Primary Portfolio")
        with col2:
            amount = st.number_input("Amount", min_value=0.0, value=5000.0, step=100.0)
            frequency = st.selectbox("Frequency", ["daily", "weekly", "monthly"], index=2)
            next_due_date = st.date_input("Next due date", value=pd.Timestamp.today().date())
            status = st.selectbox("Status", ["active", "paused", "completed"], index=0)
        submitted = st.form_submit_button("Save recurring plan")
        if submitted and amount > 0:
            insert_recurring_transaction(
                template_name=template_name,
                instrument_name=instrument_name,
                amount=amount,
                frequency=frequency,
                next_due_date=next_due_date,
                account_name=account_name,
                status=status,
            )
            st.success("Recurring investment plan saved.")

    recurring = pd.DataFrame(get_recurring_transactions())
    if recurring.empty:
        st.info("No recurring investment plans yet. Add one to start tracking monthly pacing.")
        return

    recurring["amount"] = pd.to_numeric(recurring["amount"], errors="coerce").fillna(0)
    recurring["next_due_date"] = pd.to_datetime(recurring["next_due_date"], errors="coerce")

    monthly_total = float(recurring[recurring["frequency"] == "monthly"]["amount"].sum())
    weekly_total = float(recurring[recurring["frequency"] == "weekly"]["amount"].sum())
    daily_total = float(recurring[recurring["frequency"] == "daily"]["amount"].sum())
    upcoming_due = recurring[recurring["next_due_date"].dt.to_period("M") == pd.Timestamp.today().to_period("M")]

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Monthly total planned", money(monthly_total, "USD", compact=True), caption="Scheduled recurring inflow")
    with col2:
        metric_card("Weekly total planned", money(weekly_total, "USD", compact=True), caption="Pacing on a weekly basis")
    with col3:
        metric_card("Daily total planned", money(daily_total, "USD", compact=True), caption="Daily contribution baseline")
    st.caption(f"Due this month: {len(upcoming_due)}")

    panel("Recurring contribution table", "Current recurring investment plans and next dates")
    display = recurring[["template_name", "instrument_name", "account_name", "frequency", "amount", "next_due_date", "status"]].copy()
    display["amount"] = display["amount"].map(lambda value: money(value, "USD", compact=True))
    display["next_due_date"] = display["next_due_date"].dt.strftime("%Y-%m-%d")
    st.dataframe(display, use_container_width=True, hide_index=True)

    future_months = pd.date_range(start=pd.Timestamp.today(), periods=6, freq="MS")
    projection_rows = []
    for month in future_months:
        for _, row in recurring.iterrows():
            amount = float(row["amount"] or 0)
            freq = str(row["frequency"] or "monthly").lower()
            if freq == "monthly":
                projected_amount = amount
            elif freq == "weekly":
                projected_amount = amount * 4.33
            else:
                projected_amount = amount * 30
            projection_rows.append({
                "month": month.strftime("%b %Y"),
                "plan": row["template_name"],
                "projected_contribution": projected_amount,
            })

    if projection_rows:
        panel("6-month contribution forecast", "Planned contribution trajectory over the next half-year")
        forecast_df = pd.DataFrame(projection_rows)
        forecast_summary = forecast_df.groupby("month", as_index=False)["projected_contribution"].sum()
        chart = px.bar(forecast_summary, x="month", y="projected_contribution", title="Projected recurring contribution")
        st.plotly_chart(chart, use_container_width=True)
