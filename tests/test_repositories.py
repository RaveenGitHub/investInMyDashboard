import pandas as pd

from src.wealth_app.repositories.goals_repository import GoalsRepository
from src.wealth_app.repositories.portfolio_repository import PortfolioRepository
from src.wealth_app.repositories.settings_repository import SettingsRepository


def test_portfolio_repository_returns_empty_dataframe_when_data_is_missing(monkeypatch):
    repo = PortfolioRepository()
    monkeypatch.setattr("src.wealth_app.repositories.portfolio_repository.load_investments", lambda **kwargs: pd.DataFrame())

    result = repo.get_portfolio_dataframe(file_bytes=None, file_name="", search_term="", saved_view="All values")

    assert isinstance(result, pd.DataFrame)
    assert result.empty
    assert list(result.columns) == ["date", "asset_class", "instrument_name", "amount_invested", "current_value", "returns_pct", "risk_level"]


def test_portfolio_repository_filters_high_risk_view_without_crashing(monkeypatch):
    repo = PortfolioRepository()
    df = pd.DataFrame(
        [
            {"date": "2024-01-01", "asset_class": "Stocks", "instrument_name": "Alpha", "amount_invested": 100, "current_value": 120, "returns_pct": 20, "risk_level": "High"},
            {"date": "2024-01-02", "asset_class": "Crypto", "instrument_name": "Beta", "amount_invested": 200, "current_value": 130, "returns_pct": -35, "risk_level": "Medium"},
            {"date": "2024-01-03", "asset_class": "Crypto", "instrument_name": "Gamma", "amount_invested": 50, "current_value": 80, "returns_pct": 60, "risk_level": "Very High"},
        ]
    )
    monkeypatch.setattr("src.wealth_app.repositories.portfolio_repository.load_investments", lambda **kwargs: df)

    result = repo.get_portfolio_dataframe(file_bytes=None, file_name="", search_term="", saved_view="High risk")

    assert len(result) == 2
    assert set(result["instrument_name"]) == {"Alpha", "Gamma"}


def test_goals_repository_handles_missing_goal_columns_gracefully(monkeypatch):
    repo = GoalsRepository()
    monkeypatch.setattr("src.wealth_app.repositories.goals_repository.load_goals", lambda **kwargs: pd.DataFrame({"goal_name": ["Retirement"]}))

    result = repo.get_goals_dataframe(file_bytes=None, file_name="", search_term="", saved_view="All values")

    assert isinstance(result, pd.DataFrame)
    assert result.empty
    assert "progress_pct" in result.columns
    assert "remaining_amount" in result.columns


def test_goals_repository_computes_progress_safely_with_zero_target_values(monkeypatch):
    repo = GoalsRepository()
    df = pd.DataFrame(
        [
            {"goal_name": "Retirement", "category": "Retirement", "target_amount": 1000, "target_date": "2035-01-01", "current_savings": 600, "priority": "High"},
            {"goal_name": "Education", "category": "Child Education", "target_amount": 0, "target_date": "2030-01-01", "current_savings": 250, "priority": "Medium"},
        ]
    )
    monkeypatch.setattr("src.wealth_app.repositories.goals_repository.load_goals", lambda **kwargs: df)

    result = repo.get_goals_dataframe(file_bytes=None, file_name="", search_term="", saved_view="All values")

    assert result["progress_pct"].tolist() == [60.0, 0.0]
    assert result["remaining_amount"].tolist() == [400.0, -250.0]


def test_settings_repository_normalizes_invalid_values(monkeypatch):
    repo = SettingsRepository()
    storage = {"default_currency": "INR", "compact_numbers": "false"}

    def fake_get_setting(key, default=None):
        return storage.get(key, default)

    def fake_set_setting(key, value):
        storage[key] = str(value)

    monkeypatch.setattr("src.wealth_app.repositories.settings_repository.get_setting", fake_get_setting)
    monkeypatch.setattr("src.wealth_app.repositories.settings_repository.set_setting", fake_set_setting)

    assert repo.get_default_currency() == "INR"
    assert repo.get_compact_numbers_default() is False

    repo.set_default_currency(" eur ")
    repo.set_compact_numbers_default(True)

    assert repo.get_default_currency() == "EUR"
    assert repo.get_compact_numbers_default() is True

    assert repo.get_page_currency("dashboard", "GBP") == "GBP"
    assert repo.get_page_compact("dashboard", False) is False
