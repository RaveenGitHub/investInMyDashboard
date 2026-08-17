from __future__ import annotations

from database import get_setting, set_setting


class SettingsRepository:
    @staticmethod
    def _normalize_currency(currency_code: str | None, default: str = "USD") -> str:
        value = str(currency_code or default).strip().upper()
        return value if value else default

    @staticmethod
    def _normalize_bool(value, default: bool = False) -> bool:
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() == "true"

    def get_default_currency(self) -> str:
        return self._normalize_currency(get_setting("default_currency", "USD"), "USD")

    def set_default_currency(self, currency_code: str) -> None:
        set_setting("default_currency", self._normalize_currency(currency_code, "USD"))

    def get_compact_numbers_default(self) -> bool:
        return self._normalize_bool(get_setting("compact_numbers", "false"), False)

    def set_compact_numbers_default(self, enabled: bool) -> None:
        set_setting("compact_numbers", str(bool(enabled)).lower())

    def get_page_currency(self, page_name: str, default: str = "USD") -> str:
        return self._normalize_currency(get_setting(f"currency_{page_name}", default), default)

    def set_page_currency(self, page_name: str, currency: str) -> None:
        set_setting(f"currency_{page_name}", self._normalize_currency(currency, "USD"))

    def get_page_compact(self, page_name: str, default: bool = False) -> bool:
        return self._normalize_bool(get_setting(f"compact_{page_name}", str(default).lower()), default)

    def set_page_compact(self, page_name: str, enabled: bool) -> None:
        set_setting(f"compact_{page_name}", str(bool(enabled)).lower())
