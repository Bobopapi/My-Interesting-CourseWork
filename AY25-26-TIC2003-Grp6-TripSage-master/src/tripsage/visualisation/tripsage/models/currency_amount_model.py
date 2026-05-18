from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class CurrencyAmount:
    currency_symbol: str
    amount: Decimal
    exchange_rate: Decimal

    def convert_exchange_rate(self, target_currency_symbol: str, target_rate: Decimal) -> CurrencyAmount:
        base_amount = self.amount / self.exchange_rate
        target_amount = base_amount * target_rate
        return CurrencyAmount(currency_symbol=target_currency_symbol, amount=target_amount, exchange_rate=target_rate)