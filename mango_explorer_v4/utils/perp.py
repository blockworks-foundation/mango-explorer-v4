from mango_explorer_v4.types.perp_position import PerpPosition
from mango_explorer_v4.accounts.perp_market import PerpMarket
from decimal import Decimal


def is_active(perp_position: PerpPosition):
    return perp_position.market_index != 65535


def unsettled_funding(perp_position: PerpPosition, perp_market: PerpMarket) -> Decimal:
    if perp_position.market_index != perp_market.perp_market_index:
        raise ValueError(f"Perp position does not belong to perp market")

    if perp_position.base_position_lots == 0:
        return 0

    minuend, subtrahend = (
        [perp_market.long_funding, perp_position.long_settled_funding]
        if perp_position.base_position_lots > 0 else
        [perp_market.short_funding, perp_position.short_settled_funding]
    )

    multiplier = perp_position.base_position_lots

    return (minuend - subtrahend) * multiplier


def equity(perp_position: PerpPosition, perp_market: PerpMarket, perp_market_oracle_price: Decimal):
    if perp_position.market_index != perp_market.perp_market_index:
        raise ValueError(f"Perp position does not belong to perp market")

    base_lots_to_quote_currency_converter = Decimal(perp_market.base_lot_size) * perp_market_oracle_price

    base_lots = perp_position.base_position_lots + perp_position.taker_base_lots

    taker_quote = perp_position.taker_quote_lots * perp_market.quote_lot_size

    quote_current = perp_position.quote_position_native.to_decimal() - unsettled_funding(perp_position, perp_market) + taker_quote

    return base_lots * base_lots_to_quote_currency_converter + quote_current




