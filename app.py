import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_ROOT = PROJECT_ROOT / "src"
BRAND_LOGO_PATH = PROJECT_ROOT / "assets" / "rtj-monogram.svg"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from app_config import SAMPLE_ASSET_PATH, SAMPLE_GOALS_PATH, CURRENCY_META, build_sample_bundle
from database import (
    add_import_log,
    ensure_holdings,
    init_db,
    seed_sample_data_if_empty,
)
from wealth_app.repositories.settings_repository import SettingsRepository
from wealth_app.ui.theme.styles import apply_brand_theme
from wealth_app.ui.pages.dashboard import render_dashboard_page
from wealth_app.ui.pages.goals import render_goals_dashboard
from wealth_app.ui.pages.insights import render_insights_dashboard
from wealth_app.ui.pages.portfolio import render_portfolio_page
from wealth_app.ui.pages.quality import render_quality_dashboard
from wealth_app.ui.pages.recurring import render_recurring_dashboard
from wealth_app.ui.pages.settings import render_settings_page
from wealth_app.ui.pages.transactions import render_transactions_dashboard


def main():
    init_db()
    seed_sample_data_if_empty(SAMPLE_ASSET_PATH, SAMPLE_GOALS_PATH)
    ensure_holdings()
    st.set_page_config(page_title="Personal Wealth & Goals Dashboard", layout="wide")
    apply_brand_theme()

    if BRAND_LOGO_PATH.exists():
        st.sidebar.image(str(BRAND_LOGO_PATH), width=70)
    st.sidebar.markdown("### WealthOS")

    pages = [
        "Dashboard",
        "Portfolio & Investments",
        "Transactions",
        "Daily & Monthly Investments",
        "Investment Quality & Decisions",
        "Insights",
        "Goals & Progress",
        "Settings",
    ]
    st.sidebar.caption("Navigation")
    app_page = st.sidebar.radio("WealthOS", pages)

    settings_repo = SettingsRepository()
    currency_key = f"currency_{app_page}"
    compact_key = f"compact_{app_page}"
    default_currency = settings_repo.get_default_currency()
    default_compact = settings_repo.get_compact_numbers_default()
    default_page_currency = st.session_state.get(currency_key, default_currency)
    default_page_compact = st.session_state.get(compact_key, default_compact)

    currency_code = st.sidebar.selectbox(
        "Currency",
        list(CURRENCY_META.keys()),
        index=list(CURRENCY_META.keys()).index(default_page_currency),
        key=currency_key,
        help="Choose the ISO currency code and symbol for this page.",
    )
    compact_mode = st.sidebar.checkbox(
        "Compact numbers",
        value=default_page_compact,
        key=compact_key,
        help="Use compact format like $1.2M instead of full values.",
    )
    settings_repo.set_page_currency(app_page, currency_code)
    settings_repo.set_page_compact(app_page, compact_mode)

    st.sidebar.caption("Data sources")

    reset_to_sample_clicked = st.sidebar.button("Reset to sample data")
    if reset_to_sample_clicked:
        st.session_state["use_sample_data"] = True
        st.session_state.pop("investment_upload", None)
        st.session_state.pop("goal_upload", None)
        st.rerun()

    reset_all_clicked = st.sidebar.button("Reset all")
    if reset_all_clicked:
        st.session_state.pop("use_sample_data", None)
        st.session_state.pop("investment_upload", None)
        st.session_state.pop("goal_upload", None)
        st.rerun()

    use_sample_data = st.sidebar.checkbox(
        "Use sample workbook",
        value=st.session_state.get("use_sample_data", True),
        key="use_sample_data",
        help="Load the bundled Excel sample file instead of a custom upload.",
    )
    st.sidebar.caption(
        "Expected asset columns: Asset Type, Asset Catogry, Asset Sub Catogry, Asset Name, Amount Invested, Inv Unit Value, Unit, Current Unit Value, Current Asset Value"
    )
    with st.sidebar:
        st.download_button(
            "Download sample asset workbook",
            data=SAMPLE_ASSET_PATH.read_bytes(),
            file_name="Asset.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    st.sidebar.caption("Expected goals columns: goal_name, category, target_amount, target_date, current_savings, priority")
    with st.sidebar:
        st.download_button(
            "Download sample goals workbook",
            data=SAMPLE_GOALS_PATH.read_bytes(),
            file_name="Goals.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    with st.sidebar:
        st.download_button(
            "Download all sample files",
            data=build_sample_bundle(),
            file_name="sample_data_bundle.zip",
            mime="application/zip",
            help="Download both sample Excel files in one bundle.",
        )

    investment_upload = None
    goal_upload = None
    if not use_sample_data:
        investment_upload = st.sidebar.file_uploader(
            "Upload investments file",
            key="investment_upload",
            type=["csv", "xlsx", "xls"],
            help="Replace the sample investments file with your own portfolio CSV or Excel workbook.",
        )
        goal_upload = st.sidebar.file_uploader(
            "Upload goals file",
            key="goal_upload",
            type=["csv", "xlsx", "xls"],
            help="Replace the sample goals file with your own savings goals CSV or Excel workbook.",
        )
        if investment_upload is not None:
            add_import_log(investment_upload.name, "uploaded", "Custom investments upload")
        if goal_upload is not None:
            add_import_log(goal_upload.name, "uploaded", "Custom goals upload")

    refresh_clicked = st.sidebar.button("Refresh uploaded data")
    if refresh_clicked:
        st.rerun()

    if app_page == pages[0]:
        render_dashboard_page()
    elif app_page == pages[1]:
        render_portfolio_page(investment_upload)
    elif app_page == pages[2]:
        render_transactions_dashboard()
    elif app_page == pages[3]:
        render_recurring_dashboard()
    elif app_page == pages[4]:
        render_quality_dashboard(investment_upload)
    elif app_page == pages[5]:
        render_insights_dashboard()
    elif app_page == pages[6]:
        render_goals_dashboard(goal_upload)
    else:
        render_settings_page()


if __name__ == "__main__":
    main()
