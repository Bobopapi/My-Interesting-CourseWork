from datetime import datetime, timezone
from decimal import Decimal
import reflex as rx
import sqlalchemy
import sqlmodel
from typing import List, Optional

class Country(rx.Model, table=True):
    name: str
    code: str = sqlmodel.Field(unique=True)
    flag_assets_path: str

    regions: List["Region"] = sqlmodel.Relationship(back_populates="country")

class Region(rx.Model, table=True):
    name: str
    
    country_id: int = sqlmodel.Field(foreign_key="country.id")
    country: Optional[Country] = sqlmodel.Relationship(back_populates="regions")

class Currency(rx.Model, table=True):
    name: str
    code: str = sqlmodel.Field(unique=True)
    symbol: str
    exchange_rate: Decimal = sqlmodel.Field(
        sa_column = sqlalchemy.Column(sqlalchemy.Numeric(precision=18, scale=6))
    )

class Auth(rx.Model, table=True):
    name: str
    age: int
    gender: str
    email: str = sqlmodel.Field(unique=True)
    password: str
    created_on: datetime = sqlmodel.Field(
        default_factory=datetime.now,
        nullable=False
    )