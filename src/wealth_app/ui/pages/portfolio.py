import pandas as pd
import plotly.express as px
import streamlit as st

from data_layer import load_investments
from wealth_app.repositories.portfolio_repository import PortfolioRepository
from wealth_app.services.portfolio_service import PortfolioService
from wealth_app.ui.components.cards import metric_card, page_header, panel, section_toolbar, status_badge
from wealth_app.utils.formatting import money, percent


def render_portfolio_page(investment_upload=None):
    page_header(
        "Portfolio & Investments",
        "Track portfolio value, allocation, and performance across your investments.",
        badge="Portfolio",
    )

    repo = PortfolioRepository()
    service = PortfolioService(repo)

    upload_bytes = investment_upload.getvalue() if investment_upload is not None else None
    upload_name = investment_upload.name if investment_upload is not None else ""
    df = service.get_portfolio_dataframe(file_bytes=upload_bytes, file_name=upload_name, search_term=str(st.session_state.get("global_search", "")).strip(), saved_view=st.session_state.get("saved_view", "All values"))

    if df.empty:
        st.info("Missing data/investments.csv. Add your investment data to enable the dashboard.")
        return

    available_assets, available_risks = service.get_available_filters(df)

    with st.sidebar:
        st.caption("Filters")
        selected_assets = st.multiselect("Asset class", available_assets, default=available_assets)
        min_date = df["date"].min().date()
        max_date = df["date"].max().date()
        start_date, end_date = st.slider(
            "Date range",
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date),
            format="YYYY-MM-DD",
        )
        selected_risks = st.multiselect("Risk level", available_risks, default=available_risks)

    filtered = service.get_filtered_frame(df, selected_assets, start_date, end_date, selected_risks)
    if filtered.empty:
        st.warning("No investments match the current filters.")
        return

    currency_code = st.session_state.get("currency_Portfolio & Investments", "USD")
    compact_mode = st.session_state.get("compact_Portfolio & Investments", False)
    export_cols = ["date", "asset_class", "instrument_name", "amount_invested", "current_value", "returns_pct", "risk_level"]
    export_csv = filtered[export_cols].to_csv(index=False).encode()
    st.download_button("Export filtered investments", export_csv, file_name="filtered_investments.csv", mime="text/csv")

    kpis = service.get_kpis(filtered)
    total_invested = kpis["total_invested"]
    total_value = kpis["total_value"]
    overall_return_pct = kpis["overall_return_pct"]

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Total invested", money(total_invested, currency_code, compact=compact_mode), caption="Capital committed")
    with col2:
        metric_card("Current portfolio value", money(total_value, currency_code, compact=compact_mode), delta=f"{percent(overall_return_pct)} net", delta_positive=overall_return_pct >= 0, caption="Live market value")
    with col3:
        metric_card("Overall return", percent(overall_return_pct), delta_positive=overall_return_pct >= 0, caption="Weighted return on invested capital")

    section_toolbar("Allocation and performance", right_html=status_badge("Mix + trend", "warning"))
    allocation = filtered.groupby("asset_class", as_index=False)["current_value"].sum().sort_values("current_value", ascending=False)
    pie_fig = px.pie(allocation, values="current_value", names="asset_class", title="Asset allocation", hole=0.4)
    pie_fig.update_traces(textinfo="percent+label")

    portfolio_by_date = filtered.groupby("date", as_index=False)["current_value"].sum()
    line_fig = px.line(portfolio_by_date, x="date", y="current_value", markers=True, title="Portfolio value over time")
    line_fig.update_layout(xaxis_title="Date", yaxis_title="Value")

    top_holdings = filtered.sort_values("current_value", ascending=False).head(10)
    bar_fig = px.bar(top_holdings, x="instrument_name", y="current_value", color="asset_class", title="Top holdings by current value")
    bar_fig.update_layout(xaxis_title="Instrument", yaxis_title="Current value")

    st.plotly_chart(pie_fig, use_container_width=True)
    col_a, col_b = st.columns(2)
    col_a.plotly_chart(line_fig, use_container_width=True)
    col_b.plotly_chart(bar_fig, use_container_width=True)

    section_toolbar("Filtered investments", right_html=status_badge(f"{len(filtered)} investments in view", "success"))
    display = filtered[["date", "asset_class", "instrument_name", "amount_invested", "current_value", "returns_pct", "risk_level"]].copy()
    display["amount_invested"] = display["amount_invested"].map(lambda v: money(v, currency_code, compact=compact_mode))
    display["current_value"] = display["current_value"].map(lambda v: money(v, currency_code, compact=compact_mode))
    display["returns_pct"] = display["returns_pct"].map(lambda v: percent(v) if pd.notna(v) else "0%")
    st.dataframe(display, use_container_width=True, hide_index=True)
