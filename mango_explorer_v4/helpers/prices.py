import decimal

from mango_explorer_v4.types.prices import Prices
from mango_explorer_v4.types.health_type import HealthTypeKind, Maint, LiquidationEnd


class PricesHelper:
    @staticmethod
    def liab(prices: Prices, health_type: HealthTypeKind) -> decimal.Decimal:
        if health_type in [Maint, LiquidationEnd] or health_type is None:
            return prices.oracle.to_decimal()
        else:
            return max(prices.oracle.to_decimal(), prices.stable.to_decimal())

    @staticmethod
    def asset(prices: Prices, health_type: HealthTypeKind) -> decimal.Decimal:
        if health_type in [Maint, LiquidationEnd] or health_type is None:
            return prices.oracle.to_decimal()
        else:
            return min(prices.oracle.to_decimal(), prices.stable.to_decimal())
