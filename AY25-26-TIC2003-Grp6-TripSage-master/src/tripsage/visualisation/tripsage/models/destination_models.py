from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from . import CurrencyAmount

@dataclass
class DestinationItem():
    id: int
    name: str
    highlights_rating: float
    trending_rating: float
    city: str
    country: str

    entity_type: str = "attraction"
    category: str = ""
    source_url: str = ""
    review_count: int = 0
    avg_rating: float | None = None
    keywords: str | None = None
    liked: bool = False
    visited: bool = False
    price: CurrencyAmount | None = None
    show_price: bool = True
    start_date: date | None = None
    end_date: date | None = None