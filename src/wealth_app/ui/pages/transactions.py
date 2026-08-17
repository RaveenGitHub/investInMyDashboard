from __future__ import annotations

import pandas as pd
import streamlit as st

from database import get_holdings_summary, get_transaction_ledger
from data_layer import filter_by_query
from wealth_app.ui.components.cards import metric_card, page_header, panel, section_toolbar, status_badge


def render_transactions_dashboard():
    page_header(
        "Transactions",
        "Local transaction ledger and holdings rollup derived from imported asset data.",
        badge="Ledger",
        action_html=status_badge("WealthOS", "success"),
    )

    ledger = get_transaction_ledger()
    ledger_df = pd.DataFrame(ledger)
    ledger_df = filter_by_query(
        ledger_df,
        ["instrument_name", "account_name", "asset_class", "type", "notes"],
        str(st.session_state.get("global_search", "")).strip(),
    )
    saved_view = st.session_state.get("saved_view", "All values")
    if saved_view == "Monthly contributions":
        ledger_df = ledger_df[ledger_df["type"].str.lower().str.contains("buy|investment|contribution", na=False)] if "type" in ledger_df.columns else ledger_df

    if ledger_df.empty:
        st.info("No transactions exist yet. Import a sample or custom Excel file to populate the ledger.")
        return

    if "date" in ledger_df.columns:
        ledger_df["date"] = pd.to_datetime(ledger_df["date"], errors="coerce")

    total_transactions = len(ledger_df)
    section_toolbar("Transaction overview", right_html=status_badge("Operating ledger", "warning"))
    metric_cards = st.columns(2)
    with metric_cards[0]:
        metric_card("Transactions", str(total_transactions), caption="Rows in the local ledger")
    with metric_cards[1]:
        metric_card("Holdings", str(len(pd.DataFrame(get_holdings_summary()))), caption="Current active holdings")

    panel("Ledger", "Detailed record of account activity and source origin")
    st.dataframe(
        ledger_df[["date", "account_name", "instrument_name", "asset_class", "type", "amount", "notes", "source"]],
        use_container_width=True,
        hide_index=True,
    )

    panel("Holdings rollup", "Performance and position summary derived from the ledger")
    holdings = pd.DataFrame(get_holdings_summary())
    if holdings.empty:
        st.info("No holdings available yet.")
        return
    st.dataframe(
        holdings[["instrument_name", "asset_class", "account_name", "units", "avg_cost", "current_value"]],
        use_container_width=True,
        hide_index=True,
    )
