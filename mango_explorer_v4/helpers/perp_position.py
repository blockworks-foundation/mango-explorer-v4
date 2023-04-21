from mango_explorer_v4.types.perp_position import PerpPosition
from mango_explorer_v4.accounts.perp_market import PerpMarket
from mango_explorer_v4.helpers.perp_market import PerpMarketHelper
from decimal import Decimal
from dataclasses import dataclass


@dataclass
class PerpPositionHelper():
    @staticmethod
    def is_active(perp_position: PerpPosition):
        return perp_position.market_index != 65535

    @staticmethod
    def equity(perp_position: PerpPosition, perp_market: PerpMarket, perp_market_oracle_price: Decimal):
        if perp_position.market_index != perp_market.perp_market_index:
            raise ValueError(f"Perp position does not belong to perp market")

        base_lots_to_quote_currency_converter = Decimal(perp_market.base_lot_size) * perp_market_oracle_price * Decimal(10 ** (6 - perp_market.base_decimals))

        base_lots = perp_position.base_position_lots + perp_position.taker_base_lots

        taker_quote = perp_position.taker_quote_lots * perp_market.quote_lot_size

        unsettled_funding = PerpPositionHelper.unsettled_funding(perp_position, perp_market)

        quote_current = perp_position.quote_position_native.to_decimal() - unsettled_funding + taker_quote

        # print(perp_market.perp_market_index, perp_market_oracle_price * Decimal(10 ** (6 - perp_market.base_decimals)), base_lots_to_quote_currency_converter, base_lots, unsettled_funding, taker_quote, quote_current)

        return (base_lots * base_lots_to_quote_currency_converter + quote_current) / Decimal(1e6)

    @staticmethod
    def unsettled_funding(perp_position: PerpPosition, perp_market: PerpMarket) -> Decimal:
        if perp_position.market_index != perp_market.perp_market_index:
            raise ValueError(f"Perp position does not belong to perp market")

        if perp_position.base_position_lots == 0:
            return Decimal(0)

        minuend, subtrahend = (
            [perp_market.long_funding, perp_position.long_settled_funding]
            if perp_position.base_position_lots > 0 else
            [perp_market.short_funding, perp_position.short_settled_funding]
        )

        multiplier = perp_position.base_position_lots

        return (minuend.to_decimal() - subtrahend.to_decimal()) * multiplier

    @staticmethod
    def unsettled_pnl(
        perp_position: PerpPosition, perp_market: PerpMarket, oracle_price: Decimal
    ) -> Decimal:
        if perp_position.market_index != perp_market.perp_market_index:
            raise ValueError(f"Perp position does not belong to perp market")

        return (
            perp_position.quote_position_native.to_decimal()
            + Decimal(PerpPositionHelper.base_position_native(perp_position, perp_market))
            * Decimal(oracle_price) * Decimal(10 ** (6 - perp_market.base_decimals))
            # ^ 6 is the number of decimals for the insurance mint TODO: change this when that does
        ) / Decimal(1e6)

    @staticmethod
    def base_position_native(
        perp_position: PerpPosition, perp_market: PerpMarket
    ) -> int:
        return perp_position.base_position_lots * perp_market.base_lot_size

    @staticmethod
    def base_position_ui(perp_position: PerpPosition, perp_market: PerpMarket, use_event_queue: bool = False):
        if perp_position.market_index != perp_market.perp_market_index:
            raise ValueError("Perp position doesn't belong to perp market")

        return PerpMarketHelper.base_lots_to_ui(
            perp_market,
            perp_position.base_position_lots + perp_position.taker_base_lots
            if use_event_queue
            else perp_position.base_position_lots
        )

    @staticmethod
    def has_open_orders(perp_position: PerpPosition):
        return any([
            value != 0
            for value in [
                perp_position.asks_base_lots,
                perp_position.bids_base_lots,
                perp_position.taker_base_lots,
                perp_position.taker_quote_lots
            ]
        ])

    @staticmethod
    def has_open_fills(perp_position: PerpPosition):
        return perp_position.taker_base_lots != 0 or perp_position.taker_quote_lots != 0

    @staticmethod
    def average_entry_price(perp_position: PerpPosition, perp_market: PerpMarket) -> Decimal:
        if perp_position.market_index != perp_market.perp_market_index:
            raise ValueError("Perp position doesn't belong to perp market")

        return (Decimal(perp_position.avg_entry_price_per_base_lot) / Decimal(perp_market.base_lot_size)) / Decimal(10 ** (6 - perp_market.base_decimals))

    @staticmethod
    def cumulative_pnl_over_position_lifetime(perp_position: PerpPosition, perp_market: PerpMarket, oracle_price: Decimal) -> Decimal:
        if perp_position.market_index != perp_market.perp_market_index:
            raise ValueError("Perp position doesn't belong to perp market")

        price_change = (oracle_price - PerpPositionHelper.average_entry_price(perp_position, perp_market)) * Decimal(10 ** (6 - perp_market.base_decimals))

        return (
            perp_position.realized_pnl_for_position_native.to_decimal() + Decimal(PerpPositionHelper.base_position_native(perp_position, perp_market)) * price_change
        ) / Decimal(1e6)



