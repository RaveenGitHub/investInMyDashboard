from __future__ import annotations

from typing import Iterable


def _normalize_column_name(column_name: str | None) -> str:
    if column_name is None:
        return ""
    normalized = str(column_name).strip().lower().replace("-", " ").replace("_", " ")
    return " ".join(normalized.split())


def validate_required_columns(columns: Iterable[str], required: Iterable[str]) -> list[str]:
    column_set = {_normalize_column_name(column) for column in columns if column is not None}
    missing = [column for column in required if _normalize_column_name(column) not in column_set]
    return missing


def require_columns(df, required_columns: list[str]) -> None:
    missing = validate_required_columns(df.columns, required_columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
