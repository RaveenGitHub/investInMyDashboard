from __future__ import annotations

import streamlit as st


def status_badge(label: str, tone: str = "success") -> str:
    return str(label)


def metric_card(label: str, value: str, delta: str | None = None, delta_positive: bool = True, caption: str | None = None) -> None:
    delta_value = None
    if delta:
        delta_value = delta if delta_positive else f"▼ {delta}"
        if delta_positive and not delta.startswith("+"):
            delta_value = f"+{delta}"
    st.metric(label=label, value=value, delta=delta_value, help=caption)


def panel(title: str, subtitle: str | None = None, accent: str = "gold") -> object:
    container = st.container()
    with container:
        st.markdown(f"### {title}")
        if subtitle:
            st.caption(subtitle)
    return container


def page_header(title: str, subtitle: str | None = None, badge: str | None = None, action_html: str | None = None) -> None:
    left, right = st.columns([4, 1])
    with left:
        st.markdown(f"## {title}")
        if subtitle:
            st.caption(subtitle)
    with right:
        if badge:
            st.markdown(f"**{badge}**")
        if action_html:
            st.markdown(f"{action_html}")


def section_toolbar(label: str, right_html: str | None = None) -> None:
    left, right = st.columns([3, 1])
    with left:
        st.markdown(f"**{label}**")
    with right:
        if right_html:
            st.markdown(f"{right_html}")


def metric_group(metrics: list[tuple]) -> None:
    if not metrics:
        return
    columns = st.columns(len(metrics))
    for col, metric in zip(columns, metrics):
        label = metric[0]
        value = metric[1]
        caption = metric[2] if len(metric) > 2 else None
        delta = metric[3] if len(metric) > 3 else None
        positive = metric[4] if len(metric) > 4 else True
        with col:
            metric_card(label, value, delta=delta, delta_positive=positive, caption=caption)


def empty_state(title: str, message: str, tone: str = "warning") -> None:
    if tone == "success":
        st.success(f"{title}: {message}")
    else:
        st.warning(f"{title}: {message}")


def goal_progress_card(goal_name: str, progress_pct: float, current_savings: float, target_amount: float, status: str) -> None:
    safe_pct = min(max(float(progress_pct), 0.0), 100.0)
    with st.container():
        st.caption("Goal")
        st.markdown(f"### {goal_name}")
        st.progress(min(max(safe_pct / 100, 0.0), 1.0))
        st.caption(f"{safe_pct:.1f}% complete • {current_savings:,.0f} / {target_amount:,.0f}")
        st.caption(status)
