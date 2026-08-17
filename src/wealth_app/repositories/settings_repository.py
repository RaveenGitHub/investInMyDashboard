from __future__ import annotations

from typing import Any

from database import get_setting, set_setting


class SettingsRepository:
    def get_default_currency(self) -> str:
        return str(get_setting("default_currency", "USD"))

    def set_default_currency(self, currency_code: str) -> None:
        set_setting("default_currency", currency_code)

    def get_compact_numbers_default(self) -> bool:
        return str(get_setting("compact_numbers", "false")).lower() == "true"

    def set_compact_numbers_default(self, enabled: bool) -> None:
        set_setting("compact_numbers", str(enabled).lower())

    def get_page_currency(self, page_name: str, default: str = "USD") -> str:
        return str(get_setting(f"currency_{page_name}", default))

    def set_page_currency(self, page_name: str, currency: str) -> None:
        set_setting(f"currency_{page_name}", currency)

    def get_page_compact(self, page_name: str, default: bool = False) -> bool:
        return str(get_setting(f"compact_{page_name}", str(default).lower())).lower() == "true"

    def set_page_compact(self, page_name: str, enabled: bool) -> None:
        set_setting(f"compact_{page_name}", str(enabled).lower())
