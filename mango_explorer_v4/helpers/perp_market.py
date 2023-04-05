from mango_explorer_v4.accounts.perp_market import PerpMarket
from mango_explorer_v4.constants import QUOTE_DECIMALS
from decimal import Decimal


class PerpMarketHelper():
    @staticmethod
    async def oracle_price(perp_market) -> Decimal:
        pass

    @staticmethod
    def price_lots_to_ui(perp_market: PerpMarket, price_lots: int):
        return float(Decimal(price_lots) * Decimal(10) ** Decimal(perp_market.base_decimals - QUOTE_DECIMALS) * Decimal(perp_market.quote_lot_size) / Decimal(perp_market.base_lot_size))

    @staticmethod
    def base_lots_to_ui(perp_market: PerpMarket, base_lots: int):
        return float(Decimal(base_lots) * (Decimal(perp_market.base_lot_size) / Decimal(10) ** Decimal(perp_market.base_decimals)))

    @staticmethod
    def quote_lots_to_ui(perp_market: PerpMarket, quote_lots: int):
        raise NotImplementedError

    @staticmethod
    def ui_price_to_lots(perp_market: PerpMarket, ui_price: float) -> int:
        return int(Decimal(ui_price * 10 ** QUOTE_DECIMALS) * Decimal(perp_market.base_lot_size) / Decimal(
            perp_market.quote_lot_size * 10 ** perp_market.base_decimals))

    @staticmethod
    def ui_base_to_lots(perp_market: PerpMarket, ui_base: float) -> int:
        return int(Decimal(ui_base * 10 ** perp_market.base_decimals) / Decimal(perp_market.base_lot_size))

    @staticmethod
    def ui_quote_to_lots(perp_market: PerpMarket, ui_quote: float) -> int:
        return int(Decimal(ui_quote * 10 ** QUOTE_DECIMALS) / Decimal(perp_market.quote_lot_size))
