import copy
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Literal, Tuple

import pandas as pd
import reflex as rx

from . import LocaleDialogState
from ..models import DestinationItem, CurrencyAmount

DATA_DIR = Path(__file__).resolve().parents[5] / "data"
PRESENTATION_DIR = DATA_DIR / "presentation"
ANALYTICS_DIR = DATA_DIR / "analytics"
CORE_DIR = DATA_DIR / "core"


def _safe_read_parquet(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_parquet(path)
    except Exception:
        return pd.DataFrame()


def _coerce_float(value: Any, default: float = 0.0) -> float:
    if pd.isna(value):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _coerce_int(value: Any, default: int = 0) -> int:
    if pd.isna(value):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _pretty_name(name: Any, source_url: Any) -> str:
    raw_name = "" if pd.isna(name) else str(name).strip()
    if raw_name and not raw_name.startswith("http"):
        return raw_name

    raw_url = "" if pd.isna(source_url) else str(source_url).strip()
    if not raw_url:
        return "Unknown Place"

    token = raw_url.rstrip("/").split("/")[-1].replace(".html", "")
    token = token.replace("-", " ").replace("_", " ")
    token = " ".join([part for part in token.split(" ") if part])
    return token.title() if token else "Unknown Place"


def _load_base_items() -> list[DestinationItem]:
    entities = _safe_read_parquet(PRESENTATION_DIR / "viz_entities.parquet")
    reviews = _safe_read_parquet(PRESENTATION_DIR / "viz_reviews.parquet")
    attractions = _safe_read_parquet(CORE_DIR / "attractions.parquet")
    restaurants = _safe_read_parquet(CORE_DIR / "restaurants.parquet")

    if entities.empty:
        return []

    all_counts: dict[str, int] = {}
    recent_counts: dict[str, int] = {}
    if not reviews.empty and "entity_key" in reviews.columns:
        review_frame = reviews.copy()
        all_counts = review_frame.groupby("entity_key").size().to_dict()
        if "review_date" in review_frame.columns:
            review_frame["review_date"] = pd.to_datetime(review_frame["review_date"], errors="coerce")
            cutoff = pd.Timestamp.utcnow().tz_localize(None) - timedelta(days=90)
            recent = review_frame[review_frame["review_date"] >= cutoff]
            recent_counts = recent.groupby("entity_key").size().to_dict()

    attraction_keywords: dict[str, str] = {}
    if not attractions.empty and "source_url" in attractions.columns and "keywords" in attractions.columns:
        subset = attractions[["source_url", "keywords"]].dropna(subset=["source_url"])
        attraction_keywords = {
            str(row["source_url"]): str(row["keywords"]) if not pd.isna(row["keywords"]) else ""
            for _, row in subset.iterrows()
        }

    restaurant_names: dict[str, str] = {}
    if not restaurants.empty and "source_url" in restaurants.columns and "name" in restaurants.columns:
        subset = restaurants[["source_url", "name"]].dropna(subset=["source_url"])
        restaurant_names = {
            str(row["source_url"]): str(row["name"]).strip() if not pd.isna(row["name"]) else ""
            for _, row in subset.iterrows()
        }

    items: list[DestinationItem] = []
    frame = entities.fillna(value={"entity_type": "attraction", "category": ""})
    for index, row in frame.reset_index(drop=True).iterrows():
        entity_key = str(row.get("entity_key") or "")
        entity_type = str(row.get("entity_type") or "attraction").lower()
        normalized_category = "food" if entity_type == "food" else "attractions"

        total_reviews = all_counts.get(entity_key, _coerce_int(row.get("total_reviews"), 0))
        recent_reviews = recent_counts.get(entity_key, 0)
        trending_score = 0.0
        if total_reviews > 0:
            trending_score = min(5.0, (recent_reviews / total_reviews) * 5.0)

        recommendation = _coerce_float(row.get("recommendation_score"), 0.0)
        highlights_score = min(5.0, max(0.0, recommendation))

        display_name = _pretty_name(row.get("name"), row.get("source_url"))
        if entity_type == "food":
            fallback_name = restaurant_names.get(str(row.get("source_url") or entity_key), "")
            if fallback_name and not fallback_name.startswith("http"):
                display_name = fallback_name

        item = DestinationItem(
            id=index + 1,
            name=display_name,
            highlights_rating=round(highlights_score, 2),
            trending_rating=round(trending_score, 2),
            city=str(row.get("prefecture") or row.get("location_name") or "Unknown"),
            country="Japan",
            entity_type=entity_type,
            category=normalized_category,
            source_url=str(row.get("source_url") or entity_key),
            review_count=total_reviews,
            avg_rating=_coerce_float(row.get("avg_rating"), 0.0),
            keywords=attraction_keywords.get(entity_key),
            show_price=False,
        )
        items.append(item)

    return items


def _load_dashboard_payload() -> dict[str, Any]:
    entities = _safe_read_parquet(PRESENTATION_DIR / "viz_entities.parquet")
    category_summary = _safe_read_parquet(PRESENTATION_DIR / "viz_category_summary.parquet")
    monthly = _safe_read_parquet(PRESENTATION_DIR / "viz_monthly_review_activity.parquet")

    if entities.empty:
        return {
            "stats": [],
            "category_rows": [],
            "monthly_rows": [],
        }

    total_entities = len(entities)
    total_reviews = _coerce_int(entities.get("total_reviews", pd.Series(dtype=float)).fillna(0).sum(), 0)
    food_count = _coerce_int((entities.get("entity_type", pd.Series(dtype=str)) == "food").sum(), 0)
    attraction_count = _coerce_int((entities.get("entity_type", pd.Series(dtype=str)) == "attraction").sum(), 0)

    stats = [
        {"label": "Total Places", "value": str(total_entities)},
        {"label": "Total Reviews", "value": str(total_reviews)},
        {"label": "Restaurants", "value": str(food_count)},
        {"label": "Attractions", "value": str(attraction_count)},
    ]

    category_rows: list[dict[str, Any]] = []
    if not category_summary.empty:
        for _, row in category_summary.iterrows():
            category_rows.append(
                {
                    "entity_type": str(row.get("entity_type") or ""),
                    "entity_count": _coerce_int(row.get("entity_count"), 0),
                    "total_reviews": _coerce_int(row.get("total_reviews"), 0),
                    "avg_score": round(_coerce_float(row.get("avg_recommendation_score"), 0.0), 2),
                }
            )

    monthly_rows: list[dict[str, Any]] = []
    if not monthly.empty:
        ordered = monthly.sort_values("month_start", ascending=False).head(12)
        for _, row in ordered.iterrows():
            month_val = row.get("month_start")
            month_str = ""
            if not pd.isna(month_val):
                month_str = pd.to_datetime(month_val).strftime("%Y-%m")

            monthly_rows.append(
                {
                    "month": month_str,
                    "entity_type": str(row.get("entity_type") or ""),
                    "review_count": _coerce_int(row.get("review_count"), 0),
                    "avg_rating": round(_coerce_float(row.get("avg_rating"), 0.0), 2),
                }
            )

    return {
        "stats": stats,
        "category_rows": category_rows,
        "monthly_rows": monthly_rows,
    }


def _build_wordcloud(item: DestinationItem) -> list[dict[str, Any]]:
    if item.entity_type == "food":
        keywords = _safe_read_parquet(ANALYTICS_DIR / "review_keywords.parquet")
        reviews = _safe_read_parquet(PRESENTATION_DIR / "viz_reviews.parquet")
        sentiments = _safe_read_parquet(ANALYTICS_DIR / "review_sentiment.parquet")

        if (
            keywords.empty
            or reviews.empty
            or "entity_key" not in reviews.columns
            or "source_review_key" not in reviews.columns
            or "source_review_key" not in keywords.columns
            or "keyword" not in keywords.columns
        ):
            return []

        review_keys = reviews.loc[reviews["entity_key"] == item.source_url, "source_review_key"]

        review_key_list = set(review_keys.dropna().astype(str).tolist())
        if not review_key_list:
            return []

        kw = keywords[keywords["source_review_key"].astype(str).isin(review_key_list)].copy()
        if kw.empty:
            return []

        if not sentiments.empty and "source_review_key" in sentiments.columns:
            sentiment_subset = sentiments[["source_review_key", "sentiment_score"]].copy()
            kw = kw.merge(sentiment_subset, on="source_review_key", how="left")
        else:
            kw["sentiment_score"] = 0.0

        summary = (
            kw.groupby("keyword", as_index=False)
            .agg(
                frequency=("frequency", "sum"),
                sentiment=("sentiment_score", "mean"),
            )
            .sort_values("frequency", ascending=False)
            .head(30)
        )

        frequencies = summary["frequency"].astype(float).tolist()
        min_frequency = min(frequencies) if frequencies else 1.0
        max_frequency = max(frequencies) if frequencies else 1.0
        spread = max(1.0, max_frequency - min_frequency)

        output: list[dict[str, Any]] = []
        for _, row in summary.iterrows():
            frequency = _coerce_int(row.get("frequency"), 1)
            sentiment = _coerce_float(row.get("sentiment"), 0.0)

            # Build a strong visual hierarchy similar to BI wordclouds.
            norm = (float(frequency) - min_frequency) / spread
            size_px = int(14 + (norm ** 0.75) * 34)
            weight = int(380 + norm * 420)
            opacity = round(0.55 + norm * 0.45, 2)

            if sentiment > 0.25:
                color = "#2e7d32"
            elif sentiment < -0.25:
                color = "#c62828"
            else:
                color = "#455a64"

            output.append(
                {
                    "keyword": str(row.get("keyword") or ""),
                    "frequency": frequency,
                    "font_size": f"{size_px}px",
                    "font_weight": str(weight),
                    "opacity": str(opacity),
                    "color": color,
                }
            )
        return output

    keywords = (item.keywords or "").strip()
    if not keywords:
        return []

    return [
        {
            "keyword": keyword.strip(),
            "frequency": 1,
            "font_size": "16px",
            "font_weight": "500",
            "opacity": "0.75",
            "color": "#455a64",
        }
        for keyword in keywords.split(",")
        if keyword.strip()
    ]

class DestinationsState(rx.State):
    search_country: str | None = None
    search_city: str | None = None

    sort_by: Literal["highlights", "trending"] = "highlights"

    selected_category: Literal["all", "attractions", "food", "liked"] = "all"
    display_item: list[DestinationItem] = []

    liked_ids: list[int] = []
    visited_ids: list[int] = []

    selected_item_id: int | None = None
    selected_item: DestinationItem | None = None
    detail_wordcloud: list[dict[str, Any]] = []

    dashboard_stats: list[dict[str, str]] = []
    dashboard_category_rows: list[dict[str, Any]] = []
    dashboard_monthly_rows: list[dict[str, Any]] = []

    @rx.var
    def visited_items(self) -> list[DestinationItem]:
        return [
            item
            for item in self._load_items_with_user_flags()
            if item.visited
        ]

    @rx.event
    async def load_page(self):
        await self._load_display_item()

    @rx.event
    async def load_dashboard_page(self):
        payload = _load_dashboard_payload()
        self.dashboard_stats = payload["stats"]
        self.dashboard_category_rows = payload["category_rows"]
        self.dashboard_monthly_rows = payload["monthly_rows"]

    @rx.event
    async def load_detail_page(self):
        params = self.router.page.params if self.router and self.router.page else {}
        raw_item_id = params.get("item_id")
        item_id = None
        if raw_item_id is not None:
            try:
                item_id = int(raw_item_id)
            except (TypeError, ValueError):
                item_id = None

        self.selected_item_id = item_id
        await self._load_selected_item()

    @rx.event
    async def submit_search(self, form_data: dict):
        self.search_country = form_data.get("country")
        self.search_city = form_data.get("city")

        await self._load_display_item()

    @rx.event
    async def change_sort_by(self, sort: str):
        self.sort_by = sort
        await self._load_display_item()

    @rx.event
    async def change_category(self, category: str):
        self.selected_category = category
        await self._load_display_item()

    @rx.event
    async def toggle_like(self, item_id: int):
        if item_id in self.liked_ids:
            self.liked_ids = [item for item in self.liked_ids if item != item_id]
        else:
            self.liked_ids = [*self.liked_ids, item_id]

        await self._load_display_item()
        if self.selected_item_id == item_id:
            await self._load_selected_item()

    @rx.event
    async def toggle_visited(self, item_id: int):
        if item_id in self.visited_ids:
            self.visited_ids = [item for item in self.visited_ids if item != item_id]
        else:
            self.visited_ids = [*self.visited_ids, item_id]

        await self._load_display_item()
        if self.selected_item_id == item_id:
            await self._load_selected_item()

    @rx.event
    async def toggle_selected_like(self):
        if self.selected_item_id is None:
            return
        await self.toggle_like(self.selected_item_id)

    @rx.event
    async def toggle_selected_visited(self):
        if self.selected_item_id is None:
            return
        await self.toggle_visited(self.selected_item_id)

    @rx.event
    def open_detail(self, item_id: int):
        return rx.redirect(f"/details/{item_id}")

    async def _load_display_item(self):
        currency_symbol, exchange_rate = await self._get_target_locale()

        all_items = self._load_items_with_user_flags()
        if self.selected_category == "all":
            items = all_items
        elif self.selected_category == "liked":
            items = [item for item in all_items if item.liked]
        else:
            items = [item for item in all_items if item.category == self.selected_category]
        
        filtered_items = self._filter_items(items)
        sorted_items = self._sort_items(filtered_items)

        final_items = []
        for item in sorted_items:
            clone = copy.deepcopy(item)

            if clone.price is not None:
                clone.price = clone.price.convert_exchange_rate(
                    target_currency_symbol=currency_symbol,
                    target_rate=exchange_rate
                )
            final_items.append(clone)

        self.display_item = final_items

    async def _load_selected_item(self):
        if self.selected_item_id is None:
            self.selected_item = None
            self.detail_wordcloud = []
            return

        all_items = self._load_items_with_user_flags()
        matched = next((item for item in all_items if item.id == self.selected_item_id), None)
        if matched is None:
            self.selected_item = None
            self.detail_wordcloud = []
            return

        self.selected_item = matched
        self.detail_wordcloud = _build_wordcloud(matched)

    def _load_items_with_user_flags(self) -> list[DestinationItem]:
        base_items = _load_base_items()
        items: list[DestinationItem] = []
        for item in base_items:
            clone = copy.deepcopy(item)
            clone.liked = clone.id in self.liked_ids
            clone.visited = clone.id in self.visited_ids
            items.append(clone)
        return items
    
    async def _get_target_locale(self) -> Tuple[str, Decimal]:
        target_currency_symbol: str = "$"
        target_exchange_rate: Decimal = Decimal("1.0")

        locale_state = await self.get_state(LocaleDialogState)
        target_currency_symbol = locale_state.selected_currency_symbol
        target_exchange_rate = locale_state.selected_currency_exchange_rate
        
        return target_currency_symbol, target_exchange_rate
        
    def _filter_items(self, items: list[DestinationItem]) -> list[DestinationItem]:
        filtered_items = []
        
        for item in items:
            if self.search_country and self.search_country.strip():
                if self.search_country.lower() not in item.country.lower():
                    continue
            
            if self.search_city and self.search_city.strip():
                if self.search_city.lower() not in item.city.lower():
                    continue
            
            filtered_items.append(item)
            
        return filtered_items
    
    def _sort_items(self, items: list[DestinationItem]) -> list[DestinationItem]:
        if self.sort_by == "highlights":
            return sorted(
                items, 
                key=lambda x: x.highlights_rating if x.highlights_rating is not None else 0, 
                reverse=True
            )
        if self.sort_by == "trending":
            return sorted(
                items, 
                key=lambda x: x.trending_rating if x.trending_rating is not None else 0, 
                reverse=True
            )
        return items