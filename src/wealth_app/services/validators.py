from __future__ import annotations

from typing import Iterable


def validate_required_columns(columns: Iterable[str], required: Iterable[str]) -> list[str]:
    column_set = {str(column).strip() for column in columns}
    missing = [column for column in required if column not in column_set]
    return missing


def require_columns(df, required_columns: list[str]) -> None:
    missing = validate_required_columns(df.columns, required_columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
