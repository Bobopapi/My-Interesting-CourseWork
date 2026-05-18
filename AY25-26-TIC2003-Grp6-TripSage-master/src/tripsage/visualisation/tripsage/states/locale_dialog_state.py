from pathlib import Path
from decimal import Decimal

import pandas as pd
import reflex as rx

from ..models import LocaleGroup, LocaleItem


DATA_DIR = Path(__file__).resolve().parents[5] / "data"
PRESENTATION_DIR = DATA_DIR / "presentation"


def _safe_read_parquet(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_parquet(path)
    except Exception:
        return pd.DataFrame()

class LocaleDialogState(rx.State):
    region_group: LocaleGroup = LocaleGroup(
        tab_value = "region",
        tab_name = "Country and region", 
        content_title = "Select a country and region")
    currency_group: LocaleGroup = LocaleGroup(
        tab_value = "currency",
        tab_name = "Currency", 
        content_title = "Select a currency")

    region_items: list[LocaleItem] = []
    currency_items: list[LocaleItem] = []

    currency_symbol_map: dict[int, str] = {
        1: "$",
        2: "S$",
        3: "¥",
    }

    currency_rate_map: dict[int, Decimal] = {
        1: Decimal("1.0"),
        2: Decimal("1.35"),
        3: Decimal("150.0"),
    }

    # Will be overwritten in load_locales.
    selected_region_item: LocaleItem | None = None
    selected_currency_item: LocaleItem | None = None

    tab_default_value: str = region_group.tab_value

    @rx.event
    def load_locales(self):
        self.region_items = self._fetch_locale_regions()
        self.currency_items = self._fetch_locale_currencies()

        if not self.region_items:
            self.region_items = [LocaleItem(id=1, name="Japan", description="All Prefectures")]

        if not self.currency_items:
            self.currency_items = [LocaleItem(id=1, name="US Dollar", description="USD - $")]

        if self.selected_region_item is None:
            self.selected_region_item = self.region_items[0]

        if self.selected_currency_item is None:
            self.selected_currency_item = self.currency_items[0]

    @rx.event
    def set_region_item(self, item: LocaleItem):
        self.selected_region_item = item
    
    @rx.event
    def set_currency_item(self, item: LocaleItem):
        self.selected_currency_item = item

        from . import DestinationsState
        yield DestinationsState.load_page
    
    @rx.var
    def get_selected_region(self) -> LocaleItem | None:
        return self.selected_region_item

    @rx.var
    def get_selected_currency(self) -> LocaleItem | None:
        return self.selected_currency_item

    @rx.var
    def selected_currency_symbol(self) -> str:
        if self.selected_currency_item is None:
            return "$"
        return self.currency_symbol_map.get(self.selected_currency_item.id, "$")

    @rx.var
    def selected_currency_exchange_rate(self) -> Decimal:
        if self.selected_currency_item is None:
            return Decimal("1.0")
        return self.currency_rate_map.get(self.selected_currency_item.id, Decimal("1.0"))

    def _fetch_locale_regions(self) -> list[LocaleItem]:
        entities = _safe_read_parquet(PRESENTATION_DIR / "viz_entities.parquet")
        if entities.empty or "prefecture" not in entities.columns:
            return []

        prefectures = (
            entities["prefecture"]
            .dropna()
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .dropna()
            .unique()
            .tolist()
        )

        prefectures = sorted(prefectures)
        return [
            LocaleItem(
                id=index + 1,
                name="Japan",
                description=prefecture,
            )
            for index, prefecture in enumerate(prefectures)
        ]

    def _fetch_locale_currencies(self) -> list[LocaleItem]:
        return [
            LocaleItem(id=1, name="US Dollar", description="USD - $"),
            LocaleItem(id=2, name="Singapore Dollar", description="SGD - S$"),
            LocaleItem(id=3, name="Japanese Yen", description="JPY - ¥"),
        ]