from __future__ import annotations

import streamlit as st

from wealth_app.ui.theme.tokens import COLORS, FONT_STACK, RADIUS, SHADOWS, SPACING


def apply_brand_theme() -> None:
    st.markdown(
        f"""
        <style>
        :root {{
            --rj-black: {COLORS['black']};
            --rj-charcoal: {COLORS['charcoal']};
            --rj-charcoal-soft: {COLORS['charcoal_soft']};
            --rj-gold: {COLORS['gold']};
            --rj-gold-soft: {COLORS['gold_soft']};
            --rj-gold-deep: {COLORS['gold_deep']};
            --rj-text-primary: {COLORS['text_primary']};
            --rj-text-muted: {COLORS['text_muted']};
            --rj-surface: {COLORS['surface']};
            --rj-surface-alt: {COLORS['surface_alt']};
            --rj-border: {COLORS['border']};
            --rj-success: {COLORS['success']};
            --rj-warning: {COLORS['warning']};
            --rj-danger: {COLORS['danger']};
            --rj-shadow-soft: {SHADOWS['soft']};
            --rj-shadow-gold: {SHADOWS['gold']};
            --rj-radius-md: {RADIUS['md']};
            --rj-radius-lg: {RADIUS['lg']};
            --rj-gap-sm: {SPACING['sm']};
            --rj-gap-md: {SPACING['md']};
            --rj-gap-lg: {SPACING['lg']};
        }}

        html, body, [data-testid="stAppViewContainer"], .stApp {{
            background: linear-gradient(180deg, var(--rj-black) 0%, var(--rj-charcoal-soft) 100%);
            color: var(--rj-text-primary);
            font-family: {FONT_STACK};
        }}

        .stApp {{
            background-image: radial-gradient(circle at top left, rgba(255, 215, 0, 0.12), transparent 20%),
                radial-gradient(circle at top right, rgba(255, 215, 0, 0.08), transparent 18%);
        }}

        .stSidebar {{
            background: rgba(12, 12, 12, 0.96);
            border-right: 1px solid var(--rj-border);
        }}

        .stSidebar .block-container {{
            padding-top: 1.2rem;
            padding-bottom: 1.5rem;
        }}

        .stSidebar .stRadio > div[role="radiogroup"] {{
            display: flex;
            flex-direction: column;
            gap: 0.35rem;
            margin-top: 0.5rem;
        }}

        .stSidebar .stRadio label {{
            min-height: 42px;
            border-radius: 10px;
            padding: 0.55rem 0.7rem;
            border: 1px solid transparent;
            background: rgba(255,255,255,0.01);
            transition: all 180ms ease;
            margin: 0;
        }}

        .stSidebar .stRadio label:hover {{
            border-color: rgba(255, 215, 0, 0.18);
            background: rgba(255, 215, 0, 0.04);
        }}

        .stSidebar .stRadio label[aria-checked="true"] {{
            background: linear-gradient(180deg, rgba(255, 215, 0, 0.12), rgba(255, 215, 0, 0.04));
            border: 1px solid rgba(255, 215, 0, 0.28);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
        }}

        .stSidebar .stRadio [data-baseweb="radio"] > div[role="radio"] {{
            display: flex;
            align-items: center;
            min-height: 42px;
        }}

        .stSidebar .stCheckbox {{
            min-height: 42px;
            display: flex;
            align-items: center;
        }}

        .stSidebar .stCheckbox > label {{
            width: 100%;
            min-height: 42px;
            padding: 0.2rem 0.1rem;
        }}

        .stSidebar .stCheckbox label:hover {{
            color: var(--rj-text-primary);
        }}

        .block-container {{
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1600px;
            padding-left: 1.15rem;
            padding-right: 1.15rem;
        }}

        .main .block-container {{
            margin-left: 0.2rem;
            margin-right: 0.2rem;
            position: relative;
            overflow: hidden;
        }}

        .prospera-watermark {{
            position: absolute;
            top: 0.9rem;
            left: 1.1rem;
            font-size: clamp(2.6rem, 4vw, 5.2rem);
            font-weight: 800;
            line-height: 1;
            letter-spacing: -0.08em;
            color: rgba(255, 215, 0, 0.08);
            pointer-events: none;
            user-select: none;
            white-space: nowrap;
            z-index: 0;
        }}

        .main .block-container > * {{
            position: relative;
            z-index: 1;
        }}

        .element-container {{
            margin-bottom: 0.55rem;
        }}

        h1, h2, h3, h4, p, label, .stMultiSelect, .stSelectbox, .stTextInput, .stCheckbox, .stNumberInput, .stDateInput {{
            color: var(--rj-text-primary) !important;
        }}

        h1 {{
            font-size: clamp(2rem, 2.6vw, 3rem) !important;
            font-weight: 800 !important;
            letter-spacing: -0.04em;
            margin-bottom: 0.2rem !important;
        }}

        h2 {{
            font-size: clamp(1.35rem, 1.8vw, 2rem) !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
        }}

        h3 {{
            font-size: 1.12rem !important;
            font-weight: 700 !important;
        }}

        .stMetric {{
            background: linear-gradient(180deg, rgba(26,26,26,0.98), rgba(18,18,18,0.96));
            border: 1px solid var(--rj-border);
            border-radius: var(--rj-radius-lg);
            box-shadow: var(--rj-shadow-soft);
            padding: 1.15rem 1rem;
            min-height: 150px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        .stMetric [data-testid="stMetricLabel"] {{
            color: var(--rj-text-muted) !important;
            font-size: 0.72rem !important;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 700;
        }}

        .stMetric [data-testid="stMetricValue"] {{
            color: var(--rj-text-primary) !important;
            font-weight: 700 !important;
            font-size: clamp(1.3rem, 2vw, 2.2rem) !important;
        }}

        .stButton > button,
        .stDownloadButton > button,
        .stFormSubmitButton > button,
        button[kind="primary"],
        button[kind="secondary"] {{
            width: 100%;
            min-height: 46px;
            border-radius: 12px;
            border: 1px solid rgba(255, 215, 0, 0.52);
            font-weight: 700;
            transition: all 180ms ease;
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
            padding: 0.72rem 0.9rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            cursor: pointer;
            box-sizing: border-box;
        }}

        .stButton > button,
        .stFormSubmitButton > button {{
            background: linear-gradient(180deg, rgba(255, 215, 0, 0.12), rgba(212, 161, 0, 0.2));
            color: var(--rj-text-primary);
        }}

        .stDownloadButton > button {{
            background: linear-gradient(180deg, rgba(255, 215, 0, 0.28), rgba(212, 161, 0, 0.35));
            color: #0A0A0A;
        }}

        .stButton > button:hover,
        .stDownloadButton > button:hover,
        .stFormSubmitButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: var(--rj-shadow-gold);
        }}

        .stTextInput > div > div,
        .stNumberInput > div > div,
        .stDateInput > div > div,
        .stTextArea > div > div,
        .stSelectbox > div[data-baseweb="select"] > div,
        .stMultiSelect > div[data-baseweb="select"] > div,
        .stFileUploader > div[data-testid="stFileUploaderDropzone"] {{
            min-height: 46px;
            border-radius: 12px;
            border: 1px solid rgba(255, 215, 0, 0.22);
            background: rgba(20, 20, 20, 0.96);
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
            box-sizing: border-box;
        }}

        .stTextInput input,
        .stNumberInput input,
        .stDateInput input,
        .stTextArea textarea,
        .stSelectbox div[role="button"],
        .stMultiSelect div[role="button"] {{
            min-height: 46px;
            border-radius: 12px;
            background: rgba(20, 20, 20, 0.96);
            color: var(--rj-text-primary);
            border: none;
            padding: 0.8rem 0.9rem;
            box-sizing: border-box;
        }}

        .stSidebar .stTextInput > div > div,
        .stSidebar .stNumberInput > div > div,
        .stSidebar .stDateInput > div > div,
        .stSidebar .stTextArea > div > div,
        .stSidebar .stSelectbox > div[data-baseweb="select"] > div,
        .stSidebar .stMultiSelect > div[data-baseweb="select"] > div,
        .stSidebar .stFileUploader > div[data-testid="stFileUploaderDropzone"] {{
            min-height: 44px;
        }}

        .stSidebar .stSelectbox label,
        .stSidebar .stTextInput label,
        .stSidebar .stNumberInput label,
        .stSidebar .stDateInput label,
        .stSidebar .stCheckbox label,
        .stSidebar .stRadio label {{
            font-weight: 600;
            color: var(--rj-text-primary);
        }}

        .stSidebar .stButton > button,
        .stSidebar .stDownloadButton > button,
        .stSidebar .stFormSubmitButton > button {{
            width: 100%;
            min-height: 42px;
            margin-top: 0.2rem;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
        }}

        .stSidebar .stButton > button > div,
        .stSidebar .stDownloadButton > button > div,
        .stSidebar .stFormSubmitButton > button > div {{
            width: 100%;
        }}

        .stDataFrame, .stTable {{
            background: rgba(17, 17, 17, 0.9);
            border: 1px solid var(--rj-border);
            border-radius: var(--rj-radius-md);
            overflow: hidden;
        }}

        .stPlotlyChart, .element-container .stPlotlyChart {{
            background: rgba(17, 17, 17, 0.8);
            border: 1px solid var(--rj-border);
            border-radius: var(--rj-radius-lg);
        }}

        .stSuccess {{
            background: rgba(139, 195, 74, 0.12);
            border: 1px solid rgba(139, 195, 74, 0.28);
            color: #dff7b3 !important;
        }}

        .stWarning {{
            background: rgba(255, 200, 87, 0.1);
            border: 1px solid rgba(255, 200, 87, 0.26);
            color: #ffe9b8 !important;
        }}

        .stInfo {{
            background: rgba(255, 215, 0, 0.08);
            border: 1px solid rgba(255, 215, 0, 0.2);
            color: #f5e8a2 !important;
        }}

        .rj-card {{
            background: linear-gradient(180deg, rgba(26,26,26,0.98), rgba(17,17,17,0.96));
            border: 1px solid var(--rj-border);
            border-radius: var(--rj-radius-lg);
            box-shadow: var(--rj-shadow-soft);
            padding: 1rem 1.1rem;
            margin-bottom: 1rem;
        }}

        .rj-card--metric {{
            padding: 1.1rem 1rem;
        }}

        .rj-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.55rem;
        }}

        .rj-label {{
            font-size: 0.7rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            font-weight: 700;
            color: var(--rj-text-muted);
        }}

        .rj-metric-value {{
            font-size: clamp(1.3rem, 2vw, 2.1rem);
            font-weight: 800;
            color: var(--rj-text-primary);
            letter-spacing: -0.03em;
        }}

        .rj-caption {{
            color: var(--rj-text-muted);
            font-size: 0.8rem;
            margin-top: 0.35rem;
        }}

        .rj-delta {{
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.2rem 0.5rem;
            font-size: 0.72rem;
            font-weight: 700;
        }}

        .rj-delta--positive {{
            background: rgba(139, 195, 74, 0.12);
            color: #dff7b3;
        }}

        .rj-delta--negative {{
            background: rgba(255, 107, 107, 0.12);
            color: #ffc2c2;
        }}

        .rj-badge {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 0.35rem 0.6rem;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            border: 1px solid var(--rj-border);
        }}

        .rj-badge--success {{
            background: rgba(139, 195, 74, 0.1);
            color: #dff7b3;
        }}

        .rj-badge--warning {{
            background: rgba(255, 200, 87, 0.1);
            color: #ffe9b8;
        }}

        .rj-badge--danger {{
            background: rgba(255, 107, 107, 0.1);
            color: #ffc2c2;
        }}

        .rj-section-header {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            gap: 0.75rem;
            margin: 1.5rem 0 0.8rem 0;
            border-bottom: 1px solid rgba(255, 215, 0, 0.16);
            padding-bottom: 0.55rem;
        }}

        .rj-section-header h3 {{
            margin: 0;
            letter-spacing: -0.02em;
        }}

        .stTabs [role="tablist"] {{
            gap: 0.5rem;
            margin-bottom: 1rem;
        }}

        .stTabs [role="tablist"] button {{
            border-radius: 10px 10px 0 0;
            border: 1px solid transparent;
            padding: 0.6rem 0.9rem;
            font-weight: 700;
        }}

        .rj-section-header h3 {{
            margin: 0;
        }}

        .rj-sidebar-section {{
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--rj-text-muted);
            margin: 1rem 0 0.5rem 0;
            padding-top: 0.6rem;
            border-top: 1px solid rgba(255, 215, 0, 0.12);
        }}

        .brand-header {{
            display: flex;
            align-items: center;
            gap: 0.9rem;
            padding: 0.5rem 0 0.85rem 0;
            border-bottom: 1px solid rgba(255, 215, 0, 0.12);
            margin-bottom: 0.75rem;
        }}

        .brand-mark {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: radial-gradient(circle at 30% 30%, #fff0ad 0%, var(--rj-gold) 25%, #b88a00 100%);
            box-shadow: 0 0 16px rgba(255, 215, 0, 0.4);
        }}

        .brand-name {{
            font-size: 1.05rem;
            font-weight: 800;
            letter-spacing: -0.04em;
            color: var(--rj-text-primary);
        }}

        .sidebar-brand-name {{
            display: flex;
            align-items: center;
            justify-content: flex-start;
            min-height: 42px;
            font-size: 1.05rem;
            font-weight: 800;
            letter-spacing: -0.04em;
            color: var(--rj-text-primary);
            margin: 0.1rem 0 0.55rem 0;
        }}

        .rj-page-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 1rem;
            margin-bottom: 1.25rem;
            padding: 1rem 0 0.75rem 0;
            border-bottom: 1px solid rgba(255, 215, 0, 0.18);
        }}

        .rj-page-header__copy {{
            flex: 1;
        }}

        .rj-page-header__title-row {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            flex-wrap: wrap;
        }}

        .rj-sector-toolbar {{
            display: none;
        }}

        .rj-header-actions {{
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 0.5rem;
            flex-wrap: wrap;
            padding-top: 0.4rem;
        }}

        .rj-section-toolbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 0.75rem;
            margin: 1.1rem 0 0.8rem 0;
        }}

        .rj-section-toolbar__label {{
            font-size: 0.82rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            font-weight: 700;
            color: var(--rj-text-muted);
        }}

        .rj-section-toolbar__actions {{
            display: flex;
            justify-content: flex-end;
            gap: 0.5rem;
            flex-wrap: wrap;
        }}

        .rj-alert {{
            display: block;
            border-radius: var(--rj-radius-md);
            padding: 0.8rem 0.9rem;
            margin: 0.5rem 0 0.8rem 0;
            border: 1px solid var(--rj-border);
            font-size: 0.9rem;
            line-height: 1.5;
        }}

        .rj-alert--success {{
            background: rgba(139, 195, 74, 0.12);
            border-color: rgba(139, 195, 74, 0.3);
            color: #dff7b3;
        }}

        .rj-alert--warning {{
            background: rgba(255, 200, 87, 0.1);
            border-color: rgba(255, 200, 87, 0.28);
            color: #ffe9b8;
        }}

        .rj-progress-label {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.6rem;
            margin-bottom: 0.4rem;
            font-size: 0.8rem;
            color: var(--rj-text-muted);
        }}

        .rj-progress-bar {{
            height: 10px;
            width: 100%;
            background: rgba(255, 255, 255, 0.07);
            border-radius: 999px;
            overflow: hidden;
            border: 1px solid rgba(255, 215, 0, 0.12);
        }}

        .rj-progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--rj-gold), #f0d15d);
            border-radius: inherit;
        }}

        .rj-row-gap {{
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
