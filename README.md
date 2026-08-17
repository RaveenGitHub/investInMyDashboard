# ProsperaX

[![Python tests](https://github.com/RaveenGitHub/investInMyDashboard/actions/workflows/python-tests.yml/badge.svg)](https://github.com/RaveenGitHub/investInMyDashboard/actions/workflows/python-tests.yml)

ProsperaX is a local-first personal wealth dashboard built with Streamlit, pandas, and Plotly. It helps you monitor your portfolio, track goals, analyze quality and risk, review recurring investments, and keep a local SQLite-backed view of your financial data.

## Overview

This app is designed for desktop use and runs locally on your machine without requiring a cloud deployment. It includes:

- Dashboard overview with portfolio health and goal risk alerts
- Portfolio and investment analysis
- Transaction and recurring investment tracking
- Investment quality and decision guidance
- Goals progress monitoring
- Settings and local data management

## Features

### Portfolio & Investments
- Portfolio value, invested capital, and return tracking
- Asset allocation views
- Date and risk filtering
- Top holdings and allocations
- Exportable filtered investment data

### Investment Quality & Decisions
- Quality scoring and risk assessment
- Decision-oriented recommendations
- Allocation and return insight summaries

### Goals & Progress
- Goal progress tracking against targets
- Current savings vs target value
- Goal priority and health indicators
- Progress and gap alerts

### Local-first architecture
- SQLite-powered local settings and data persistence
- Sample workbook fallback for quick demos
- Optional custom CSV/XLSX uploads

## Tech stack

- Python 3.10+
- Streamlit
- pandas
- Plotly
- openpyxl / xlrd
- SQLite

## Quick start

### 1) Clone the project

```bash
git clone https://github.com/RaveenGitHub/investInMyDashboard.git
cd investInMyDashboard
```

### 2) Create and activate a virtual environment

On macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Run the app

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

## App structure

```text
.
├── app.py
├── app_config.py
├── data_layer.py
├── database.py
├── requirements.txt
├── data/
│   ├── investments.csv
│   └── goals.csv
├── sample/
│   ├── Asset.xlsx
│   └── Goals.xlsx
├── src/
│   └── wealth_app/
│       ├── config/
│       ├── domain/
│       ├── repositories/
│       ├── services/
│       ├── ui/
│       └── utils/
├── tests/
├── docs/
└── README.md
```

## Sample data

The app ships with bundled sample files so it can run immediately without custom uploads:

- `data/investments.csv`
- `data/goals.csv`
- `sample/Asset.xlsx`
- `sample/Goals.xlsx`

You can also upload your own Excel or CSV files from the sidebar.

## Navigation pages

The app includes the following pages:

1. Dashboard
2. Portfolio & Investments
3. Transactions
4. Daily & Monthly Investments
5. Investment Quality & Decisions
6. Insights
7. Goals & Progress
8. Settings

## Local storage

The app stores local preferences and settings in a SQLite database (`wealth_app.db`) so the experience stays local and lightweight.

## Typical user workflow

1. Launch the app.
2. Review the dashboard summary.
3. Filter or inspect portfolio data.
4. Check investment quality and alert insights.
5. Track progress against active goals.
6. Adjust the local sample data or upload your own workbook.

## Troubleshooting

### Streamlit port already in use

If port 8501 is already busy, stop the previous Streamlit process or run the app on another port:

```bash
streamlit run app.py --server.port 8502
```

### Missing dependencies

Reinstall dependencies:

```bash
pip install -r requirements.txt
```

### Data not loading

Use the bundled sample workbook or upload a file with the expected columns. The app includes validation and fallback handling for common file variations.

## Documentation

For onboarding and user setup guidance, see:

- [docs/ONBOARDING_GUIDE.md](docs/ONBOARDING_GUIDE.md)

## Quality gates and coverage

Run the test suite locally with coverage:

```bash
python -m pip install -r requirements.txt
python -m pytest tests -q --cov=. --cov-report=term-missing --cov-report=xml
```

This project keeps a lightweight quality gate to validate financial calculations, validation helpers, and defensive defaults before release.

## License

This project is intended for local desktop use and personal wealth tracking. Modify and extend it as needed for your workflow.
