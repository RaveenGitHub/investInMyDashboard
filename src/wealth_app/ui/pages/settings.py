from __future__ import annotations

import pandas as pd
import streamlit as st

from app_config import SAMPLE_ASSET_PATH, SAMPLE_GOALS_PATH, CURRENCY_META
from database import clear_settings, list_recent_imports, set_setting, validate_required_columns
from wealth_app.repositories.settings_repository import SettingsRepository
from wealth_app.ui.components.cards import empty_state, metric_group, page_header, panel, section_toolbar, status_badge


def render_settings_page():
    page_header(
        "Settings",
        "Application defaults, saved preferences, and local data health.",
        badge="Config",
        action_html=status_badge("WealthOS", "success"),
    )

    settings_repo = SettingsRepository()
    default_currency = settings_repo.get_default_currency()
    default_compact = settings_repo.get_compact_numbers_default()

    section_toolbar("General preferences", right_html=status_badge("Saved defaults", "warning"))
    currency_choice = st.selectbox(
        "Default currency",
        list(CURRENCY_META.keys()),
        index=list(CURRENCY_META.keys()).index(default_currency),
        help="Saved to the local SQLite settings store.",
    )
    compact_choice = st.checkbox("Compact numbers by default", value=default_compact)
    metric_group([
        ("Default currency", currency_choice, "System-wide default", None, True),
        ("Compact mode", "On" if compact_choice else "Off", "Display preference", None, True),
    ])

    if st.button("Save preferences"):
        set_setting("default_currency", currency_choice)
        set_setting("compact_numbers", str(compact_choice).lower())
        st.success("Preferences saved to the local database.")

    section_toolbar("Local database", right_html=status_badge("SQLite", "success"))
    db_path = str(SAMPLE_ASSET_PATH.parent.parent / "wealth_app.db")
    st.code(db_path)
    st.caption("The app stores settings in SQLite to support a more durable local-first workflow.")

    section_toolbar("Sample data validation", right_html=status_badge("Integrity checks", "success"))
    sample_checks = []
    for excel_file, required_columns in [
        (SAMPLE_ASSET_PATH, ["Asset Type", "Asset Catogry", "Asset Name", "Amount Invested", "Current Asset Value"]),
        (SAMPLE_GOALS_PATH, ["goal_name", "category", "target_amount", "target_date", "current_savings", "priority"]),
    ]:
        if excel_file.exists():
            df = pd.read_excel(excel_file, engine="openpyxl")
            validation = validate_required_columns(list(df.columns), required_columns)
            status = "OK" if validation["valid"] else "Missing columns: " + ", ".join(validation["missing"])
            sample_checks.append((excel_file.name, status))
        else:
            sample_checks.append((excel_file.name, "Not found"))

    for file_name, status in sample_checks:
        if status.startswith("OK"):
            st.success(f"{file_name}: {status}")
        else:
            st.warning(f"{file_name}: {status}")

    section_toolbar("Recent imports", right_html=status_badge("Activity", "warning"))
    recent_imports = list_recent_imports(limit=5)
    if recent_imports:
        st.dataframe(pd.DataFrame(recent_imports), use_container_width=True, hide_index=True)
    else:
        empty_state("No imports logged yet", "Add sample or custom files to populate your local data history.", tone="warning")

    if st.button("Reset local settings"):
        clear_settings()
        st.success("Local settings were reset. Defaults will be restored on the next refresh.")
