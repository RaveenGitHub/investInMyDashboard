"""Page renderers for the app."""

from wealth_app.ui.pages.dashboard import render_dashboard_page
from wealth_app.ui.pages.goals import render_goals_dashboard
from wealth_app.ui.pages.insights import render_insights_dashboard
from wealth_app.ui.pages.portfolio import render_portfolio_page
from wealth_app.ui.pages.quality import render_quality_dashboard
from wealth_app.ui.pages.recurring import render_recurring_dashboard
from wealth_app.ui.pages.settings import render_settings_page
from wealth_app.ui.pages.transactions import render_transactions_dashboard

render_investment_dashboard = render_portfolio_page

__all__ = [
    "render_dashboard_page",
    "render_investment_dashboard",
    "render_quality_dashboard",
    "render_goals_dashboard",
    "render_transactions_dashboard",
    "render_recurring_dashboard",
    "render_insights_dashboard",
    "render_settings_page",
]
