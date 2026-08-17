import sqlite3
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
DB_PATH = PROJECT_DIR / "wealth_app.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT,
            currency TEXT DEFAULT 'USD',
            institution TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS instruments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            asset_class TEXT,
            asset_category TEXT,
            asset_subcategory TEXT,
            risk_level TEXT,
            currency TEXT DEFAULT 'USD',
            UNIQUE(name, asset_class)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER,
            instrument_id INTEGER,
            date TEXT NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            units REAL,
            unit_price REAL,
            fees REAL DEFAULT 0,
            notes TEXT,
            source TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(account_id) REFERENCES accounts(id),
            FOREIGN KEY(instrument_id) REFERENCES instruments(id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS recurring_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instrument_id INTEGER,
            account_id INTEGER,
            frequency TEXT NOT NULL,
            amount REAL NOT NULL,
            next_due_date TEXT,
            status TEXT DEFAULT 'active',
            template_name TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(instrument_id) REFERENCES instruments(id),
            FOREIGN KEY(account_id) REFERENCES accounts(id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS holdings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instrument_id INTEGER,
            account_id INTEGER,
            units REAL,
            avg_cost REAL,
            current_value REAL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(instrument_id, account_id),
            FOREIGN KEY(instrument_id) REFERENCES instruments(id),
            FOREIGN KEY(account_id) REFERENCES accounts(id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            target_amount REAL,
            target_date TEXT,
            priority TEXT,
            status TEXT DEFAULT 'active'
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS goal_contributions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_id INTEGER,
            date TEXT,
            amount REAL,
            source_account TEXT,
            FOREIGN KEY(goal_id) REFERENCES goals(id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS import_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            imported_at TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT,
            messages TEXT
        )
        """
    )

    default_settings = {
        "default_currency": "USD",
        "compact_numbers": "false",
        "theme": "dark",
        "sample_source": "Asset.xlsx",
    }
    for key, value in default_settings.items():
        conn.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            (key, value),
        )

    conn.commit()
    conn.close()


def set_setting(key, value):
    conn = get_connection()
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, str(value)),
    )
    conn.commit()
    conn.close()


def get_setting(key, default=None):
    conn = get_connection()
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    if row is None:
        return default
    return row["value"]


def clear_settings():
    conn = get_connection()
    conn.execute("DELETE FROM settings")
    conn.commit()
    conn.close()
    init_db()


def count_rows(table_name):
    conn = get_connection()
    row = conn.execute(f"SELECT COUNT(*) AS total FROM {table_name}").fetchone()
    conn.close()
    return int(row["total"]) if row else 0


def add_import_log(file_name, status, messages):
    conn = get_connection()
    conn.execute(
        "INSERT INTO import_logs (file_name, status, messages) VALUES (?, ?, ?)",
        (file_name, status, messages),
    )
    conn.commit()
    conn.close()


def list_recent_imports(limit=5):
    conn = get_connection()
    rows = conn.execute(
        "SELECT file_name, imported_at, status, messages FROM import_logs ORDER BY imported_at DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def upsert_account(conn, name, account_type="portfolio", currency="USD", institution=None):
    row = conn.execute(
        "SELECT id FROM accounts WHERE name = ?",
        (name,),
    ).fetchone()
    if row:
        return row["id"]
    cursor = conn.execute(
        "INSERT INTO accounts (name, type, currency, institution) VALUES (?, ?, ?, ?)",
        (name, account_type, currency, institution),
    )
    return cursor.lastrowid


def upsert_instrument(conn, name, asset_class, asset_category=None, asset_subcategory=None, risk_level="Medium", currency="USD"):
    row = conn.execute(
        "SELECT id FROM instruments WHERE name = ? AND asset_class = ?",
        (name, asset_class),
    ).fetchone()
    if row:
        return row["id"]
    cursor = conn.execute(
        "INSERT INTO instruments (name, asset_class, asset_category, asset_subcategory, risk_level, currency) VALUES (?, ?, ?, ?, ?, ?)",
        (name, asset_class, asset_category, asset_subcategory, risk_level, currency),
    )
    return cursor.lastrowid


def store_investment_rows(df, source_name="sample"):
    if df is None or df.empty:
        return 0

    conn = get_connection()
    account_id = upsert_account(conn, "Primary Portfolio", "portfolio", "USD", "Local")
    inserted = 0

    for _, row in df.iterrows():
        asset_class = str(row.get("asset_class") or row.get("Asset Type") or "Uncategorized").strip() or "Uncategorized"
        instrument_name = str(row.get("instrument_name") or row.get("Asset Name") or "Unknown Instrument").strip() or "Unknown Instrument"
        asset_category = str(row.get("asset_category") or row.get("Asset Catogry") or row.get("Asset Category") or "").strip()
        risk_level = str(row.get("risk_level") or "Medium").strip() or "Medium"
        amount_invested = float(row.get("amount_invested") or row.get("Amount Invested") or 0)
        current_value = float(row.get("current_value") or row.get("Current Asset Value") or 0)
        date_value = row.get("date")
        if date_value is None or str(date_value).strip() == "":
            date_value = "2026-01-01"

        instrument_id = upsert_instrument(
            conn,
            instrument_name,
            asset_class,
            asset_category if asset_category else None,
            None,
            risk_level,
            "USD",
        )
        conn.execute(
            "INSERT INTO transactions (account_id, instrument_id, date, type, amount, units, unit_price, fees, notes, source) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                account_id,
                instrument_id,
                str(date_value)[:10],
                "buy",
                float(amount_invested),
                float(max(current_value, amount_invested)) if current_value else float(amount_invested),
                None,
                0,
                f"Imported from {source_name}",
                source_name,
            ),
        )
        inserted += 1

    conn.commit()
    conn.close()
    rebuild_holdings()
    return inserted


def store_goal_rows(df, source_name="sample"):
    if df is None or df.empty:
        return 0

    conn = get_connection()
    inserted = 0
    for _, row in df.iterrows():
        goal_name = str(row.get("goal_name") or "Goal").strip() or "Goal"
        category = str(row.get("category") or "General").strip() or "General"
        target_amount = float(row.get("target_amount") or 0)
        target_date = row.get("target_date")
        priority = str(row.get("priority") or "Medium").strip() or "Medium"
        current_savings = float(row.get("current_savings") or 0)
        conn.execute(
            "INSERT INTO goals (name, category, target_amount, target_date, priority, status) VALUES (?, ?, ?, ?, ?, ?)",
            (goal_name, category, target_amount, str(target_date)[:10], priority, "active"),
        )
        inserted += 1
        goal_id = conn.execute("SELECT id FROM goals WHERE name = ? ORDER BY id DESC LIMIT 1", (goal_name,)).fetchone()["id"]
        if current_savings > 0:
            conn.execute(
                "INSERT INTO goal_contributions (goal_id, date, amount, source_account) VALUES (?, ?, ?, ?)",
                (goal_id, str(target_date)[:10], current_savings, "Primary Portfolio"),
            )
    conn.commit()
    conn.close()
    return inserted


def rebuild_holdings():
    conn = get_connection()
    conn.execute("DELETE FROM holdings")
    rows = conn.execute(
        """
        SELECT
            instrument_id,
            account_id,
            SUM(CASE WHEN type IN ('buy', 'investment', 'deposit', 'contribution') THEN amount ELSE 0 END) AS total_invested,
            SUM(CASE WHEN type IN ('sell', 'withdrawal', 'divest') THEN amount ELSE 0 END) AS total_sold
        FROM transactions
        GROUP BY instrument_id, account_id
        """
    ).fetchall()

    for row in rows:
        total_invested = float(row["total_invested"] or 0)
        total_sold = float(row["total_sold"] or 0)
        position_value = max(total_invested - total_sold, 0.0)
        conn.execute(
            "INSERT INTO holdings (instrument_id, account_id, units, avg_cost, current_value, updated_at) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
            (row["instrument_id"], row["account_id"], position_value, max(position_value, 0.0), position_value),
        )

    conn.commit()
    conn.close()
    return count_rows("holdings")


def ensure_holdings():
    if count_rows("transactions") > 0 and count_rows("holdings") == 0:
        return rebuild_holdings()
    return count_rows("holdings")


def get_transaction_ledger():
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT
            t.id,
            a.name AS account_name,
            i.name AS instrument_name,
            i.asset_class,
            i.risk_level,
            t.date,
            t.type,
            t.amount,
            t.units,
            t.unit_price,
            t.fees,
            t.notes,
            t.source
        FROM transactions t
        LEFT JOIN accounts a ON a.id = t.account_id
        LEFT JOIN instruments i ON i.id = t.instrument_id
        ORDER BY t.date DESC, t.id DESC
        """
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_holdings_summary():
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT
            h.id,
            i.name AS instrument_name,
            i.asset_class,
            i.risk_level,
            a.name AS account_name,
            h.units,
            h.avg_cost,
            h.current_value,
            h.updated_at
        FROM holdings h
        LEFT JOIN instruments i ON i.id = h.instrument_id
        LEFT JOIN accounts a ON a.id = h.account_id
        ORDER BY h.current_value DESC
        """
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def insert_recurring_transaction(template_name, instrument_name, amount, frequency, next_due_date, account_name="Primary Portfolio", status="active"):
    conn = get_connection()
    account_id = upsert_account(conn, account_name, "portfolio", "USD", "Local")
    instrument_id = upsert_instrument(
        conn,
        instrument_name,
        "Recurring Investment",
        "Recurring",
        None,
        "Medium",
        "USD",
    )
    cursor = conn.execute(
        "INSERT INTO recurring_transactions (instrument_id, account_id, frequency, amount, next_due_date, status, template_name) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (instrument_id, account_id, str(frequency).lower(), float(amount), str(next_due_date), status, template_name),
    )
    conn.commit()
    conn.close()
    return cursor.lastrowid


def get_recurring_transactions():
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT
            rt.id,
            rt.template_name,
            i.name AS instrument_name,
            i.asset_class,
            a.name AS account_name,
            rt.frequency,
            rt.amount,
            rt.next_due_date,
            rt.status
        FROM recurring_transactions rt
        LEFT JOIN instruments i ON i.id = rt.instrument_id
        LEFT JOIN accounts a ON a.id = rt.account_id
        ORDER BY rt.next_due_date ASC
        """
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def insert_goal_record(goal_name, category, target_amount, target_date, priority="Medium", status="active"):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO goals (name, category, target_amount, target_date, priority, status) VALUES (?, ?, ?, ?, ?, ?)",
        (goal_name, category, float(target_amount), str(target_date), priority, status),
    )
    conn.commit()
    conn.close()
    return cursor.lastrowid


def add_goal_contribution(goal_name, amount, contribution_date=None, source_account="Primary Portfolio"):
    conn = get_connection()
    goal_row = conn.execute("SELECT id FROM goals WHERE name = ? ORDER BY id DESC LIMIT 1", (goal_name,)).fetchone()
    if goal_row is None:
        conn.close()
        return None
    target_date = contribution_date or "2026-01-01"
    cursor = conn.execute(
        "INSERT INTO goal_contributions (goal_id, date, amount, source_account) VALUES (?, ?, ?, ?)",
        (goal_row["id"], str(target_date), float(amount), source_account),
    )
    conn.commit()
    conn.close()
    return cursor.lastrowid


def get_goals_summary():
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT
            g.id,
            g.name AS goal_name,
            g.category,
            g.target_amount,
            g.target_date,
            g.priority,
            g.status,
            COALESCE(SUM(gc.amount), 0) AS current_savings,
            COALESCE((SUM(gc.amount) / NULLIF(g.target_amount, 0)) * 100, 0) AS progress_pct,
            COALESCE(g.target_amount - SUM(gc.amount), g.target_amount) AS remaining_amount
        FROM goals g
        LEFT JOIN goal_contributions gc ON gc.goal_id = g.id
        GROUP BY g.id, g.name, g.category, g.target_amount, g.target_date, g.priority, g.status
        ORDER BY g.target_date ASC
        """
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def seed_sample_data_if_empty(asset_path, goals_path):
    if count_rows("transactions") > 0 or count_rows("goals") > 0:
        ensure_holdings()
        return {"transactions": count_rows("transactions"), "goals": count_rows("goals")}

    asset_df = None
    goals_df = None
    if asset_path and asset_path.exists():
        asset_df = pd.read_excel(asset_path, engine="openpyxl")
    if goals_path and goals_path.exists():
        goals_df = pd.read_excel(goals_path, engine="openpyxl")

    tx_count = store_investment_rows(asset_df, source_name=asset_path.name if asset_path else "sample") if asset_df is not None else 0
    goal_count = store_goal_rows(goals_df, source_name=goals_path.name if goals_path else "sample") if goals_df is not None else 0
    rebuild_holdings()
    return {"transactions": tx_count, "goals": goal_count}


def validate_required_columns(columns, required):
    missing = [col for col in required if col not in columns]
    return {
        "valid": len(missing) == 0,
        "missing": missing,
    }
