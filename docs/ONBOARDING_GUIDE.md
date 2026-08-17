# WealthOS Onboarding Guide

This guide helps new users get started quickly with WealthOS and understand the basic flow of the app.

## Who this is for

This app is designed for:

- Individuals tracking personal investments
- Users planning savings goals
- People wanting a local-first wealth dashboard without a cloud account
- Developers who want to extend a Streamlit-based finance dashboard

## What the app does

WealthOS combines:

- Portfolio monitoring
- Investment quality review
- Goal tracking and progress alerts
- Recurring contribution planning
- Local settings persistence

## First-time setup

### 1. Install Python

Make sure Python 3.10 or later is installed.

Check:

```bash
python --version
```

### 2. Open the project folder

Use the project root in VS Code or your terminal.

### 3. Create a virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install requirements

```bash
pip install -r requirements.txt
```

### 5. Run the app

```bash
streamlit run app.py
```

Open the browser link displayed by Streamlit.

## Main workflows

### Dashboard page

Use the dashboard to view:

- Total portfolio value
- Invested capital
- Current return
- Goal progress
- Portfolio health and alerts

### Portfolio & Investments page

This page is where you review:

- Investment allocation by asset class
- Date-filtered holdings
- Risk level filters
- Instrument details and current values

### Investment Quality & Decisions page

Use this screen to understand whether an asset is:

- performing well
- under pressure
- overweight relative to your target mix

### Goals & Progress page

Track progress toward individual goals such as:

- Retirement
- Education
- Community projects
- Emergency reserves

Each goal shows its current funding level, target value, and progress status.

### Recurring Investments page

This page helps you track:

- monthly contribution plans
- weekly or daily contribution models
- future forecast contribution patterns

### Settings page

Use settings to:

- manage local preferences
- review app configuration
- inspect data validation results
- view recent imports

## Sample data

The app loads sample data by default so you can explore the dashboard immediately.

If you want to test with your own workbook:

- upload a CSV or Excel file from the sidebar
- choose your sample or custom data source
- refresh the data if needed

## Data expectations

For portfolio data, the app can handle a range of column naming differences and typical workbook structures. The app is designed to adapt to real-world local files.

Typical investment fields include:

- date
- asset_class
- instrument_name
- amount_invested
- current_value
- returns_pct
- risk_level

Typical goal fields include:

- goal_name
- category
- target_amount
- target_date
- current_savings
- priority

## Best practices

- Keep your local files organized and named consistently.
- Validate portfolio data before relying on quality decisions.
- Use the dashboard to monitor trends over time, not only one-off values.
- Revisit goal targets and contribution assumptions regularly.

## Troubleshooting

### The app does not open

Check whether Python and dependencies were installed correctly.

```bash
pip install -r requirements.txt
```

### Port 8501 is already in use

Use a different port:

```bash
streamlit run app.py --server.port 8502
```

### Data looks incomplete

Try resetting to the sample dataset or re-uploading the workbook.

## Support and extension

This project is intentionally local-first and easy to extend. You can build on it by:

- adding more portfolio analytics
- adding export features
- introducing user authentication
- moving from local files to a hosted database

## Summary

WealthOS is designed to make personal financial monitoring simple, local, and visual. With minimal setup, you can begin tracking your investment health and progress toward your goals in a single desktop app.
