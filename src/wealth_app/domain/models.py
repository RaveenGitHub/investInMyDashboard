from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from .enums import CurrencyCode, GoalStatus, RiskLevel


@dataclass(frozen=True)
class InvestmentRecord:
    date: date
    asset_class: str
    instrument_name: str
    amount_invested: float
    current_value: float
    returns_pct: float
    risk_level: RiskLevel = RiskLevel.MEDIUM
    currency: CurrencyCode = CurrencyCode.USD


@dataclass(frozen=True)
class GoalRecord:
    goal_name: str
    category: str
    target_amount: float
    target_date: date
    current_savings: float
    priority: str
    status: GoalStatus = GoalStatus.ACTIVE


@dataclass
class PortfolioSummary:
    total_invested: float
    total_value: float
    overall_return_pct: float
    health_score: float
    health_risk: str
    top_concentration: str
    top_concentration_pct: float


@dataclass
class GoalProgress:
    goal_name: str
    progress_pct: float
    remaining_amount: float
    status: str
    monthly_need: float = 0.0


@dataclass
class ImportResult:
    rows_loaded: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
